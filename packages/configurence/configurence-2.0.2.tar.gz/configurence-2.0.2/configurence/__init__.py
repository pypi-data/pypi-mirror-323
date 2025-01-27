# -*- coding: utf-8 -*-

"""
A simple CLI configuration management library
"""

from abc import ABC
from dataclasses import asdict, dataclass
from dataclasses import field as _field
from dataclasses import fields, MISSING, replace
import logging
import os
import os.path
from pathlib import Path
import platform
from typing import (
    Any,
    Callable,
    cast,
    Dict,
    get_args,
    get_origin,
    NoReturn,
    Optional,
    Set,
    Type,
    TypeVar,
    Union,
)

try:
    from typing import Self
except ImportError:
    Self = Any

from appdirs import user_config_dir
import yaml

try:
    from yaml import CDumper as Dumper
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Dumper, Loader

logger = logging.getLogger(__name__)


def _is_optional(type_: Any) -> bool:
    return get_origin(type_) is Union and type(None) in get_args(type_)


def _optional_of(type_: Any) -> Any:
    if not _is_optional(type_):
        raise ValueError(f"{type_} is not optional")
    return [arg for arg in get_args(type_) if arg is not type(None)][0]


def global_file(name: str) -> str:
    """
    Get the global file path for the config.
    """

    if platform.system() == "Windows":
        raise NotImplementedError("global_file")

    return f"/etc/{name}.yaml"


def default_file(name: str) -> str:
    """
    Get the default file path for the config.
    """

    config_dir: str = (
        user_config_dir(name)
        if platform.system() == "Windows"
        else os.path.expanduser("~/.config")
    )

    return os.path.join(config_dir, f"{name}.yaml")


def _read_config_file(file: str) -> Dict[str, Any]:
    with open(file, "r") as f:
        logger.debug(f"Loading config from {file}...")
        return yaml.load(f, Loader=Loader)


def _write_config_file(file: str, config: Dict[str, Any]) -> None:
    os.makedirs(Path(file).parent, exist_ok=True)

    with open(file, "w") as f:
        yaml.dump(config, f, Dumper=Dumper)

    logger.info(f"Wrote configuration to {file}.")


def field(
    *,
    default: Any = MISSING,
    default_factory: Any = MISSING,
    init: bool = True,
    repr: bool = True,
    hash: Any = None,
    compare: bool = True,
    metadata: Optional[Any] = None,
    env_var: Optional[str] = None,
    load: Optional[Callable[[str], Any]] = None,
    dump: Optional[Callable[[Any], str]] = None,
    kw_only: Any = MISSING,
) -> Any:
    """
    A configuration field. Compatible with dataclass fields, but with extra
    metadata for environment variables and conversions.
    """

    md: Any = metadata
    if metadata:
        md = metadata
    else:
        md = dict()
    if isinstance(md, dict):
        md.update(
            env_var=env_var if env_var else md.get("env_var", None),
            load=load if load else md.get("load", None),
            dump=dump if dump else md.get("dump", None),
        )

    # TODO: I don't know why the type checker is unhappy with this call, but
    # Python seems fine with it and it matches Python's docs
    return cast(Any, _field)(
        default=default,
        default_factory=default_factory,
        init=init,
        repr=repr,
        hash=hash,
        compare=compare,
        metadata=md,
        kw_only=kw_only,
    )


def to_bool(value: str) -> bool:
    if value.lower() in {"true", "yes", "y", "1"}:
        return True
    elif value.lower() in {"false", "no", "n", "0"}:
        return False
    else:
        raise ValueError(f"Can not convert {value} to bool")


def _env_prefix(name: str) -> str:
    return name.upper().replace("-", "_")


def _from_environment(cls: Any, env_prefix: str) -> Dict[str, Any]:
    env: Dict[str, Any] = dict()
    for f in fields(cls):
        if f.metadata.get("env_var", None):
            env_var = f"{env_prefix}_{f.metadata['env_var']}"
            if env_var in os.environ:
                type_: Any = f.type
                var: Any = os.environ[env_var]
                if _is_optional(type_):
                    if var == "":
                        var = None
                        type_ = None
                    else:
                        type_ = _optional_of(type_)
                if f.metadata.get("load", None):
                    env[f.name] = f.metadata["load"](var)
                elif type_ is float:
                    env[f.name] = float(var)
                elif type_ is int:
                    env[f.name] = int(var)
                elif type_ is bool:
                    env[f.name] = to_bool(var)
                else:
                    env[f.name] = var
    return env


