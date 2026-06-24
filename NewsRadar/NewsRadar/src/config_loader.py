"""
src/config_loader.py
---------------------
Load and validate config/config.json.
"""

import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "../config/config.json")


def load_config(path: str = CONFIG_PATH) -> dict:
    """Load config from JSON file."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config not found at: {path}")
    with open(path, "r") as f:
        config = json.load(f)
    _validate(config)
    return config


def _validate(config: dict):
    required_keys = ["keywords", "feeds", "email", "schedule_time", "db_path"]
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config key: '{key}'")
    if not config["keywords"]:
        raise ValueError("'keywords' list cannot be empty.")
    if not config["feeds"]:
        raise ValueError("'feeds' list cannot be empty.")
