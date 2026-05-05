import configparser

import pytest

from marco.config_helpers import env_bool, env_int, env_str, parse_bool


def _section(values: dict[str, str]) -> configparser.SectionProxy:
    cfg = configparser.ConfigParser()
    cfg["APP"] = values
    return cfg["APP"]


def test_env_str_prefers_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    section = _section({"APP_NAME": "FromConfig"})
    monkeypatch.setenv("APP_NAME", "FromEnv")
    assert env_str("APP_NAME", section, "APP_NAME", "Default") == "FromEnv"


def test_env_str_falls_back_to_config_then_default(monkeypatch: pytest.MonkeyPatch) -> None:
    section = _section({"APP_NAME": "FromConfig"})
    monkeypatch.delenv("APP_NAME", raising=False)
    assert env_str("APP_NAME", section, "APP_NAME", "Default") == "FromConfig"
    assert env_str("MISSING", section, "MISSING", "Default") == "Default"


def test_env_bool_prefers_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    section = _section({"DEBUG": "false"})
    monkeypatch.setenv("DEBUG", "true")
    assert env_bool("DEBUG", section, "DEBUG", False) is True


def test_env_bool_falls_back_to_default(monkeypatch: pytest.MonkeyPatch) -> None:
    section = _section({})
    monkeypatch.delenv("DEBUG", raising=False)
    assert env_bool("DEBUG", section, "DEBUG", False) is False
    assert env_bool("DEBUG", section, "DEBUG", True) is True


def test_parse_bool_accepts_common_values() -> None:
    assert parse_bool("1") is True
    assert parse_bool("yes") is True
    assert parse_bool("ON") is True
    assert parse_bool("0") is False
    assert parse_bool("no") is False
    assert parse_bool("off") is False


def test_parse_bool_rejects_invalid_values() -> None:
    with pytest.raises(ValueError):
        parse_bool("maybe", setting_name="DEBUG")


def test_env_int_prefers_environment_and_parses(monkeypatch: pytest.MonkeyPatch) -> None:
    section = _section({"PORT": "25"})
    monkeypatch.setenv("EMAIL_PORT", "587")
    assert env_int("EMAIL_PORT", section, "PORT", 25) == 587


def test_env_int_falls_back_to_config_then_default(monkeypatch: pytest.MonkeyPatch) -> None:
    section = _section({"PORT": "2525"})
    monkeypatch.delenv("EMAIL_PORT", raising=False)
    assert env_int("EMAIL_PORT", section, "PORT", 25) == 2525

    empty_section = _section({})
    assert env_int("EMAIL_PORT", empty_section, "PORT", 25) == 25
