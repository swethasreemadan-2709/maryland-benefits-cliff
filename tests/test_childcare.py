import pytest
from cliff.household import Household
from cliff.params import load_params
from cliff.childcare import childcare_costs

PARAMS = load_params()
FULL_PRICE = 302.22 * 52   # one preschooler, about $15,715 a year


def single_parent(annual_earnings):
	return Household(adults=1, child_ages=[3], annual_earnings=annual_earnings)


def test_free_below_poverty_line():
	assert childcare_costs(single_parent(20_000), PARAMS)["family_pays"] == 0


def test_free_when_receiving_snap():
	result = childcare_costs(single_parent(35_000), PARAMS, receives_snap=True)
	assert result["family_pays"] == 0


def test_copay_in_the_middle():
	# Placeholder copay at $40,000: about $43 a week, about $2,235 a year
	result = childcare_costs(single_parent(40_000), PARAMS)
	assert result["family_pays"] == pytest.approx(2235.5, abs=1)


def test_cliff_above_income_limit():
	# Limit for 2 people: $76,116. Above it, the family pays full price.
	result = childcare_costs(single_parent(80_000), PARAMS)
	assert result["eligible"] is False
	assert result["family_pays"] == pytest.approx(FULL_PRICE, abs=1)


def test_frozen_out_family_pays_full_price():
	result = childcare_costs(single_parent(40_000), PARAMS, enrolled=False)
	assert result["family_pays"] == pytest.approx(FULL_PRICE, abs=1)
