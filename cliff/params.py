from pathlib import Path
import yaml

PARAMS_PATH = Path(__file__).parent.parent / "params" / "maryland_2026.yaml"


def load_params(path=PARAMS_PATH):
	"""Read the parameters file and return it as a dictionary."""
	with open(path) as f:
		return yaml.safe_load(f)
