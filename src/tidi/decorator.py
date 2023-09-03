"""Provides the main `inject` decorator.

Uses `tidi.parameters` to determine which parameters of the wrapped function to
replace.
"""

import functools
import inspect
import typing as t

from tidi import parameters, resolver

T = t.TypeVar("T")
R = t.TypeVar("R")
P = t.ParamSpec("P")


class Registry(t.Protocol):
    def get(self, type_: t.Type[T], default: t.Any = ...) -> T:
        ...  # pragma: no cover


class Unset(t.Any):
    """Placeholder class for a dependency yet to be injected."""


UNSET = Unset()
"""Sentinel `Unset` object used to indicate a kwarg is not set yet."""


class Provider(t.Generic[T], t.Any):  # inherit from Any to appease type checkers
    """Wrapper class around a function that will be called to provide a dependency

    Args:
        provider_func (typing.Callable): Callable that will return a given
            type (TypeVar `T`) which will be used as the dependency.

    Examples:
        Define a provider function
        >>> def get_big_toolbox() -> Toolbox:
        >>>     return ...

        Give the provider function into the kwarg marked for injected
        >>> @tidi.inject
        ... def get_hammers(
        ...     toolbox: tidi.Injected[Toolbox] = tidi.Provider(get_big_toolbox)
        ... ) -> list[Hammer]:
        ...     return [tool for tool in toolbox.tools if isinstance(tool, Hammer)]

        Now when you call `get_hammers`, Tidi will call `get_big_toolbox` and
        inject it into the `toolbox` kwarg
        >>> get_hammers()
    """

    # overloading new to avoid issue with the `Any` inheritance
    @classmethod
    def __new__(cls, *args, **kwargs) -> t.Self:
        return super().__new__(cls)

    def __init__(self, provider_func: t.Callable[..., T]):
        self.provider_func = provider_func


def inject(registry: Registry | None = None) -> t.Callable[[t.Callable[P, R]], t.Callable[P, R]]:
    """A decorator that will replace certain keyword arguments with dependencies

    Args:
        registry (Registry | None, optional): Provide a `tidi.registry.Registry`
            if you have one. Defaults to None.

    Returns:
        (t.Callable[[t.Callable[P, R]], t.Callable[P, R]]): The decorator itself.

    Examples:
        Define your own inject decorator if you don't want to use the top level
        package defined one.
        >>> # note: `new_injector` doesn't have a registry, which can be useful
        >>> new_injector = tidi.decorator.inject()

        Use the decorator just like the main one (`tidi.inject`)
        >>> @new_injector
        >>> def create_db_connection(
        ...    db_string: tidi.Injected = tidi.Provider(get_db_conn_string)
        ... ) -> db_library.DBConn:
        ...     return db_library.connect(db_string)
    """

    def decorator(func: t.Callable[P, R]) -> t.Callable[P, R]:
        injectable_params = _get_injectable_parameters_from_func_signature(func)

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            for param in injectable_params:
                obj = resolver.resolve_dependency(
                    type_=param.base_type,
                    resolver_options=next(metadata for metadata in param.annotated_metadata),
                    registry=registry,
                    provider=param.default.provider_func
                    if isinstance(param.default, Provider)
                    else None,
                )
                kwargs.setdefault(param.name, obj)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def _get_injectable_parameters_from_func_signature(
    func: t.Callable,
) -> parameters.AnnotatedParameters:
    return parameters.AnnotatedParameters(
        param
        for param in parameters.AnnotatedParameters.from_func(func)
        if _is_injectable_param(param)
    )


def _is_injectable_param(param: parameters.AnnotatedParameter) -> bool:
    return _is_keyword_arg_parameter(param) and _has_resolver_options_annotation(param)


def _is_keyword_arg_parameter(param: inspect.Parameter) -> bool:
    return (
        param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
        and param.default != inspect.Parameter.empty
    )


def _has_resolver_options_annotation(param: parameters.AnnotatedParameter) -> bool:
    return any(
        isinstance(metadata, resolver.ResolverOptions) for metadata in param.annotated_metadata
    )
