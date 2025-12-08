from logging import error, info
from pathlib import Path
import re
import yaml


def load_config(config_path: str) -> dict:
    """Load YAML configuration from a file.

    Args:
        config_path: Path to YAML config file.

    Returns:
        Parsed configuration as a dictionary.

    Raises:
        FileNotFoundError: If the file does not exist.
        yaml.YAMLError: If YAML parsing fails.
    """
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    try:
        with open(path, "r") as f:
            cfg = yaml.safe_load(f)
            info(f"Config loaded from {path}")
            return cfg
    except yaml.YAMLError as e:
        error(f"Failed to parse YAML config: {e}")
        raise


def is_mac_address(s: str) -> bool:
    """Check if a string is a valid Bluetooth MAC address.

    Args:
        s: Input string.

    Returns:
        True if string matches MAC address format, else False.
    """
    return bool(re.fullmatch(r"([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}", s))
