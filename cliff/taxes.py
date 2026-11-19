def bracket_tax(taxable_income, brackets):
	"""Tax owed using a list of [income above, rate] brackets."""
	tax = 0
	for i, (start, rate) in enumerate(brackets):
		end = brackets[i + 1][0] if i + 1 < len(brackets) else float("inf")
		if taxable_income > start:
			tax += (min(taxable_income, end) - start) * rate
	return tax


def federal_eitc(household, params):
	"""Federal Earned Income Tax Credit for the year."""
	e = params["federal_tax"]["eitc"]
	earnings = household.annual_earnings
	kids = min(len(household.child_ages), e["max_children_counted"])
	if kids == 0:
		return 0  # childless EITC not modeled

	joint = household.adults == 2
	max_credit = e["max_credit"][kids]
	start = e["phaseout_start_joint"] if joint else e["phaseout_start_single"]
	end = (e["phaseout_end_joint"] if joint else e["phaseout_end_single"])[kids]

	# Rates come from the IRS table itself, so no extra numbers are needed
	phase_in_rate = max_credit / e["phase_in_end"][kids]
	phaseout_rate = max_credit / (end - start)

	credit = min(earnings * phase_in_rate, max_credit)
	if earnings > start:
		credit = min(credit, max(max_credit - phaseout_rate * (earnings - start), 0))
	return credit


def federal_taxes(household, params):
	"""Federal income tax and Child Tax Credit for the year."""
	f = params["federal_tax"]
	earnings = household.annual_earnings
	joint = household.adults == 2

	deduction = f["standard_deduction"]["married_joint" if joint else "head_of_household"]
	brackets = f["brackets_married_joint"] if joint else f["brackets_head_of_household"]
	tax_before_credits = bracket_tax(max(earnings - deduction, 0), brackets)

	# Child Tax Credit: first reduces tax owed, the rest may be paid out (refundable)
	kids = sum(1 for age in household.child_ages if age <= f["ctc_max_child_age"])
	ctc_total = kids * f["child_tax_credit_per_child"]
	ctc_used_against_tax = min(ctc_total, tax_before_credits)
	refundable_limit = min(
		kids * f["ctc_refundable_max_per_child"],
		max(earnings - f["ctc_refundable_earnings_floor"], 0) * f["ctc_refundable_rate"],
	)
	ctc_refundable = min(ctc_total - ctc_used_against_tax, refundable_limit)

	return {
		"income_tax": tax_before_credits - ctc_used_against_tax,
		"ctc_refundable": ctc_refundable,
		"eitc": federal_eitc(household, params),
	}


def maryland_taxes(household, params, federal_eitc_amount):
	"""Maryland state tax, Baltimore City local tax, and Maryland EITC."""
	m = params["maryland_tax"]
	earnings = household.annual_earnings
	deduction = m["standard_deduction"]["joint_or_head_of_household"]
	exemptions = m["personal_exemption"] * household.size
	taxable = max(earnings - deduction - exemptions, 0)

	return {
		"state_tax": bracket_tax(taxable, m["brackets_joint_or_head_of_household"]),
		"local_tax": taxable * m["local_rate_baltimore_city"],
		"md_eitc": federal_eitc_amount * m["eitc_pct_of_federal"],
	}


def all_taxes(household, params):
	"""Every tax and credit, plus the net effect on the family (positive = family gains)."""
	fica = household.annual_earnings * params["federal_tax"]["fica_rate"]
	fed = federal_taxes(household, params)
	md = maryland_taxes(household, params, fed["eitc"])

	taxes_paid = fica + fed["income_tax"] + md["state_tax"] + md["local_tax"]
	credits_received = fed["eitc"] + fed["ctc_refundable"] + md["md_eitc"]

	result = {"fica": fica, **fed, **md,
			  "taxes_paid": taxes_paid,
			  "credits_received": credits_received,
			  "net": credits_received - taxes_paid}
	return {k: round(v, 2) for k, v in result.items()}
