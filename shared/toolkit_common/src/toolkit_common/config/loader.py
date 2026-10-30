"""Configuration file loader supporting YAML, TOML, and JSON."""

import json
from pathlib import Path
from typing import Any, Dict

import yaml

try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib  # type: ignore
    except ImportError:
        tomllib = None  # type: ignore


class ConfigError(Exception):
    """Raised when configuration file parsing fails."""
    pass


def load_config_file(path: str | Path) -> Dict[str, Any]:
    """Load and parse a config file (YAML, TOML, or JSON)."""
    p = Path(path).resolve()
    if not p.is_file():
        raise ConfigError(f"Config file not found: {p}")

    ext = p.suffix.lower()
    try:
        content = p.read_text(encoding="utf-8")
        if ext in (".yaml", ".yml"):
            parsed = yaml.safe_load(content)
            return parsed if isinstance(parsed, dict) else {}
        elif ext == ".json":
            parsed = json.loads(content)
            return parsed if isinstance(parsed, dict) else {}
        elif ext == ".toml":
            if tomllib is None:
                raise ConfigError("TOML support requires Python 3.11+ or tomli")
            return tomllib.loads(content)
        else:
            # Fallback attempt YAML then JSON
            try:
                parsed = yaml.safe_load(content)
                if isinstance(parsed, dict):
                    return parsed
            except Exception:
                pass
            return json.loads(content)
    except Exception as e:
        raise ConfigError(f"Failed to parse config file {p}: {e}") from e
