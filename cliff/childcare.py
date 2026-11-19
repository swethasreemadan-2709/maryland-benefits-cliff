from cliff.poverty import fpl_annual


def full_price_annual(household, params):
    """What the family's child care would cost with no help, per year."""
    p = params["childcare"]
    weekly = 0
    for age in household.child_ages:
        if age <= p["preschool_max_age"]:
            weekly += p["price_weekly"]["preschool"]
        elif age <= p["school_age_max_age"]:
            weekly += p["price_weekly"]["school_age"]
    return weekly * 52


def weekly_copay(household, params, receives_snap):
    """Family's weekly copay under the new scale (simplified placeholder)."""
    c = params["childcare"]["copay"]
    income = household.annual_earnings
    poverty_line = fpl_annual(household.size, params)

    if receives_snap and c["free_if_receiving_snap"]:
        return 0
    if income <= poverty_line * c["free_at_or_below_pct_fpl"] / 100:
        return 0

    # Placeholder: rise in a straight line from the lowest to the highest copay
    # between the poverty line and the income limit. Replace with the real tiers.
    limit = params["childcare"]["initial_income_limit"][household.size]
    share = (income - poverty_line) / (limit - poverty_line)
    share = min(max(share, 0), 1)
    return c["lowest_weekly"] + share * (c["highest_weekly"] - c["lowest_weekly"])


def childcare_costs(household, params, enrolled=True, receives_snap=False, care_share=1.0):
    """Yearly child care: full price, what the family pays, and the subsidy.

    care_share is the fraction of full-time care needed (1.0 = full time).
    """
    p = params["childcare"]
    full_price = full_price_annual(household, params) * care_share
    limit = p["initial_income_limit"][household.size]

    can_get_scholarship = enrolled or not p["new_enrollment_frozen"]
    eligible = can_get_scholarship and household.annual_earnings <= limit

    if eligible:
        copay = weekly_copay(household, params, receives_snap) * 52
        cap = household.annual_earnings * p["copay"]["cap_pct_income"]
        family_pays = min(copay, cap, full_price)
    else:
        family_pays = full_price

    return {
        "eligible": eligible,
        "full_price": round(full_price, 2),
        "family_pays": round(family_pays, 2),
        "subsidy": round(full_price - family_pays, 2),
    }
