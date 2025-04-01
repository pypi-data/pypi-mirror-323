# -*- coding: utf-8 -*-
# cython: language_level = 3


import os.path
from abc import ABC
from abc import abstractmethod
from collections.abc import Callable
from collections.abc import Iterable
from collections.abc import Mapping
from contextlib import contextmanager
from copy import deepcopy
from typing import Any
from typing import Literal
from typing import Optional
from typing import override

import wrapt
from pyrsistent import PMap
from pyrsistent import pmap

from ._protocols import SupportsReadAndReadline
from ._protocols import SupportsWrite
from .abc import ABCConfigData
from .abc import ABCConfigFile
from .abc import ABCConfigPool
from .abc import ABCConfigSL
from .abc import ABCSLProcessorPool
from .abc import SLArgument
from .base import BaseConfigPool
from .base import ConfigData
from .base import ConfigFile
from .errors import FailedProcessConfigFileError
from .validators import DefaultValidatorFactory
from .validators import ValidatorFactoryConfig
from .validators import ValidatorTypes
from .validators import pydantic_validator


class RequiredPath:
    """
    对需求的键进行存在检查、类型检查、填充默认值
    """

    def __init__[V: Any, D: ABCConfigData](
            self,
            validator: V,
            validator_factory: Optional[
                Callable[[V, ValidatorFactoryConfig], Callable[[D], D]] | ValidatorTypes | Literal["ignore", "pydantic"]
                ] = ValidatorTypes.DEFAULT,
            static_config: Optional[ValidatorFactoryConfig] = None
    ):
        """
        .. tip::
           提供static_config参数，可以避免在filter中反复调用validator_factory以提高性能(filter配置一切都为默认值的前提下)

        :param validator: 数据验证器
        :type validator: Any
        :param validator_factory: 数据验证器工厂
        :type validator_factory:
            Optional[
            Callable[
            [Any, validators.ValidatorFactoryConfig],
            Callable[[ABCConfigData], ABCConfigData]
            ] | validators.ValidatorTypes | Literal["ignore", "pydantic"]
            ]
        :param static_config: 静态配置
        :type static_config: Optional[validators.ValidatorFactoryConfig]
        """
        if not callable(validator_factory):
            validator_factory = ValidatorTypes(validator_factory)
        if isinstance(validator_factory, ValidatorTypes):
            validator_factory = self.ValidatorFactories[validator_factory]

        self._validator: Iterable[str] | Mapping[str, type] = deepcopy(validator)
        self._validator_factory: Callable[[V, ValidatorFactoryConfig], Callable[[D], D]] = validator_factory
        if static_config is not None:
            self._static_validator: Optional[Callable[[D], D]] = self._validator_factory(self._validator, static_config)
        else:
            self._static_validator = None

    ValidatorFactories: dict[
        ValidatorTypes,
        Callable[[Any, ValidatorFactoryConfig], Callable[[ABCConfigData], ABCConfigData]]
    ] = {
        ValidatorTypes.DEFAULT: DefaultValidatorFactory,
        ValidatorTypes.IGNORE: lambda v, *_: v,
        ValidatorTypes.PYDANTIC: pydantic_validator,
    }

    def filter[D: ABCConfigData](
            self,
            data: D,
            *,
            allow_modify: Optional[bool] = None,
            ignore_missing: Optional[bool] = None,
            **extra
    ) -> D:
        """
        检查过滤需求的键

        .. attention::
           返回的配置数据是*快照*

        .. caution::
           提供了任意配置参数(``allow_modify``, ``ignore_missing``, ...)时,这次调用将完全舍弃static_config使用当前提供的配置参数

           这会导致调用validator_factory产生额外开销(如果你提供static_config参数是为了避免反复调用validator_factory的话)

        :param data: 要过滤的原始数据
        :type data: ABCConfigData
        :param allow_modify: 是否允许值不存在时修改data参数对象填充默认值(即使为False仍然会在结果中填充默认值,但不会修改data参数对象)
        :type allow_modify: bool
        :param ignore_missing: 忽略丢失的键
        :type ignore_missing: bool
        :param extra: 额外参数
        :type extra: Any

        :return: 处理后的配置数据*快照*
        :rtype: ABCConfigData

        :raise ConfigDataTypeError: 配置数据类型错误
        :raise RequiredPathNotFoundError: 必要的键未找到
        :raise UnknownErrorDuringValidateError: 验证过程中发生未知错误
        """
        config_kwargs = {}
        if allow_modify is not None:
            config_kwargs["allow_modify"] = allow_modify
        if ignore_missing is not None:
            config_kwargs["ignore_missing"] = ignore_missing
        if extra:
            config_kwargs["extra"] = extra

        if (self._static_validator is None) or config_kwargs:
            config = ValidatorFactoryConfig(**config_kwargs)
            validator: Callable[[ABCConfigData], ABCConfigData] = self._validator_factory(self._validator, config)
        else:
            validator = self._static_validator

        return validator(data)


