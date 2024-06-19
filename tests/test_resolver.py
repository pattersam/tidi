import contextlib
import typing as t

import pytest
import pytest_mock

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


def provide_dep_func() -> Dep:
    return PROVIDED_DEP


@contextlib.contextmanager
def provide_dep_from_context_manager() -> t.Iterator[Dep]:
    yield PROVIDED_DEP


class ProviderContextManager:
    def __enter__(self):
        return PROVIDED_DEP

    def __exit__(self, *_):
        ...


def test_resolve_dependency_from_registry_no_init():
    # `case ResolverOptions(use_registry=True, initialise_missing=False) if registry is not None`
    assert (
        resolver.resolve_dependency(
            Dep,
            resolver.ResolverOptions(use_registry=True, initialise_missing=False),
            registry=Registry(REGISTERED_DEP),
        ).__enter__()
        == REGISTERED_DEP
    )


def test_resolve_dependency_from_registry_no_init_without_registry_fails():
    # `case ResolverOptions(use_registry=True, initialise_missing=False) if registry is None`
    with pytest.raises(resolver.DependencyResolutionError):
        resolver.resolve_dependency(
            Dep,
            resolver.ResolverOptions(use_registry=True, initialise_missing=False),
            registry=None,
        ).__enter__()


def test_resolve_dependency_from_registry_or_init_with_dep_in_registry():
    # `case ResolverOptions(use_registry=True, initialise_missing=True) if registry is not None`
    assert (
        resolver.resolve_dependency(
            Dep,
            resolver.ResolverOptions(use_registry=True, initialise_missing=True),
            registry=Registry(REGISTERED_DEP),
        ).__enter__()
        == REGISTERED_DEP
    )


def test_resolve_dependency_from_registry_or_init_without_dep_in_registry():
    # `case ResolverOptions(use_registry=True, initialise_missing=True) if registry is not None`
    resolved_dep = resolver.resolve_dependency(
        Dep,
        resolver.ResolverOptions(use_registry=True, initialise_missing=True),
        registry=Registry(None),
    ).__enter__()
    assert resolved_dep != REGISTERED_DEP
    assert isinstance(resolved_dep, Dep)


def test_resolve_dependency_from_registry_or_init_without_dep_in_registry_from_provider_function():
    # `case ResolverOptions(use_registry=True, initialise_missing=True) if registry is not None`
    resolved_dep = resolver.resolve_dependency(
        Dep,
        resolver.ResolverOptions(use_registry=True, initialise_missing=True),
        registry=Registry(None),
        provider=provide_dep_func,
    ).__enter__()
    assert resolved_dep == PROVIDED_DEP


def test_resolve_dependency_from_registry_or_init_without_dep_in_registry_from_provider_context_manager_decorator():
    # `case ResolverOptions(use_registry=True, initialise_missing=True) if registry is not None`
    resolved_dep = resolver.resolve_dependency(
        Dep,
        resolver.ResolverOptions(use_registry=True, initialise_missing=True),
        registry=Registry(None),
        provider=provide_dep_from_context_manager,
    ).__enter__()
    assert resolved_dep == PROVIDED_DEP


def test_resolve_dependency_from_registry_or_init_without_dep_in_registry_from_provider_context_manager_class(
    mocker: pytest_mock.MockerFixture,
):
    # `case ResolverOptions(use_registry=True, initialise_missing=True) if registry is not None`
    mock_exit = mocker.patch.object(ProviderContextManager, "__exit__")
    with resolver.resolve_dependency(
        Dep,
        resolver.ResolverOptions(use_registry=True, initialise_missing=True),
        registry=Registry(None),
        provider=ProviderContextManager,
    ) as resolved_dep:
        assert resolved_dep == PROVIDED_DEP
        mock_exit.assert_not_called()
    mock_exit.assert_called_once()


def test_resolve_dependency_from_registry_or_init_without_dep_in_registry_unable_to_create():
    # `case ResolverOptions(use_registry=True, initialise_missing=True) if registry is not None`
    with pytest.raises(resolver.DependencyResolutionError):
        resolver.resolve_dependency(
            DepWithArgs,
            resolver.ResolverOptions(use_registry=True, initialise_missing=True),
            registry=Registry(None),
        ).__enter__()


def test_resolve_dependency_init_only():
    # `case case ResolverOptions(initialise_missing=True) if registry is None`
    resolved_dep = resolver.resolve_dependency(
        Dep,
        resolver.ResolverOptions(use_registry=False, initialise_missing=True),
    ).__enter__()
    assert resolved_dep != REGISTERED_DEP
    assert isinstance(resolved_dep, Dep)


def test_resolve_dependency_init_only_from_provider_function():
    # `case case ResolverOptions(initialise_missing=True) if registry is None`
    resolved_dep = resolver.resolve_dependency(
        Dep,
        resolver.ResolverOptions(use_registry=False, initialise_missing=True),
        provider=provide_dep_func,
    ).__enter__()
    assert resolved_dep == PROVIDED_DEP


def test_resolve_dependency_init_only_from_provider_context_manager_decorator():
    # `case case ResolverOptions(initialise_missing=True) if registry is None`
    resolved_dep = resolver.resolve_dependency(
        Dep,
        resolver.ResolverOptions(use_registry=False, initialise_missing=True),
        provider=provide_dep_from_context_manager,
    ).__enter__()
    assert resolved_dep == PROVIDED_DEP


def test_resolve_dependency_init_only_from_provider_context_manager_class(
    mocker: pytest_mock.MockerFixture,
):
    # `case ResolverOptions(use_registry=True, initialise_missing=True) if registry is not None`
    mock_exit = mocker.patch.object(ProviderContextManager, "__exit__")
    with resolver.resolve_dependency(
        Dep,
        resolver.ResolverOptions(use_registry=True, initialise_missing=True),
        registry=Registry(None),
        provider=ProviderContextManager,
    ) as resolved_dep:
        assert resolved_dep == PROVIDED_DEP
        mock_exit.assert_not_called()
    mock_exit.assert_called_once()


def test_resolve_dependency_init_only_unable_to_create():
    # `case ResolverOptions(use_registry=True, initialise_missing=True) if registry is not None`
    with pytest.raises(resolver.DependencyResolutionError):
        resolver.resolve_dependency(
            DepWithArgs,
            resolver.ResolverOptions(use_registry=False, initialise_missing=True),
        ).__enter__()


def test_resolve_dependency_unhandled_pattern():
    with pytest.raises(resolver.DependencyResolutionError):
        resolver.resolve_dependency(
            type_=DepWithArgs,
            resolver_options=None,
        ).__enter__()
