import os
from pathlib import Path

from .models import Kit

CONFIG_FILENAME = "config.toml"
DEFAULT_LZKIT_PATH = "~/.lzkit"


def find_lzkit_path() -> Path:
    lz_kit_path: str = os.getenv("LZKIT_PATH", DEFAULT_LZKIT_PATH)
    return Path(lz_kit_path).expanduser().resolve()


def load_config() -> Kit:
    """
    Load config from {lzkit_path}/config.toml (or .json/.yaml if you want).
    Then parse into a pydantic model with sensible defaults.
    If file doesn't exist or can't parse, returns a default KitConfig.
    """
    lz_path = find_lzkit_path()
    config_path = lz_path / CONFIG_FILENAME

    # Lazy import to avoid circular references
    from ..file import load

    if not config_path.exists():
        return Kit()  # return defaults if no file

    raw_data = load(config_path, raise_on_error=False)
    if not raw_data or not isinstance(raw_data, dict):
        # If load fails or isn't a dict, fallback to defaults
        return Kit()

    # Merge with Pydantic
    # noinspection PyBroadException
    try:
        return Kit(**raw_data)

    except Exception:
        # If the file is invalid or partial, you can log or ignore
        return Kit()


def save_config(cfg: Kit, path: Path | None = None) -> bool:
    """
    Write the config to {lzkit_path}/config.toml by default.
    Let the extension do the work in .files.dump.
    """
    if path is None:
        lz_path = find_lzkit_path()
        path = lz_path / CONFIG_FILENAME

    from ..file import dump

    data_dict = cfg.dict()  # Convert Pydantic model to dict
    ok = dump(path, data_dict, raise_on_error=False)
    return ok


def new_config(overwrite: bool = False) -> None:
    """
    Create a new default config if none exists. Writes out the
    default TOML from defaults.py to config.toml in the lzkit_path.
    If overwrite=False and a config file exists, do nothing.
    """
    lz_path = find_lzkit_path()
    lz_path.mkdir(parents=True, exist_ok=True)
    config_path = lz_path / CONFIG_FILENAME

    if not config_path.exists() or overwrite:
        # Lazy import to avoid circular references
        from ..file import dump

        success = dump(config_path, Kit().model_dump(), raise_on_error=False)
        if success:
            print(f"Created new config at {config_path}")
        else:
            print(f"Failed to create new config at {config_path}")
