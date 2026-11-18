import math


def snap_benefit(household, params):
	"""Monthly SNAP benefit for a household, in dollars."""
	p = params["snap"]
	size = household.size
	gross = household.monthly_earnings

	# Step 1: gross income test (Maryland: 200% of the poverty line)
	if gross > p["gross_limit_monthly"][size]:
		return 0

	# Step 2: subtract deductions to get adjusted income
	earned_deduction = gross * p["earned_income_deduction"]
	adjusted = gross - earned_deduction - p["standard_deduction"][size] - household.childcare_paid_monthly
	adjusted = max(adjusted, 0)

	# Step 3: shelter deduction (housing costs above half of adjusted income, capped)
	shelter_costs = household.rent_monthly + p["standard_utility_allowance"]
	excess_shelter = max(shelter_costs - adjusted / 2, 0)
	excess_shelter = min(excess_shelter, p["max_excess_shelter"])

	# Step 4: net income
	net = max(adjusted - excess_shelter, 0)

	# Step 5: benefit = maximum allotment minus 30% of net income
	benefit = p["max_benefit"][size] - math.ceil(net * p["benefit_reduction_rate"])

	# Step 6: small households get a minimum benefit
	if size <= p["min_benefit_max_size"]:
		benefit = max(benefit, p["min_benefit"])

	return max(benefit, 0)
