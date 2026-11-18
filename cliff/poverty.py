def fpl_annual(size, params):
    """Federal poverty line for a household of this size, per year."""
    p = params["fpl"]
    return p["first_person"] + p["each_additional_person"] * (size - 1)


def pct_fpl(household, params):
    """Household earnings as a percent of the poverty line (150 means 150%)."""
    return household.annual_earnings / fpl_annual(household.size, params) * 100
