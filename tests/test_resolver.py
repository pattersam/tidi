import typing as t

import pytest

from tidi import resolver

T = t.TypeVar("T")


class Dep:
    def __init__(self) -> None:
        self.hello = "world"


class DepWithArgs:
    def __init__(self, arg: str) -> None:
        self.arg = arg


REGISTERED_DEP = Dep()
PROVIDED_DEP = Dep()


class Registry:
    def __init__(self, dep):
        self.dep = dep

    def get(self, type_: t.Type[T], default: t.Any = ...) -> T:
        return self.dep


def provide_dep():
    return PROVIDED_DEP


def test_resolve_dependency_from_registry_no_init():
    # `case ResolverOptions(use_registry=True, initialise_missing=False) if registry is not None`
    assert (
        resolver.resolve_dependency(
            Dep,
            resolver.ResolverOptions(use_registry=True, initialise_missing=False),
            registry=Registry(REGISTERED_DEP),
        )
        == REGISTERED_DEP
    )


def test_resolve_dependency_from_registry_no_init_without_registry_fails():
    # `case ResolverOptions(use_registry=True, initialise_missing=False) if registry is None`
    with pytest.raises(resolver.DependencyResolutionError):
        resolver.resolve_dependency(
            Dep,
            resolver.ResolverOptions(use_registry=True, initialise_missing=False),
            registry=None,
        )


def test_resolve_dependency_from_registry_or_init_with_dep_in_registry():
    # `case ResolverOptions(use_registry=True, initialise_missing=True) if registry is not None`
    assert (
        resolver.resolve_dependency(
            Dep,
            resolver.ResolverOptions(use_registry=True, initialise_missing=True),
            registry=Registry(REGISTERED_DEP),
        )
        == REGISTERED_DEP
    )


def test_resolve_dependency_from_registry_or_init_without_dep_in_registry():
    # `case ResolverOptions(use_registry=True, initialise_missing=True) if registry is not None`
    resolved_dep = resolver.resolve_dependency(
        Dep,
        resolver.ResolverOptions(use_registry=True, initialise_missing=True),
        registry=Registry(None),
    )
    assert resolved_dep != REGISTERED_DEP
    assert isinstance(resolved_dep, Dep)


def test_resolve_dependency_from_registry_or_init_without_dep_in_registry_from_provider():
    # `case ResolverOptions(use_registry=True, initialise_missing=True) if registry is not None`
    resolved_dep = resolver.resolve_dependency(
        Dep,
        resolver.ResolverOptions(use_registry=True, initialise_missing=True),
        registry=Registry(None),
        provider=provide_dep,
    )
    assert resolved_dep == PROVIDED_DEP


def test_resolve_dependency_from_registry_or_init_without_dep_in_registry_unable_to_create():
    # `case ResolverOptions(use_registry=True, initialise_missing=True) if registry is not None`
    with pytest.raises(TypeError):
        resolver.resolve_dependency(
            DepWithArgs,
            resolver.ResolverOptions(use_registry=True, initialise_missing=True),
            registry=Registry(None),
        )


def test_resolve_dependency_init_only():
    # `case case ResolverOptions(initialise_missing=True) if registry is None`
    resolved_dep = resolver.resolve_dependency(
        Dep,
        resolver.ResolverOptions(use_registry=False, initialise_missing=True),
    )
    assert resolved_dep != REGISTERED_DEP
    assert isinstance(resolved_dep, Dep)


def test_resolve_dependency_init_only_from_provider():
    # `case case ResolverOptions(initialise_missing=True) if registry is None`
    resolved_dep = resolver.resolve_dependency(
        Dep,
        resolver.ResolverOptions(use_registry=False, initialise_missing=True),
        provider=provide_dep,
    )
    assert resolved_dep == PROVIDED_DEP


def test_resolve_dependency_init_only_unable_to_create():
    # `case ResolverOptions(use_registry=True, initialise_missing=True) if registry is not None`
    with pytest.raises(TypeError):
        resolver.resolve_dependency(
            DepWithArgs,
            resolver.ResolverOptions(use_registry=False, initialise_missing=True),
        )


def test_resolve_dependency_unhandled_pattern():
    with pytest.raises(resolver.DependencyResolutionError):
        resolver.resolve_dependency(
            type_=DepWithArgs,
            resolver_options=None,
        )