class ConfigPool(BaseConfigPool):
    """
    配置池
    """

    @override
    def load[F: ABCConfigFile](
            self,
            namespace: str,
            file_name: str,
            *,
            config_file_cls: type[F] = ConfigFile,
            config_formats: Optional[str | Iterable[str]] = None,
            allow_create: bool = False
    ) -> F:
        if (namespace, file_name) in self:
            return self.get(namespace, file_name)

        def processor(pool, ns, fn, cf):
            try:
                result = config_file_cls.load(pool, ns, fn, cf)
            except FileNotFoundError:
                if not allow_create:
                    raise
                result = config_file_cls(
                    ConfigData(),
                    config_format=cf
                )

            pool.set(namespace, file_name, result)
            return result

        return self._test_all_sl(namespace, file_name, config_formats, processor)

    @override
    def require(
            self,
            namespace: str,
            file_name: str,
            validator: Any,
            validator_factory: Any = ValidatorTypes.DEFAULT,
            static_config: Optional[Any] = None,
            **kwargs
    ):
        return RequireConfigDecorator(
            self,
            namespace,
            file_name,
            RequiredPath(validator, validator_factory, static_config),
            **kwargs
        )


class RequireConfigDecorator:
    """
    配置获取器，可作装饰器使用
    """

    def __init__(
            self,
            config_pool: ABCConfigPool,
            namespace: str,
            file_name: str,
            required: RequiredPath,
            *,
            config_file_cls: type[ABCConfigFile] = ConfigFile,
            config_formats: Optional[str | Iterable[str]] = None,
            allow_create: bool = True,
            cache_config: Optional[Callable[[Callable], Callable]] = None,
            filter_kwargs: Optional[dict[str, Any]] = None
    ):
        """
        :param config_pool: 所在的配置池
        :type config_pool: ConfigPool
        :param namespace: 详见 :py:func:`ConfigPool.load`
        :param file_name: 详见 :py:func:`ConfigPool.load`
        :param required: 需求的键
        :type required: RequiredPath
        :param config_file_cls: 详见 :py:func:`ConfigPool.load`
        :param config_formats: 详见 :py:func:`ConfigPool.load`
        :param allow_create: 详见 :py:func:`ConfigPool.load`
        :param cache_config: 缓存配置的装饰器，默认为None，即不缓存
        :type cache_config: Optional[Callable[[Callable], Callable]]
        :param filter_kwargs: :py:func:`RequiredPath.filter` 要绑定的默认参数，默认为allow_modify=True
        :type filter_kwargs: dict[str, Any]

        :raise UnsupportedConfigFormatError: 不支持的配置格式
        """
        config = config_pool.load(namespace, file_name, config_file_cls=config_file_cls, config_formats=config_formats,
                                  allow_create=allow_create)

        if filter_kwargs is None:
            filter_kwargs = {}

        self._config: ABCConfigFile = config
        self._required = required
        self._filter_kwargs = {"allow_modify": True} | filter_kwargs
        self._cache_config: Callable = cache_config if cache_config is not None else lambda x: x

    def check(self, *, ignore_cache: bool = False, **filter_kwargs) -> Any:
        """
        手动检查配置

        :param ignore_cache: 是否忽略缓存
        :type ignore_cache: bool
        :param filter_kwargs: RequiredConfig.filter的参数
        :return: 得到的配置数据
        :rtype: Any
        """
        kwargs = self._filter_kwargs | filter_kwargs
        if ignore_cache:
            return self._required.filter(self._config.data, **kwargs)
        return self._wrapped_filter(**kwargs)

    def __call__(self, func):
        @wrapt.decorator
        def wrapper(wrapped, _instance, args, kwargs):
            config_data = self._wrapped_filter(**self._filter_kwargs)

            return wrapped(
                *(config_data, *args),
                **kwargs
            )

        return wrapper(func)

    def _wrapped_filter(self, **kwargs):
        return self._cache_config(self._required.filter(self._config.data, **kwargs))


