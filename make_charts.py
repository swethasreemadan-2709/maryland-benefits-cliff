"""Build the charts from data/results.csv and save them to charts."""
from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg")  # save image files without opening windows

from cliff.charts import plot_cliff_sizes, plot_components, plot_net_resources

results = pd.read_csv("data/results.csv")
cliffs = pd.read_csv("data/cliffs.csv")
Path("charts").mkdir(exist_ok=True)

titles = {
	"A: single parent, 1 child": "a_single_parent_1_child",
	"B: single parent, 2 children": "b_single_parent_2_children",
	"C: two parents, 2 children": "c_two_parents_2_children",
}

for household, slug in titles.items():
	fig = plot_net_resources(
		results,
		cliffs,
		household,
		title=f"{household}: a raise can leave the family with less",
	)
	fig.savefig(f"charts/net_resources_{slug}.png", dpi=150, bbox_inches="tight")

	fig = plot_components(
		results,
		household,
		title=f"{household}: what changes as earnings rise",
	)
	fig.savefig(f"charts/components_{slug}.png", dpi=150, bbox_inches="tight")

fig = plot_cliff_sizes(
	cliffs, title="Losing the child care scholarship causes the largest cliffs"
)
fig.savefig("charts/cliff_sizes.png", dpi=150, bbox_inches="tight")

print("Saved charts to charts/")