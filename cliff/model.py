from dataclasses import replace

import pandas as pd

from cliff.childcare import childcare_costs
from cliff.household import Household
from cliff.medicaid import medicaid_status
from cliff.snap import snap_benefit
from cliff.taxes import all_taxes


def care_share(household, params):
	"""Share of full-time child care needed, based on hours worked at minimum wage."""
	w = params["work"]
	full_time_earnings = w["wage_hourly"] * w["full_time_hours_per_year"]
	return min(household.annual_earnings / full_time_earnings, 1.0)


def snap_and_childcare(household, params, enrolled):
	"""SNAP and child care depend on each other, so work them out together.

	- Child care costs raise SNAP (dependent care deduction).
	- Families on SNAP pay no child care copay.
	We first check whether the family gets SNAP with the copay waived. If not,
	they pay the copay, and SNAP is recalculated with that cost deducted.
	"""
	share = care_share(household, params)

	care_on = childcare_costs(household, params, enrolled, receives_snap=True, care_share=share)
	snap_on = snap_benefit(replace(household, childcare_paid_monthly=care_on["family_pays"] / 12), params)
	if snap_on > 0:
		return snap_on * 12, care_on

	care_off = childcare_costs(household, params, enrolled, receives_snap=False, care_share=share)
	snap_off = snap_benefit(replace(household, childcare_paid_monthly=care_off["family_pays"] / 12), params)
	return snap_off * 12, care_off


def health_costs(household, params):
	"""Yearly cost of health coverage the family has to buy, plus MCHP premiums."""
	h = params["health"]
	status = medicaid_status(household, params)
	uncovered = (household.adults - status["adults_covered"]) + status["children"].count(None)
	if uncovered == 0:
		replacement = 0
	elif uncovered == 1:
		replacement = h["worker_contribution_single"]
	else:
		replacement = h["worker_contribution_family"]
	return replacement + status["premium_annual"], status


def net_resources(household, params, enrolled=True):
	"""Everything for one family at one earnings level, as a dictionary of yearly amounts."""
	snap, care = snap_and_childcare(household, params, enrolled)
	health, status = health_costs(household, params)
	taxes = all_taxes(household, params)

	before_health = household.annual_earnings + snap + taxes["net"] - care["family_pays"]
	return {
		"earnings": household.annual_earnings,
		"snap": snap,
		"childcare_paid": care["family_pays"],
		"childcare_subsidy": care["subsidy"],
		"health_costs": health,
		"adults_on_medicaid": status["adults_covered"],
		"children_coverage": ", ".join(str(c) for c in status["children"]),
		"taxes_paid": taxes["taxes_paid"],
		"tax_credits": taxes["credits_received"],
		"net_resources": round(before_health - health, 2),
		"net_resources_no_health": round(before_health, 2),
	}


HOUSEHOLDS = {
	"A: single parent, 1 child": dict(adults=1, child_ages=[3]),
	"B: single parent, 2 children": dict(adults=1, child_ages=[3, 7]),
	"C: two parents, 2 children": dict(adults=2, child_ages=[3, 7]),
}


def run_all(params, max_earnings=120_000, step=500):
	"""Net resources for every household, earnings level, and child care scenario."""
	rows = []
	for name, setup in HOUSEHOLDS.items():
		for enrolled in [True, False]:
			for earnings in range(0, max_earnings + 1, step):
				family = Household(**setup, annual_earnings=earnings,
								   rent_monthly=params["housing"]["rent_monthly"])
				row = net_resources(family, params, enrolled)
				row["household"] = name
				row["scenario"] = "enrolled" if enrolled else "frozen out"
				rows.append(row)

	df = pd.DataFrame(rows)
	df = add_metr(df)
	return df


def add_metr(df):
	"""Marginal effective tax rate: share of each extra dollar the family loses."""
	df = df.sort_values(["household", "scenario", "earnings"]).copy()
	groups = df.groupby(["household", "scenario"])
	change_net = groups["net_resources"].diff()
	change_earnings = groups["earnings"].diff()
	df["metr"] = (1 - change_net / change_earnings).round(3)
	df["is_cliff"] = df["metr"] > 1
	return df


def find_cliffs(df):
	"""Every step where earning $500 more leaves the family with less."""
	df = df.sort_values(["household", "scenario", "earnings"])
	cols = ["snap", "childcare_paid", "health_costs", "taxes_paid", "tax_credits"]
	changes = df.groupby(["household", "scenario"])[cols].diff()
	# Effect on the family: more SNAP or credits helps; more costs or taxes hurts
	effect = pd.DataFrame({
		"SNAP": changes["snap"],
		"Child care": -changes["childcare_paid"],
		"Health coverage": -changes["health_costs"],
		"Taxes": -changes["taxes_paid"],
		"Tax credits": changes["tax_credits"],
	}).fillna(0)
	df = df.assign(
		net_drop=-df.groupby(["household", "scenario"])["net_resources"].diff(),
		main_cause=effect.idxmin(axis=1),
	)
	cliffs = df[df["is_cliff"]]
	return cliffs[["household", "scenario", "earnings", "net_drop", "main_cause"]]
