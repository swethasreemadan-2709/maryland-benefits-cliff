"""Run the full model and save the results to data/results.csv."""
from pathlib import Path

from cliff.model import find_cliffs, run_all
from cliff.params import load_params

params = load_params()
results = run_all(params)
cliffs = find_cliffs(results)

Path("data").mkdir(exist_ok=True)
results.to_csv("data/results.csv", index=False)
cliffs.to_csv("data/cliffs.csv", index=False)

print(f"Saved {len(results)} rows to data/results.csv")
print(f"Found {len(cliffs)} cliff points; saved to data/cliffs.csv")
