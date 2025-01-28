# -*- coding: utf-8 -*-

from typing import Any

import pytest


@pytest.mark.parametrize(
    "name",
    [
        "some_str",
        "some_bool",
        "some_int",
        "some_float",
        "opt_str",
        "opt_bool",
        "opt_int",
        "opt_float",
    ],
)
def test_get(config, name: str) -> None:
    assert config.get(name) == getattr(config, name)


def test_get_unknown(config) -> None:
    with pytest.raises(ValueError):
        config.get("pony")


OTHER = "__other__"


@pytest.mark.parametrize(
    "name,value,expected",
    [
        ("some_str", "foo", "foo"),
        ("some_bool", "true", True),
        ("some_bool", "false", False),
        ("some_int", "1", 1),
        ("some_float", "1.0", 1.0),
        ("opt_str", "foo", "foo"),
        ("opt_bool", "true", True),
        ("opt_bool", "false", False),
        ("opt_int", "1", 1),
        ("opt_float", "1.0", 1.0),
        ("some_other", "foo", OTHER),
    ],
)
def test_set(config, other_cls, name: str, value: str, expected: Any) -> None:
    if expected == OTHER:
        expected = other_cls(value)
    config.set(name, value)
    assert config.get(name) == expected


@pytest.mark.parametrize(
    "name,value",
    [
        ("some_bool", "foo"),
        ("some_int", "foo"),
    ],
)
def test_set_value_error(config, name: str, value: str) -> None:
    with pytest.raises(ValueError):
        config.set(name, value)


def test_set_unknown(config) -> None:
    with pytest.raises(ValueError):
        config.set("pony", "pony")


@pytest.mark.parametrize(
    "name",
    [
        "opt_str",
        "opt_bool",
        "opt_int",
        "opt_float",
    ],
)
def test_unset(config, name: str) -> None:
    config.unset(name)
    assert config.get(name) is None


@pytest.mark.parametrize(
    "name",
    [
        "some_str",
        "some_bool",
        "some_int",
        "some_float",
    ],
)
def test_unset_required(config, name: str) -> None:
    with pytest.raises(ValueError):
        config.unset(name)
