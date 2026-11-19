# Requirements: Maryland Benefits Cliff Model

## Purpose
When a low-income family earns more, they can lose public benefits faster than their pay goes up. I want to find out where that happens for typical Maryland families, how much it costs them, and which programs cause it.

## Main question
At what earnings levels do typical Maryland families hit a benefits cliff, and how big is each one?

## Who this is for
- Policy readers who want to see where cliffs fall and how big they are
- Families and caseworkers who want to see how a raise affects total resources (through the calculator)
- Hiring managers reviewing my work

## Households
| ID | Household | Children's ages |
|---|---|---|
| A | Single parent, 1 child | 3 |
| B | Single parent, 2 children | 3 and 7 |
| C | Two parents, 2 children | 3 and 7 |

All households live in Baltimore City. Earnings range from $0 to $120,000 a year, in $500 steps.

## In scope
- SNAP
- Medicaid (adults) and Medicaid/MCHP (children)
- Child Care Scholarship, for an enrolled family and for a family affected by the enrollment freeze
- Federal and Maryland EITC, federal Child Tax Credit
- Payroll tax, federal and Maryland income tax, Baltimore City local tax

## Out of scope (for now)
- Housing vouchers (long waitlists make them hard to model fairly)
- WIC, TCA, school meals, energy assistance
- Timing rules, such as when benefits are recertified
- Savings and asset limits

## Key assumptions
- All income is wages; no child support or other income.
- The 3-year-old is in full-time center care; the 7-year-old needs before and after school care.
- Lost Medicaid is valued at what replacement coverage would cost. Since this is a judgment call, results are shown with and without it.
- All rules are as of November 2026.
- Single parents file as head of household; two-parent families file jointly.
- The Maryland EITC is modeled as the refundable 45% credit. Local EITCs are not modeled.
- The parent earns Maryland's $15 minimum wage; child care need grows with hours worked, up to full time at $31,200 a year.
- Losing public coverage is valued at the average worker contribution to employer insurance ($1,440 for one person, $6,850 for two or more, KFF 2025). This assumes the job offers coverage.
- When SNAP and child care affect each other, the model first checks whether the family qualifies for SNAP with the copay waived; if not, the family pays the copay.

## Outputs
1. Net resources for each household at each earnings level
2. Marginal effective tax rate at each level, with every rate over 100% flagged as a cliff
3. Charts showing benefits switching off as earnings rise
4. An interactive calculator
5. A short policy memo

## Success criteria
- Every rule and number traces back to an official source in params/maryland_2026.yaml
- Each program has tests that check results just below and just above its limits
- Results are in the same range as the Atlanta Fed CLIFF tool for a similar family
- Someone with no background can find the biggest cliff on the chart in 10 seconds

## Risks
- Real rules have more detail than this model. I state "simplified" plainly and list what's left out.
- Rules change every year. All numbers live in one parameters file, so they're easy to update.

*Personal project using only publicly available rules. Not affiliated with or endorsed by any Maryland state agency.*

## Open questions and how I handled them

| Question | What I found | What the model assumes |
|---|---|---|
| What is the current child care income limit? | The MSDE income scale page still shows 2022 limits ($90,033 for a family of 4). News coverage of the 2026 copay changes gives $111,936 for a family of 4. | $111,936 for a family of 4. Limits for other family sizes are estimated using the same size ratios as the old scale (68% for 2 people, 84% for 3). |
| Which copay rules apply? | The State Board approved new copays in August 2026 ($10.58 to $106.74 a week), starting no earlier than January 2027. Families pay about $1 to $3 a week today. | The new copay model, since it reflects where the program is heading. The current copays can be added as a comparison scenario. |
| What are the copay limits for continuing families? | Not published with the new numbers. | Not modeled yet; listed as a limitation. |
| What share of the federal EITC does Maryland give? | Refundable credit of 45% for families with children, or a nonrefundable 50%, not both. | The refundable 45%. |
| Do families on SNAP pay a child care copay? | No. Families receiving SNAP pay no copay under the new model. | Losing SNAP also starts a child care copay. The model checks for this combined effect. |
| What is the SNAP maximum benefit? | Maryland's SNAP income guidelines PDF lists $773 for a family of 3, but USDA's official FY2027 table and Maryland's SNAP standards manual both give $808. | USDA's figures, since USDA sets SNAP benefit amounts. |
| What are the new child care copay tiers? | The approved scale runs from $10.58 to $106.74 a week, capped at 7% of income, but I haven't yet recorded each tier from the State Board document. | A placeholder that rises in a straight line between those amounts. To be replaced with the real tiers. |
| What are the current MCHP premiums? | The most recent official chart I found (2017) shows $54 and $67 a month per family. | Those amounts, labeled approximate. |
| Do the EITC results match the IRS lookup table? | The IRS publishes the 2026 EITC table in early 2027. The model's phase-in and phase-out rates, worked out from the 2026 IRS parameters, match the official rates (34% and 15.98% for one child). | The formula, using official 2026 parameters. Recheck against the IRS table when it is published. |