# -*- coding: utf-8 -*-

import os.path
from typing import Any, Dict, Optional, Type
from unittest.mock import Mock

try:
    from typing import Self
except ImportError:
    Self = Any

import pytest
import yaml

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from configurence import BaseConfig
from configurence import config as config_
from configurence import field


class Other:
    def __init__(self: Self, name: str) -> None:
        self.name = name

    def __eq__(self: Self, other: Any) -> bool:
        return isinstance(other, Other) and self.name == other.name


def load_other(value: str) -> Other:
    return Other(value)


def dump_other(value: Other) -> str:
    return value.name


@pytest.fixture
def other_cls() -> Type[Other]:
    return Other


@pytest.fixture
def config_cls(app_name):
    @config_(app_name)
    class Config(BaseConfig):
        some_str: str = field(default="", env_var="SOME_STR")
        opt_str: Optional[str] = field(default=None, env_var="OPT_STR")
        some_bool: bool = field(default=False, env_var="SOME_BOOL")
        opt_bool: Optional[bool] = field(default=None, env_var="OPT_BOOL")
        some_int: int = field(default=0, env_var="SOME_INT")
        opt_int: Optional[int] = field(default=None, env_var="OPT_INT")
        some_float: float = field(default=0.0, env_var="SOME_FLOAT")
        opt_float: Optional[float] = field(default=None, env_var="OPT_FLOAT")

        some_other: Other = field(
            default_factory=lambda: Other("default"),
            env_var="SOME_OTHER",
            load=load_other,
            dump=dump_other,
        )

    return Config


@pytest.fixture
def app_name() -> str:
    return "test-app"


@pytest.fixture
def local_filename(app_name) -> str:
    return os.path.expanduser(f"~/.config/{app_name}.yaml")


@pytest.fixture
def global_filename(app_name) -> str:
    return f"/etc/{app_name}.yaml"


@pytest.fixture
def config(config_cls, local_filename):
    return config_cls(
        file=local_filename,
        some_str="some_str",
        opt_str=None,
        some_bool=True,
        opt_bool=None,
        some_int=1,
        opt_int=None,
        some_float=1.0,
        opt_float=None,
    )


@pytest.fixture
def local_config(config_cls, read_config_file, write_config_file):
    return config_cls.from_file()


@pytest.fixture
def local_config_no_file(config_cls, read_config_file_not_found, write_config_file):
    return config_cls.from_file()


@pytest.fixture
def global_config(config_cls, read_config_file, write_config_file):
    return config_cls.from_file(global_=True)


@pytest.fixture
def global_config_no_file(config_cls, read_config_file_not_found, write_config_file):
    return config_cls.from_file(global_=True)


@pytest.fixture
def config_file() -> str:
    return """opt_bool: null
opt_float: null
opt_int: null
opt_str: null
some_bool: true
some_float: 1.0
some_int: 1
some_other: default
some_str: some_str"""


@pytest.fixture
def environ(monkeypatch) -> Dict[str, str]:
    env = dict(
        TEST_APP_OPT_FLOAT="",
        TEST_APP_OPT_INT="",
        TEST_APP_OPT_STR="",
        TEST_APP_SOME_BOOL="1",
        TEST_APP_SOME_FLOAT="2.0",
        TEST_APP_SOME_INT="5",
        TEST_APP_SOME_OTHER="foo",
        TEST_APP_SOME_STR="bar",
    )
    monkeypatch.setattr("configurence.os.environ", env)
    return env


@pytest.fixture
def read_config_file(monkeypatch, config_file):
    config = yaml.load(config_file, Loader=Loader)
    mock = Mock(name="_read_config_file", return_value=config)
    monkeypatch.setattr("configurence._read_config_file", mock)
    return mock


@pytest.fixture
def read_config_file_not_found(monkeypatch):
    mock = Mock(name="_read_config_file", side_effect=FileNotFoundError(""))
    monkeypatch.setattr("configurence._read_config_file", mock)
    return mock


@pytest.fixture
def write_config_file(monkeypatch):
    mock = Mock(name="_write_config_file")
    monkeypatch.setattr("configurence._write_config_file", mock)
    return mock
