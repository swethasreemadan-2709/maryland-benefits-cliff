from cliff.household import Household
from cliff.params import load_params
from cliff.medicaid import medicaid_status

PARAMS = load_params()


def single_parent(annual_earnings):
	# Household A. Poverty line for 2 people: $21,640
	return Household(adults=1, child_ages=[3], annual_earnings=annual_earnings)


def test_parent_covered_below_138_percent():
	# 138% of $21,640 = $29,863
	assert medicaid_status(single_parent(29_000), PARAMS)["adults_covered"] == 1


def test_parent_loses_coverage_above_138_percent():
	status = medicaid_status(single_parent(30_000), PARAMS)
	assert status["adults_covered"] == 0
	assert status["children"] == ["Medicaid"]   # child still covered (limit 143%)


def test_child_moves_to_mchp():
	assert medicaid_status(single_parent(40_000), PARAMS)["children"] == ["MCHP"]


def test_lower_premium_band():
	status = medicaid_status(single_parent(50_000), PARAMS)
	assert status["children"] == ["MCHP Premium"]
	assert status["premium_annual"] == 54 * 12


def test_higher_premium_band():
	assert medicaid_status(single_parent(60_000), PARAMS)["premium_annual"] == 67 * 12


def test_no_coverage_above_322_percent():
	# 322% of $21,640 = $69,681
	status = medicaid_status(single_parent(70_000), PARAMS)
	assert status["children"] == [None]
	assert status["premium_annual"] == 0
