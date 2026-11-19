import pytest
from cliff.household import Household
from cliff.params import load_params
from cliff.model import net_resources, run_all, find_cliffs

PARAMS = load_params()
RENT = PARAMS["housing"]["rent_monthly"]


def single_parent(annual_earnings):
	return Household(adults=1, child_ages=[3], annual_earnings=annual_earnings, rent_monthly=RENT)


def test_net_resources_adds_up():
	r = net_resources(single_parent(30_000), PARAMS)
	expected = (r["earnings"] + r["snap"] + r["tax_credits"] - r["taxes_paid"]
				- r["childcare_paid"] - r["health_costs"])
	assert r["net_resources"] == pytest.approx(expected, abs=0.05)


def test_snap_family_pays_no_copay():
	# At $40,000 the family still gets SNAP, so the child care copay is waived
	r = net_resources(single_parent(40_000), PARAMS)
	assert r["snap"] > 0
	assert r["childcare_paid"] == 0


def test_frozen_out_family_is_worse_off():
	enrolled = net_resources(single_parent(40_000), PARAMS, enrolled=True)
	frozen = net_resources(single_parent(40_000), PARAMS, enrolled=False)
	assert frozen["net_resources"] < enrolled["net_resources"] - 10_000


def test_child_care_cliff_for_household_a():
	# Crossing the $76,116 income limit costs the family more than the $500 raise
	before = net_resources(single_parent(76_000), PARAMS)
	after = net_resources(single_parent(76_500), PARAMS)
	assert after["net_resources"] < before["net_resources"] - 9_000


def test_find_cliffs_reports_the_child_care_cliff():
	cliffs = find_cliffs(run_all(PARAMS))
	a = cliffs[(cliffs["household"].str.startswith("A")) & (cliffs["scenario"] == "enrolled")]
	assert 76_500 in a["earnings"].values
