# -*- coding: utf-8 -*-
# cython: language_level = 3


from typing import override

from .._protocols import SupportsReadAndReadline
from .._protocols import SupportsWrite
from ..abc import ABCConfigFile
from ..base import ConfigData
from ..main import BaseLocalFileConfigSL

try:
    # noinspection PyPackageRequirements, PyUnresolvedReferences
    import toml
except ImportError:  # pragma: no cover
    raise ImportError("toml is not installed. Please install it with `pip install toml`") from None


class TomlSL(BaseLocalFileConfigSL):
    """
    Toml格式处理器
    """

    @property
    @override
    def processor_reg_name(self) -> str:
        return "toml"

    @property
    @override
    def file_ext(self) -> tuple[str, ...]:
        return ".toml",

    @override
    def save_file(
            self,
            config_file: ABCConfigFile,
            target_file: SupportsWrite[str],
            *merged_args,
            **merged_kwargs
    ) -> None:
        with self.raises():
            toml.dump(config_file.data.data, target_file)

    @override
    def load_file[C: ABCConfigFile](
            self, config_file_cls: type[C],
            source_file: SupportsReadAndReadline[str],
            *merged_args,
            **merged_kwargs
    ) -> C:
        with self.raises():
            data = toml.load(source_file)

        return config_file_cls(ConfigData(data), config_format=self.processor_reg_name)


__all__ = (
    "TomlSL",
)
