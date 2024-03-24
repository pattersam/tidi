import typing as t
from dataclasses import dataclass

import pytest

from tidi import registry


@pytest.fixture
def tidi_registry() -> registry.TidiRegistry:
    return registry.TidiRegistry()


def test_register_normal_class(tidi_registry: registry.TidiRegistry):
    class TestClass:
        def __init__(self, hello: str) -> None:
            self.hello = hello

    obj = TestClass("world")
    tidi_registry.register(obj)
    assert tidi_registry.get(TestClass) == obj
    assert tidi_registry.get(TestClass).hello == "world"


def test_register_dataclass(tidi_registry: registry.TidiRegistry):
    @dataclass
    class TestDataClass:
        field: int
        default_field: int = 2

    obj = TestDataClass(1)
    tidi_registry.register(obj)
    assert tidi_registry.get(TestDataClass) == obj
    assert tidi_registry.get(TestDataClass).field == 1
    assert tidi_registry.get(TestDataClass).default_field == 2


def test_register_inheritted_class_without_specifying_type_key_fails(
    tidi_registry: registry.TidiRegistry,
):
    class ParentClass:
        ...

    class ChildClass(ParentClass):
        ...

    obj = ChildClass()
    tidi_registry.register(obj)
    with pytest.raises(registry.RegistryLookupError):
        tidi_registry.get(ParentClass)


def test_register_inheritted_class_with_specifying_type_key_fails(
    tidi_registry: registry.TidiRegistry,
):
    class ParentClass:
        ...

    class ChildClass(ParentClass):
        ...

    obj = ChildClass()
    tidi_registry.register(obj, type_=ParentClass)
    assert tidi_registry.get(ParentClass) == obj


def test_register_str_subclass(tidi_registry: registry.TidiRegistry):
    class MyString(str):
        ...

    obj = MyString("unit test")
    tidi_registry.register(obj)
    assert tidi_registry.get(MyString) == obj


def test_register_builtin_str(tidi_registry: registry.TidiRegistry):
    obj = "unit test"
    with pytest.raises(registry.RegistrationError):
        tidi_registry.register(obj)


def test_register_str_alias(tidi_registry: registry.TidiRegistry):
    MyString = str
    obj = MyString("unit test")
    with pytest.raises(registry.RegistrationError):
        tidi_registry.register(obj)


def test_register_str_new_type(tidi_registry: registry.TidiRegistry):
    MyString = t.NewType("MyString", str)
    obj = MyString("unit test")
    with pytest.raises(registry.RegistrationError):
        tidi_registry.register(obj)


def test_get_missing_type_without_default_error(tidi_registry: registry.TidiRegistry):
    with pytest.raises(LookupError):
        tidi_registry.get(int)


def test_get_missing_type_with_default_of_same_type(tidi_registry: registry.TidiRegistry):
    assert tidi_registry.get(int, 12345) == 12345


def test_get_missing_type_with_None_default(tidi_registry: registry.TidiRegistry):
    assert tidi_registry.get(int, None) is None
