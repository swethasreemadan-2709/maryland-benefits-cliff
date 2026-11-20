"""Maryland Benefits Cliff Calculator (Streamlit app)."""
import plotly.graph_objects as go
import streamlit as st

from cliff.model import HOUSEHOLDS, find_cliffs, run_all
from cliff.params import load_params

st.set_page_config(page_title="Maryland Benefits Cliff Calculator", layout="wide")


@st.cache_data
def load_results():
    """Run the model once and reuse the results while the app is open."""
    params = load_params()
    results = run_all(params)
    return results, find_cliffs(results)


results, cliffs = load_results()

# ---------- Controls ----------
st.sidebar.header("Choose a family")
household = st.sidebar.selectbox("Family", list(HOUSEHOLDS))
scenario = st.sidebar.radio(
    "Child Care Scholarship",
    ["enrolled", "frozen out"],
    format_func=lambda s: "Already enrolled" if s == "enrolled" else "Shut out by the enrollment freeze",
)
include_health = st.sidebar.checkbox("Count the cost of replacing lost health coverage", value=True)
earnings = st.sidebar.slider("Annual earnings", 0, 120_000, 40_000, step=500, format="$%d")

column = "net_resources" if include_health else "net_resources_no_health"
data = results[(results["household"] == household) & (results["scenario"] == scenario)]
data = data.set_index("earnings")
row = data.loc[earnings]

# ---------- Headline numbers ----------
st.title("Maryland Benefits Cliff Calculator")
st.write("See how a family's total resources change as earnings rise, and where a raise "
         "can leave them with less.")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Net resources per year", f"${row[column]:,.0f}")
col2.metric("SNAP per year", f"${row['snap']:,.0f}")
col3.metric("Child care paid per year", f"${row['childcare_paid']:,.0f}")
col4.metric("Health coverage costs per year", f"${row['health_costs']:,.0f}" if include_health else "Not counted")

# ---------- What would a raise do? ----------
raise_to = min(earnings + 5_000, 120_000)
change = data.loc[raise_to, column] - row[column]
if raise_to > earnings:
    message = (f"A raise to **${raise_to:,}** (+${raise_to - earnings:,}) changes net resources "
               f"by **{'+' if change >= 0 else '−'}${abs(change):,.0f}**.")
    if change < 0:
        st.error(message + " The family would be worse off.")
    elif change < (raise_to - earnings) * 0.5:
        st.warning(message + " The family keeps less than half of the raise.")
    else:
        st.success(message)

# Next cliff above the current earnings
drops = data[column].diff()
ahead = drops[(drops.index > earnings) & (drops < 0)]
if len(ahead) > 0:
    at = int(ahead.index[0])
    match = cliffs[(cliffs["household"] == household) & (cliffs["scenario"] == scenario)
                   & (cliffs["earnings"] == at)]
    cause = f" ({match['main_cause'].iloc[0].lower()})" if len(match) > 0 else ""
    st.info(f"Next cliff: at **${at:,}**, net resources drop by **${-ahead.iloc[0]:,.0f}**{cause}.")
else:
    st.info("No cliffs above this earnings level.")

# ---------- Chart ----------
color = "#2a78d6" if scenario == "enrolled" else "#eb6834"
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=data.index, y=data.index, name="Earnings alone",
    line=dict(color="#8a8984", dash="dash", width=1.5),
    hovertemplate="Earnings alone: $%{y:,.0f}<extra></extra>",
))
fig.add_trace(go.Scatter(
    x=data.index, y=data[column], name="Net resources",
    line=dict(color=color, width=2.5),
    hovertemplate="Earnings $%{x:,.0f}<br>Net resources $%{y:,.0f}<extra></extra>",
))
fig.add_trace(go.Scatter(
    x=[earnings], y=[row[column]], name="Selected", mode="markers",
    marker=dict(color=color, size=12, line=dict(color="white", width=2)),
    hoverinfo="skip", showlegend=False,
))
fig.update_layout(
    title=f"{household}: net resources by earnings",
    xaxis_title="Annual earnings", yaxis_title="Net resources per year",
    xaxis_tickprefix="$", yaxis_tickprefix="$", xaxis_tickformat=",", yaxis_tickformat=",",
    hovermode="x unified", height=480, margin=dict(t=60, l=10, r=10, b=10),
    legend=dict(orientation="h", y=-0.2),
)
st.plotly_chart(fig)

# ---------- Breakdown ----------
st.subheader(f"Where the money comes from at ${earnings:,}")
breakdown = [
    ("Earnings", earnings),
    ("SNAP", row["snap"]),
    ("Tax credits (EITC, Child Tax Credit)", row["tax_credits"]),
    ("Taxes paid", -row["taxes_paid"]),
    ("Child care paid by family", -row["childcare_paid"]),
]
if include_health:
    breakdown.append(("Health coverage costs", -row["health_costs"]))
breakdown.append(("Net resources", row[column]))
st.table({"Item": [b[0] for b in breakdown],
          "Per year": [f"{'−' if v < 0 else ''}${abs(v):,.0f}" for _, v in breakdown]})

st.caption(
    f"Parent's health coverage: {'Medicaid' if row['adults_on_medicaid'] else 'not covered by Medicaid'}. "
    f"Children: {row['children_coverage'].replace('None', 'no public coverage')}."
)

# ---------- About ----------
with st.expander("Assumptions and sources"):
    st.markdown("""
- Rules as of November 2026, Baltimore City. Simplified: real eligibility has more detail.
- Programs: SNAP, Medicaid/MCHP, Child Care Scholarship (new copay scale, approved for 2027),
  federal and Maryland EITC, Child Tax Credit, payroll, federal, state, and local taxes.
- The parent earns Maryland's $15 minimum wage; child care need grows with hours worked.
- Lost health coverage is valued at the average worker contribution to employer insurance (KFF 2025).
- Child care copays use a placeholder between the published lowest and highest amounts.
- Every number and its source: `params/maryland_2026.yaml` in the GitHub repo.
""")

st.caption("Personal project using only publicly available rules. Not affiliated with or endorsed "
           "by any Maryland state agency. Not financial or benefits advice.")
