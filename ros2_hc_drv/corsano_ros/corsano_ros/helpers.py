from logging import error, info, warning
from pathlib import Path
import re
import time
import yaml

def load_config(config_path):
    """Load YAML config file if provided."""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, "r") as f:
        return yaml.safe_load(f)


def is_mac_address(s: str) -> bool:
    """Return True if string looks like a Bluetooth MAC address."""
    return bool(re.match(r"^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$", s))