DefaultConfigPool = ConfigPool()
"""
默认配置池
"""
requireConfig = DefaultConfigPool.require
"""
:py:attr:`DefaultConfigPool` ``.require()``

.. seealso::
   :py:func:`ConfigPool.require`
"""
saveAll = DefaultConfigPool.save_all
"""
:py:attr:`DefaultConfigPool` ``.save_all()``

.. seealso::
   :py:func:`ConfigPool.save_all`
"""
get = DefaultConfigPool.get
"""
:py:attr:`DefaultConfigPool` ``.get()``

.. seealso::
   :py:func:`ConfigPool.get`
"""
set_ = DefaultConfigPool.set
"""
:py:attr:`DefaultConfigPool` ``.set()``

.. seealso::
   :py:func:`ConfigPool.set`
"""
save = DefaultConfigPool.save
"""
:py:attr:`DefaultConfigPool` ``.save()``

.. seealso::
   :py:func:`ConfigPool.save`
"""
load = DefaultConfigPool.load
"""
:py:attr:`DefaultConfigPool` ``.load()``

.. seealso::
   :py:func:`ConfigPool.load`
"""


class BaseConfigSL(ABCConfigSL, ABC):
    """
    基础配置SL管理器 提供了一些实用功能
    """

    @override
    def register_to(self, config_pool: Optional[ABCSLProcessorPool] = None) -> None:
        """
        注册到配置池中

        :param config_pool: 配置池
        :type config_pool: Optional[ABCSLProcessorPool]
        """
        if config_pool is None:
            config_pool = DefaultConfigPool

        super().register_to(config_pool)


