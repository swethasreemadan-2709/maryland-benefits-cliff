from cliff.household import Household
from cliff.params import load_params
from cliff.snap import snap_benefit

PARAMS = load_params()


def single_parent(annual_earnings):
	"""Household A: one adult, one 3-year-old, Baltimore rent."""
	return Household(adults=1, child_ages=[3], annual_earnings=annual_earnings,
					 rent_monthly=PARAMS["housing"]["rent_monthly"])


def test_no_earnings_gets_maximum():
	assert snap_benefit(single_parent(0), PARAMS) == 562


def test_partial_benefit_at_24000():
	# Worked by hand: gross 2000, adjusted 1383, shelter capped at 769,
	# net 614, 30% = 184.2 -> 185, benefit 562 - 185 = 377
	assert snap_benefit(single_parent(24_000), PARAMS) == 377


def test_minimum_benefit_right_at_the_limit():
	# $3,607 a month is exactly the gross limit for 2 people
	assert snap_benefit(single_parent(3_607 * 12), PARAMS) == 25


def test_cliff_just_over_the_limit():
	# One dollar a month over the limit: no SNAP at all
	assert snap_benefit(single_parent(3_608 * 12), PARAMS) == 0


def test_childcare_costs_raise_the_benefit():
	without = snap_benefit(single_parent(24_000), PARAMS)
	hh = single_parent(24_000)
	hh.childcare_paid_monthly = 300
	assert snap_benefit(hh, PARAMS) > without
