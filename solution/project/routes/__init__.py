import importlib
from pathlib import Path

current_dir = Path(__file__).parent

for module in sorted(current_dir.glob("*.py")):
    if module.stem != "__init__":
        importlib.import_module(f".{module.stem}", __package__)
