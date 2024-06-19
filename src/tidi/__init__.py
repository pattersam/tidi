"""A tiny dependecy injection library."""
import typing as t

from tidi import decorator, registry, resolver

__version__ = "0.2.0"

T = t.TypeVar("T")


Unset = decorator.Unset
UNSET = decorator.UNSET
Provider = decorator.Provider
DEFAULT_RESOLVER_OPTIONS = resolver.ResolverOptions(use_registry=True, initialise_missing=True)

Injected = t.Annotated[T | Unset | Provider, DEFAULT_RESOLVER_OPTIONS]


default_tidi_registry = registry.TidiRegistry()
register = default_tidi_registry.register
inject = decorator.inject(registry=default_tidi_registry)


def field_factory(
    type_: t.Type[T], provider: t.Callable[..., T] | None = None
) -> t.Callable[..., T]:
    def inner():
        with resolver.resolve_dependency(
            type_=type_,
            resolver_options=DEFAULT_RESOLVER_OPTIONS,
            registry=default_tidi_registry,
            provider=provider,
        ) as obj:
            return obj

    return inner
