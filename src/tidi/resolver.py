"""Finds or creates dependency instances based on availability and options."""

import contextlib
import typing as t
from dataclasses import dataclass

T = t.TypeVar("T")


class Registry(t.Protocol):
    def get(self, type_: t.Type[T], default: t.Any = ...) -> T:
        ...  # pragma: no cover


class DependencyResolutionError(Exception):
    """Unable to resolve dependency"""


@dataclass(frozen=True)
class ResolverOptions:
    """Options that control how resolving is done.

    Args:
        use_registry (bool): whether to try using the registry or not.
        initialise_missing (bool): whether to try to initialise the dependency or not.

    """

    use_registry: bool
    initialise_missing: bool


@contextlib.contextmanager
def resolve_dependency(
    type_: t.Type[T],
    resolver_options: ResolverOptions,
    registry: Registry | None = None,
    provider: t.Callable[..., T]
    | t.Callable[..., contextlib.AbstractContextManager[T]]
    | None = None,
) -> t.Iterator[T]:
    """Returns a dependency according to configured options.

    Args:
        type_ (typing.Type[T]): the type of the dependency being looked for.
        resolver_options (ResolverOptions): options dictating how to resolve
            the dependency.
        registry (Registry | None, optional): an optional registry containing
            the dependency. Defaults to None.
        provider: (t.Callable[..., T] | typing.Callable[..., contextlib.AbstractContextManager[T]] | None):
            an optional context manager function that returns the dependency.
            Defaults to None.

    Raises:
        DependencyResolutionError: if a registry is required but not provided
        DependencyResolutionError: if the function doesn't know how to handle the situation

    Returns:
        (type requested (T)): an instance of the dependency requested.
    """
    match resolver_options:
        case ResolverOptions(use_registry=True, initialise_missing=False) if registry is not None:
            yield registry.get(type_)
        case ResolverOptions(use_registry=True, initialise_missing=False) if registry is None:
            raise DependencyResolutionError("Registry required but not provided.")
        case ResolverOptions(use_registry=True, initialise_missing=True) if registry is not None:
            obj = registry.get(type_, None)
            if obj is not None:
                yield obj
            else:
                yield from _initialise_dependency(type_, provider)
        case ResolverOptions(initialise_missing=True) if registry is None:
            yield from _initialise_dependency(type_, provider)
        case _:
            raise DependencyResolutionError("Unable to resolve dependency.")


def _initialise_dependency(
    type_: t.Type[T],
    provider: t.Callable[..., contextlib.AbstractContextManager[T]] | t.Callable[..., T] | None,
) -> t.Iterator[T]:
    if provider is None:
        yield _new_dependency(type_)
        return
    maybe_a_context_manager = provider()
    match maybe_a_context_manager:
        case contextlib.AbstractContextManager() as context_manager:
            with context_manager as obj:
                yield obj
        case obj:
            yield obj


def _new_dependency(type_: t.Type[T]) -> T:
    try:
        return type_()
    except TypeError as err:
        raise DependencyResolutionError(f"Unable to instantiate {type_}") from err