@dataclass
class BaseConfig(ABC):
    file: Optional[str]

    @property
    def name(self: Self) -> str:
        return cast(Any, self)._name

    @property
    def _file(self: Self) -> str:
        return self.file or default_file(self.name)

    @classmethod
    def from_environment(cls: Type[Self], file: Optional[str] = None) -> Self:
        """
        Load configuration from the environment.
        """

        name = cast(Any, cls)._name

        logger.debug("Loading config from environment...")
        env = _from_environment(cls, _env_prefix(name))
        env["file"] = file or default_file(name)
        return cls(**env)

    @classmethod
    def from_file(
        cls: Type[Self],
        file: Optional[str] = None,
        global_: bool = False,
        load_environment: bool = False,
        create_file: bool = False,
    ) -> Self:
        """
        Load configuration from a file. Optionally load environment overrides and
        optionally create the file.
        """

        name = cast(Any, cls)._name
        env_prefix = _env_prefix(name)
        env_config = f"{env_prefix}_CONFIG"

        if file:
            _file = file
        elif env_config in os.environ:
            _file = os.environ[env_config]
        elif global_:
            _file = global_file(name)
        else:
            _file = default_file(name)

        found_file = False
        kwargs: Dict[str, Any] = dict(file=_file)
        try:
            found_file = True
            conf: Dict[str, Any] = _read_config_file(_file)
            for f in fields(cls):
                if f.name in {"name", "file"}:
                    continue
                if f.metadata.get("load", None):
                    kwargs[f.name] = f.metadata["load"](conf[f.name])
                else:
                    kwargs[f.name] = conf[f.name]
        except FileNotFoundError:
            try:
                kwargs.update(_read_config_file(global_file(name)))
            except FileNotFoundError:
                pass

        if load_environment:
            logger.debug("Loading environment overrides...")
            kwargs.update(_from_environment(cls, env_prefix))

        config = cls(**kwargs)

        if not found_file and create_file:
            config.to_file()

        return config

    def _assert_has(self: Self, name: str) -> None:
        if not hasattr(self, name) or name.startswith("_"):
            raise ValueError(f"Unknown configuration parameter {name}")

    def get(self: Self, name: str) -> Any:
        """
        Get a configuration parameter by name.
        """

        self._assert_has(name)
        return getattr(self, name)

    def _field_setters(self: Self) -> Dict[Any, Callable[[str, str], None]]:
        setters: Dict[Any, Callable[[str, str], None]] = {
            str: self.set_str,
            Optional[str]: self.set_str,
            bool: self.set_bool,
            Optional[bool]: self.set_bool,
            int: self.set_int,
            Optional[int]: self.set_int,
            float: self.set_float,
            Optional[float]: self.set_float,
        }

        for f in fields(cast(Any, self)):
            if f.metadata and f.type not in setters and f.metadata.get("load", None):

                def setter(name: str, value: str) -> None:
                    setattr(self, name, f.metadata["load"](value))

                setters[f.type] = setter

        return setters

    def _optional_field_types(self: Self) -> Set[Any]:
        optional: Set[Any] = set()

        for f in fields(cast(Any, self)):
            if _is_optional(f.type):
                optional.add(f.type)

        return optional

    def set(self: Self, name: str, value: str) -> None:
        """
        Set a configuration parameter by name and string value.
        """

        self._assert_has(name)

        setters = self._field_setters()

        for f in fields(cast(Any, self)):
            if f.name == name:
                if f.type in setters:
                    setters[f.type](name, value)
                    return
                else:
                    raise ValueError(f"Unknown type {f.type}")

    def set_str(self: Self, name: str, value: str) -> None:
        setattr(self, name, value)

    def set_bool(self: Self, name: str, value: str) -> None:
        if value.lower() in {"true", "yes", "y", "1"}:
            setattr(self, name, True)
        elif value.lower() in {"false", "no", "n", "0"}:
            setattr(self, name, False)
        else:
            raise ValueError(f"Can not convert {value} to bool")

    def set_float(self: Self, name: str, value: str) -> None:
        setattr(self, name, float(value))

    def set_int(self: Self, name: str, value: str) -> None:
        setattr(self, name, int(value))

    def unset(self: Self, name: str) -> None:
        """
        Unset an optional parameter.
        """

        self._assert_has(name)

        optional_types = self._optional_field_types()

        for f in fields(cast(Any, self)):
            if f.name == name:
                if f.type in optional_types:
                    self._unset(name)
                else:
                    self._required(name)

    def _required(self: Self, name: str) -> NoReturn:
        raise ValueError(f"{name} is a required configuraiton parameter")

    def _unset(self: Self, name: str) -> None:
        setattr(self, name, None)

    def as_dict(self: Self) -> Dict[str, Any]:
        inst = cast(Any, self)
        d: Dict[str, Any] = asdict(inst)

        for f in fields(cast(Any, self)):
            if f.metadata.get("dump", None):
                d[f.name] = f.metadata["dump"](getattr(self, f.name))

        del d["file"]

        return d

    def to_file(self: Self, file: Optional[str] = None) -> Self:
        """
        Save the configuration to a file.
        """

        file = file or self._file
        inst = cast(Any, self)

        _write_config_file(file, self.as_dict())

        return replace(inst, file=file)

    def __repr__(self: Self) -> str:
        d = dict(name=self.name, file=self.file)
        d.update(self.as_dict())
        return yaml.dump(d, Dumper=Dumper)


C = TypeVar("C", bound=BaseConfig)


def config(name: str) -> Callable[[Type[C]], Type[C]]:
    def decorator(cls: Type[C]) -> Type[C]:
        """
        A configuration object. This class is typically used by a CLI, but may
        also be useful for scripts or Jupyter notebooks using its configuration.
        """

        cfg_cls = dataclass(cls)
        cast(Any, cfg_cls)._name = name
        cfg_cls.__repr__ = BaseConfig.__repr__
        return cfg_cls

    return decorator
