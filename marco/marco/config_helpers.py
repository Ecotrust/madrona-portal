import configparser
import os


_TRUE_VALUES = {"1", "true", "yes", "on"}
_FALSE_VALUES = {"0", "false", "no", "off"}


def env_str(
    env_key: str,
    cfg_section: configparser.SectionProxy,
    cfg_key: str,
    default: str = "",
) -> str:
    """Resolve a string setting using env > config.ini > default precedence."""
    raw = os.environ.get(env_key)
    if raw is not None:
        return raw
    raw = cfg_section.get(cfg_key)
    if raw is not None:
        return raw
    return default


def parse_bool(value: object, *, setting_name: str = "setting") -> bool:
    """Parse a bool from common string values, raising on invalid input."""
    if isinstance(value, bool):
        return value
    if value is None:
        raise ValueError(f"{setting_name} cannot be None")

    normalized = str(value).strip().lower()
    if normalized in _TRUE_VALUES:
        return True
    if normalized in _FALSE_VALUES:
        return False

    raise ValueError(
        f"Invalid boolean value for {setting_name}: {value!r}. "
        "Use one of: 1/0, true/false, yes/no, on/off."
    )


def env_bool(
    env_key: str,
    cfg_section: configparser.SectionProxy,
    cfg_key: str,
    default: bool = False,
) -> bool:
    """Resolve and parse a bool setting using env > config.ini > default."""
    raw = os.environ.get(env_key)
    if raw is not None:
        return parse_bool(raw, setting_name=env_key)
    raw = cfg_section.get(cfg_key)
    if raw is not None:
        return parse_bool(raw, setting_name=cfg_key)
    return default


def env_int(
    env_key: str,
    cfg_section: configparser.SectionProxy,
    cfg_key: str,
    default: int,
) -> int:
    """Resolve and parse an int setting using env > config.ini > default."""
    raw = os.environ.get(env_key)
    if raw is not None:
        return int(str(raw).strip())
    raw = cfg_section.get(cfg_key)
    if raw is not None:
        return int(str(raw).strip())
    return default
