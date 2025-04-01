# -*- coding: utf-8 -*-
# cython: language_level = 3


import pickle
from typing import override

from .._protocols import SupportsReadAndReadline
from .._protocols import SupportsWrite
from ..abc import ABCConfigFile
from ..base import ConfigData
from ..main import BaseLocalFileConfigSL


class PickleSL(BaseLocalFileConfigSL):
    """
    pickle格式处理器
    """

    @property
    @override
    def processor_reg_name(self) -> str:
        return "pickle"

    @property
    @override
    def file_ext(self) -> tuple[str, ...]:
        return ".pickle",

    _s_open_kwargs = dict(mode="wb")

    @override
    def save_file(
            self,
            config_file: ABCConfigFile,
            target_file: SupportsWrite[bytes],
            *merged_args,
            **merged_kwargs
    ) -> None:
        with self.raises():
            pickle.dump(config_file.data.data, target_file, *merged_args, **merged_kwargs)

    _l_open_kwargs = dict(mode="rb")

    @override
    def load_file[C: ABCConfigFile](
            self, config_file_cls: type[C],
            source_file: SupportsReadAndReadline[bytes],
            *merged_args,
            **merged_kwargs
    ) -> C:
        with self.raises():
            data = pickle.load(source_file, *merged_args, **merged_kwargs)

        return config_file_cls(ConfigData(data), config_format=self.processor_reg_name)


__all__ = (
    "PickleSL",
)