class BaseLocalFileConfigSL(BaseConfigSL, ABC):
    """
    基础本地配置文件SL管理器
    """

    _s_open_kwargs: dict[str, Any] = dict(mode='w', encoding="utf-8")
    _l_open_kwargs: dict[str, Any] = dict(mode='r', encoding="utf-8")

    def __init__(
            self,
            s_arg: SLArgument = None,
            l_arg: SLArgument = None,
            *,
            reg_alias: Optional[str] = None,
            create_dir: bool = True
    ):
        # noinspection GrazieInspection
        """
        :param s_arg: 详见 :py:class:`BaseConfigSL`
        :param l_arg: 详见 :py:class:`BaseConfigSL`
        :param reg_alias: 详见 :py:class:`BaseConfigSL`
        :param create_dir: 是否允许创建目录
        :type create_dir: bool

        .. seealso::
           :py:class:`BaseConfigSL`
        """
        super().__init__(s_arg, l_arg, reg_alias=reg_alias)

        self.create_dir = create_dir

    @staticmethod
    def _merge_args(
            base_arguments: tuple[tuple, PMap[str, Any]],
            args: tuple,
            kwargs: dict
    ) -> tuple[tuple, PMap[str, Any]]:
        """
        合并参数

        :param base_arguments: 基础参数
        :type base_arguments: tuple[tuple, PMap[str, Any]]
        :param args: 新参数
        :type args: tuple
        :param kwargs: 新参数
        :type kwargs: dict

        :return: 合并后的参数
        :rtype: tuple[tuple, PMap[str, Any]]
        """
        base_arguments = list(base_arguments[0]), dict(base_arguments[1])

        merged_args = deepcopy(base_arguments[0])[:len(args)] = args
        merged_kwargs = deepcopy(base_arguments[1]) | kwargs

        return tuple(merged_args), pmap(merged_kwargs)

    @contextmanager
    def raises(self, excs: Exception | tuple[Exception, ...] = Exception) -> None:
        """
        包装意料内的异常

        提供给子类的便捷方法

        :param excs: 意料内的异常
        :type excs: Exception | tuple[Exception, ...]

        :raise FailedProcessConfigFileError: 当触发了对应的异常时

        .. versionadded:: 0.1.4
        """
        try:
            yield
        except excs as err:
            raise FailedProcessConfigFileError(err) from err

    @override
    def save(
            self,
            config_file: ABCConfigFile,
            root_path: str,
            namespace: str,
            file_name: str,
            *args, **kwargs
    ) -> None:
        merged_args, merged_kwargs = self._merge_args(self._saver_args, args, kwargs)

        with open(self._process_file_path(root_path, namespace, file_name), **self._s_open_kwargs) as f:
            self.save_file(config_file, f, *merged_args, **merged_kwargs)

    @override
    def load[C: ABCConfigFile](
            self,
            config_file_cls: type[C],
            root_path: str,
            namespace: str,
            file_name: str,
            *args, **kwargs
    ) -> C:
        merged_args, merged_kwargs = self._merge_args(self._loader_args, args, kwargs)

        with open(self._process_file_path(root_path, namespace, file_name), **self._l_open_kwargs) as f:
            return self.load_file(config_file_cls, f, *merged_args, **merged_kwargs)

    @abstractmethod
    def save_file(
            self,
            config_file: ABCConfigFile,
            target_file: SupportsWrite,
            *merged_args,
            **merged_kwargs,
    ) -> None:
        """
        将配置保存到文件

        :param config_file: 配置文件
        :type config_file: ABCConfigFile
        :param target_file: 目标文件对象
        :type target_file: SupportsWrite
        :param merged_args: 合并后的位置参数
        :param merged_kwargs: 合并后的关键字参数

        :raise FailedProcessConfigFileError: 处理配置文件失败
        """

    @abstractmethod
    def load_file[C: ABCConfigFile](
            self,
            config_file_cls: type[C],
            source_file: SupportsReadAndReadline,
            *merged_args,
            **merged_kwargs,
    ) -> C:
        """
        从文件加载配置

        :param config_file_cls: 配置文件类
        :type config_file_cls: type[ABCConfigFile]
        :param source_file: 源文件对象
        :type source_file: _SupportsReadAndReadline
        :param merged_args: 合并后的位置参数
        :param merged_kwargs: 合并后的关键字参数

        :raise FailedProcessConfigFileError: 处理配置文件失败
        """

    def _process_file_path(
            self,
            root_path: str,
            namespace: str,
            file_name: str,
    ) -> str:
        """
        处理配置文件对应的文件路径

        :param root_path: 保存的根目录
        :type root_path: str
        :param namespace: 配置的命名空间
        :type namespace: Optional[str]
        :param file_name: 配置文件名
        :type file_name: Optional[str]

        :return: 配置文件路径
        :rtype: str

        :raise ValueError: 当 ``namespace`` 和 ``file_name`` 都为 None 时
        """

        full_path = os.path.normpath(os.path.join(root_path, namespace, file_name))
        if self.create_dir:
            os.makedirs(os.path.dirname(full_path), exist_ok=True)

        return full_path


__all__ = (
    "RequiredPath",
    "ConfigPool",
    "RequireConfigDecorator",
    "BaseConfigSL",
    "BaseLocalFileConfigSL",

    "DefaultConfigPool",
    "requireConfig",
    "saveAll",
    "get",
    "set_",
    "save",
    "load",
)
