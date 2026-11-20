import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# Colors: one per meaning, used the same way in every chart
ENROLLED = "#2a78d6"      # blue
FROZEN = "#eb6834"        # orange
REFERENCE = "#8a8984"     # gray, for "earnings alone"
CAUSE_COLORS = {"Child care": "#2a78d6", "Health coverage": "#eb6834", "SNAP": "#1baf7a"}
TEXT = "#52514e"


def dollars(x, _=None):
    """Axis label like $20k, $2.5k, or −$5k."""
    sign = "−" if x < 0 else ""
    x = abs(x)
    return f"{sign}${x/1000:g}k" if x >= 1000 else f"{sign}${x:,.0f}"


DOLLARS = FuncFormatter(dollars)


def style(ax, y_dollars=True):
    """Quiet axes so the data stands out."""
    for side in ["top", "right"]:
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_color("#c9c8c3")
    ax.spines["bottom"].set_color("#c9c8c3")
    ax.tick_params(colors=TEXT, labelsize=9)
    ax.grid(axis="y", color="#e6e5e0", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.xaxis.set_major_formatter(DOLLARS)
    if y_dollars:
        ax.yaxis.set_major_formatter(DOLLARS)


def plot_net_resources(results, cliffs, household, title, top_n=3):
    """Net resources by earnings for one household, with the biggest cliffs labeled."""
    data = results[results["household"] == household]
    fig, ax = plt.subplots(figsize=(10, 5.5))

    ax.plot(data["earnings"].unique(), data["earnings"].unique(), "--",
            color=REFERENCE, linewidth=1.2, label="Earnings alone")
    for scenario, color in [("enrolled", ENROLLED), ("frozen out", FROZEN)]:
        d = data[data["scenario"] == scenario]
        label = "Enrolled in Child Care Scholarship" if scenario == "enrolled" else "Shut out by enrollment freeze"
        ax.plot(d["earnings"], d["net_resources"], color=color, linewidth=2, label=label)

    # Label the biggest cliffs for the enrolled family
    biggest = (cliffs[(cliffs["household"] == household) & (cliffs["scenario"] == "enrolled")]
               .nlargest(top_n, "net_drop").sort_values("earnings"))
    enrolled = data[data["scenario"] == "enrolled"].set_index("earnings")
    spots = biggest["earnings"].tolist()
    for i, (_, c) in enumerate(biggest.iterrows()):
        # When two cliffs are close together, push their labels apart
        close_next = i + 1 < len(spots) and spots[i + 1] - spots[i] < 15_000
        close_prev = i > 0 and spots[i] - spots[i - 1] < 15_000
        ha, dx = ("right", -6) if close_next else ("left", 6) if close_prev else ("center", 0)
        y = enrolled.loc[c["earnings"] - 500, "net_resources"]
        ax.annotate(f"−${c['net_drop']:,.0f}\n{c['main_cause'].lower()}",
                    xy=(c["earnings"], y), xytext=(dx, 22), textcoords="offset points",
                    ha=ha, fontsize=9, color=TEXT,
                    bbox=dict(facecolor="white", edgecolor="none", pad=1.5),
                    arrowprops=dict(arrowstyle="-", color="#b4b2a9", linewidth=0.8))

    style(ax)
    ax.set_title(title, loc="left", fontsize=13, pad=14)
    ax.set_xlabel("Annual earnings", color=TEXT)
    ax.set_ylabel("Net resources per year", color=TEXT)
    ax.legend(frameon=False, fontsize=9, loc="lower right")
    fig.tight_layout()
    return fig


def plot_components(results, household, title, scenario="enrolled"):
    """Small multiples: how each program changes as earnings rise."""
    d = results[(results["household"] == household) & (results["scenario"] == scenario)].copy()
    d["tax_net"] = d["tax_credits"] - d["taxes_paid"]
    panels = [
        ("snap", "SNAP received"),
        ("childcare_paid", "Child care paid by family"),
        ("health_costs", "Health coverage costs"),
        ("tax_net", "Tax credits minus taxes"),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(10, 6), sharex=True)
    for ax, (col, panel_title) in zip(axes.flat, panels):
        ax.plot(d["earnings"], d[col], color=ENROLLED, linewidth=2)
        ax.axhline(0, color="#c9c8c3", linewidth=0.8)
        ax.set_title(panel_title, fontsize=10, color=TEXT, loc="left")
        style(ax)
    for ax in axes[1]:
        ax.set_xlabel("Annual earnings", color=TEXT)
    fig.suptitle(title, x=0.02, ha="left", fontsize=13)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    return fig


def plot_cliff_sizes(cliffs, title, scenario="enrolled", min_drop=1000):
    """Horizontal bars: every cliff over $1,000, largest first, colored by cause."""
    c = cliffs[(cliffs["scenario"] == scenario) & (cliffs["net_drop"] > min_drop)]
    c = c.sort_values("net_drop")
    labels = [f"{h.split(':')[0]} at ${e:,.0f}" for h, e in zip(c["household"], c["earnings"])]

    fig, ax = plt.subplots(figsize=(9, 0.42 * len(c) + 1.2))
    colors = [CAUSE_COLORS.get(cause, REFERENCE) for cause in c["main_cause"]]
    bars = ax.barh(labels, c["net_drop"], color=colors, height=0.65)
    for bar, value in zip(bars, c["net_drop"]):
        ax.text(bar.get_width() + 200, bar.get_y() + bar.get_height() / 2,
                f"${value:,.0f}", va="center", fontsize=9, color=TEXT)

    style(ax, y_dollars=False)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color="#e6e5e0", linewidth=0.8)
    ax.set_xlabel("Resources lost from a $500 raise", color=TEXT)
    ax.set_title(title, loc="left", fontsize=13, pad=14)
    causes = [cause for cause in CAUSE_COLORS if cause in set(c["main_cause"])]
    handles = [plt.Rectangle((0, 0), 1, 1, color=CAUSE_COLORS[cause]) for cause in causes]
    ax.legend(handles, causes, frameon=False, fontsize=9, loc="lower right", title="Cause", title_fontsize=9)
    fig.tight_layout()
    return fig
