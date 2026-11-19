import pytest

from cliff.household import Household
from cliff.params import load_params
from cliff.taxes import all_taxes, bracket_tax, federal_eitc


PARAMS = load_params()


def single_parent(annual_earnings):
	return Household(adults=1, child_ages=[3], annual_earnings=annual_earnings)


def test_bracket_tax_simple():
	# $3,000 of Maryland taxable income: 2% + 3% + 4% of $1,000 each = $90
	brackets = PARAMS["maryland_tax"]["brackets_joint_or_head_of_household"]
	assert bracket_tax(3_000, brackets) == pytest.approx(90)


def test_payroll_tax():
	assert all_taxes(single_parent(30_000), PARAMS)["fica"] == 2295


def test_ctc_wipes_out_federal_income_tax_at_30000():
	# Taxable $5,850 -> tax $585, fully covered by the $2,200 credit
	result = all_taxes(single_parent(30_000), PARAMS)
	assert result["income_tax"] == 0
	assert result["ctc_refundable"] == 1615  # $2,200 - $585


def test_eitc_plateau():
	# Between $13,020 and $23,890, one child: the maximum $4,427
	assert federal_eitc(single_parent(15_000), PARAMS) == pytest.approx(4427)


def test_eitc_phasing_out():
	# $4,427 - 15.98% x ($30,000 - $23,890) = about $3,451
	assert federal_eitc(single_parent(30_000), PARAMS) == pytest.approx(3451, abs=1)


def test_eitc_gone_above_phaseout_end():
	assert federal_eitc(single_parent(52_000), PARAMS) == 0


def test_maryland_and_local_tax_at_30000():
	# Taxable: $30,000 - $6,700 - 2 x $3,200 = $16,900
	result = all_taxes(single_parent(30_000), PARAMS)
	assert result["state_tax"] == pytest.approx(750.25)
	assert result["local_tax"] == pytest.approx(540.80)


def test_two_parents_file_jointly():
	couple = Household(adults=2, child_ages=[3, 7], annual_earnings=40_000)
	# Taxable $40,000 - $32,200 = $7,800 -> $780, covered by $4,400 of credit
	assert all_taxes(couple, PARAMS)["income_tax"] == 0
