from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def home() -> Path:
    return Path(os.environ.get("OPENMINION_HOME", ROOT / ".om-home")).expanduser()


def data_root() -> Path:
    return Path(os.environ.get("OPENMINION_DATA_ROOT", home() / ".openminion")).expanduser()


def ensure_local_home() -> Path:
    """Keep OpenMinion state inside the project tree."""
    resolved_home = home()
    resolved_data = data_root()
    resolved_home.mkdir(parents=True, exist_ok=True)
    resolved_data.mkdir(parents=True, exist_ok=True)
    os.environ["OPENMINION_HOME"] = str(resolved_home)
    os.environ["OPENMINION_DATA_ROOT"] = str(resolved_data)
    forbidden = ("/home/box/secure", "/home/box/.local/share")
    for label, path in (("OPENMINION_HOME", resolved_home), ("OPENMINION_DATA_ROOT", resolved_data)):
        resolved = path.resolve()
        for bad in forbidden:
            if resolved == Path(bad) or str(resolved).startswith(bad + "/"):
                raise RuntimeError(f"{label} must not be {bad}")
    return resolved_home


def config_path() -> Path:
    ensure_local_home()
    for name in ("agents.json", "config.yaml", "config.yml", "openminion.yaml"):
        candidate = data_root() / name
        if candidate.exists():
            return candidate
    return data_root() / "agents.json"
