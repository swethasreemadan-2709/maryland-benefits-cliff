from cliff.poverty import pct_fpl


def child_coverage(age, income_pct, params):
	"""Which program covers a child: 'Medicaid', 'MCHP', 'MCHP Premium', or None."""
	p = params["medicaid"]
	limits = p["child_medicaid_limit_pct_fpl"]
	if age < 1:
		medicaid_limit = limits["under_1"]
	elif age <= 5:
		medicaid_limit = limits["age_1_to_5"]
	else:
		medicaid_limit = limits["age_6_to_18"]

	if income_pct <= medicaid_limit:
		return "Medicaid"
	if income_pct <= p["mchp_free_limit_pct_fpl"]:
		return "MCHP"
	if income_pct <= p["mchp_premium_limit_pct_fpl"]:
		return "MCHP Premium"
	return None


def medicaid_status(household, params):
	"""Who in the family has public health coverage, and the yearly premium owed."""
	p = params["medicaid"]
	income_pct = pct_fpl(household, params)

	adults_covered = household.adults if income_pct <= p["adult_limit_pct_fpl"] else 0
	children = [child_coverage(age, income_pct, params) for age in household.child_ages]

	# MCHP Premium is charged once per family, not per child
	premium_monthly = 0
	if "MCHP Premium" in children:
		for upper_limit, amount in p["mchp_premium_monthly"]:
			if income_pct <= upper_limit:
				premium_monthly = amount
				break

	return {
		"income_pct_fpl": round(income_pct, 1),
		"adults_covered": adults_covered,
		"children": children,
		"premium_annual": premium_monthly * 12,
	}
