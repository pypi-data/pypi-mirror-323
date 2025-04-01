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
    import yaml
except ImportError:  # pragma: no cover
    raise ImportError("PyYaml is not installed. Please install it with `pip install PyYaml`") from None


class PyYamlSL(BaseLocalFileConfigSL):
    """
    基于PyYaml的yaml处理器
    """

    @property
    @override
    def processor_reg_name(self) -> str:
        return "yaml"

    @property
    @override
    def file_ext(self) -> tuple[str, ...]:
        return ".yaml",

    @override
    def save_file(
            self,
            config_file: ABCConfigFile,
            target_file: SupportsWrite[str],
            *merged_args,
            **merged_kwargs
    ) -> None:
        with self.raises():
            yaml.safe_dump(config_file.data.data, target_file, *merged_args, **merged_kwargs)

    @override
    def load_file[C: ABCConfigFile](
            self, config_file_cls: type[C],
            source_file: SupportsReadAndReadline[str],
            *merged_args,
            **merged_kwargs
    ) -> C:
        with self.raises():
            data = yaml.safe_load(source_file)

        return config_file_cls(ConfigData(data), config_format=self.processor_reg_name)


__all__ = (
    "PyYamlSL",
)
