"""Provides a decorator that injects the dependencies"""

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
    """Placeholder object for a dependency yet to be injected."""


UNSET = Unset()


class Provider(t.Generic[T], t.Any):  # inherit from Any to appease type checkers
    # overloading new to avoid issue with the `Any` inheritance
    @classmethod
    def __new__(cls, *args, **kwargs) -> t.Self:
        return super().__new__(cls)

    def __init__(self, provider_func: t.Callable[..., T]):
        self.provider_func = provider_func


def inject(registry: Registry | None = None) -> t.Callable[[t.Callable[P, R]], t.Callable[P, R]]:
    """Inject dependencies as kwargs when they haven't been set."""

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
