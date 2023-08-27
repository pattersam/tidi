import typing as t
from unittest import mock

import pytest
import pytest_mock

from tidi import decorator

T = t.TypeVar("T")


class Dep:
    def __init__(self) -> None:
        self.value = "world"


TEST_DEP = Dep()


class Registry:
    def get(self, type_: t.Type[T], default: t.Any = ...) -> T:
        raise NotImplementedError()


class FakeResolverOptions:
    ...


@pytest.fixture
def mock_resolver(mocker: pytest_mock.MockerFixture) -> t.Callable:
    mock_resolver = mocker.patch("tidi.resolver.resolve_dependency")
    mock_resolver.return_value = TEST_DEP
    return mock_resolver


@mock.patch("tidi.resolver.ResolverOptions", FakeResolverOptions)
def test_inject_func_retains_properties(mock_resolver):
    @decorator.inject(registry=None)
    def original_func_name(
        arg_1: str,
        kwarg_1: t.Annotated[Dep | decorator.Unset, FakeResolverOptions()] = decorator.UNSET,
    ):
        """original docstring"""
        return f"{arg_1} {kwarg_1.value}"

    assert original_func_name.__name__ == "original_func_name"
    assert original_func_name.__doc__ == "original docstring"


@mock.patch("tidi.resolver.ResolverOptions", FakeResolverOptions)
def test_inject_func_without_registry(mock_resolver):
    @decorator.inject(registry=None)
    def injectable_func(
        arg_1: str,
        kwarg_1: t.Annotated[Dep | decorator.Unset, FakeResolverOptions()] = decorator.UNSET,
    ):
        return f"{arg_1} {kwarg_1.value}"

    response = injectable_func("hello")
    assert response == "hello world"


@mock.patch("tidi.resolver.ResolverOptions", FakeResolverOptions)
def test_inject_func_with_registry(mock_resolver):
    @decorator.inject(registry=Registry())
    def injectable_func(
        arg_1: str,
        kwarg_1: t.Annotated[Dep | decorator.Unset, FakeResolverOptions()] = decorator.UNSET,
    ):
        return f"{arg_1} {kwarg_1.value}"

    response = injectable_func("hello")
    assert response == "hello world"


def test_invalid_annotation_doesnt_get_injected(mock_resolver):
    @decorator.inject()
    def injectable_func(
        arg_1: str, kwarg_1: t.Annotated[Dep | decorator.Unset, object()] = decorator.UNSET
    ):
        return f"{arg_1} {kwarg_1.value}"

    with pytest.raises(AttributeError):
        injectable_func("hello")


@mock.patch("tidi.resolver.ResolverOptions", FakeResolverOptions)
def test_non_kwarg_doesnt_get_injected(mock_resolver):
    @decorator.inject()
    def injectable_func(arg_1: t.Annotated[Dep | decorator.Unset, FakeResolverOptions()]):
        assert not isinstance(arg_1, Dep)
        return f"{arg_1}"

    response = injectable_func("hello")
    assert response == "hello"


@mock.patch("tidi.resolver.ResolverOptions", FakeResolverOptions)
def test_inject_class_constructor(mock_resolver):
    @decorator.inject()
    class UnitTest:
        def __init__(
            self,
            kwarg_1: t.Annotated[Dep | decorator.Unset, FakeResolverOptions()] = decorator.UNSET,
        ):
            self.value = kwarg_1

    obj = UnitTest()
    assert obj.value.value == "world"


@mock.patch("tidi.resolver.ResolverOptions", FakeResolverOptions)
def test_inject_class___init___method(mock_resolver):
    class UnitTest:
        @decorator.inject()
        def __init__(
            self,
            kwarg_1: t.Annotated[Dep | decorator.Unset, FakeResolverOptions()] = decorator.UNSET,
        ):
            self.value = kwarg_1

    obj = UnitTest()
    assert obj.value.value == "world"
