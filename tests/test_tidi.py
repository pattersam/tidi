import contextlib
import typing as t
from dataclasses import dataclass, field

import pytest

import tidi


def test_injecting_into_func():
    class FuncParamDependency(str):
        ...

    dependecy = FuncParamDependency("world")

    @tidi.inject
    def my_func(a: str, b: tidi.Injected[FuncParamDependency] = tidi.UNSET) -> str:
        return f"{a} {b}"

    tidi.register(dependecy)

    assert my_func("hello") == "hello world"


def test_injecting_into_class():
    class ClassParameterDependency(str):
        ...

    dependecy = ClassParameterDependency("world")

    @tidi.inject
    class MyClass:
        def __init__(self, a: str, b: tidi.Injected[ClassParameterDependency] = tidi.UNSET):
            self.output = f"{a} {b}"

    tidi.register(dependecy)

    assert MyClass("hello").output == "hello world"


def test_injecting_into_class_init():
    class ClassInitParameterDependency(str):
        ...

    dependecy = ClassInitParameterDependency("world")

    class MyClass:
        @tidi.inject
        def __init__(self, a: str, b: tidi.Injected[ClassInitParameterDependency] = tidi.UNSET):
            self.output = f"{a} {b}"

    tidi.register(dependecy)

    assert MyClass("hello").output == "hello world"


def test_injecting_into_dataclass_field():
    class DataClassFiledDependency(str):
        ...

    dependecy = DataClassFiledDependency("world")

    @dataclass
    class MyDataClass:
        a: str
        b: str = field(default_factory=tidi.field_factory(DataClassFiledDependency))

        @property
        def output(self) -> str:
            return f"{self.a} {self.b}"

    tidi.register(dependecy)

    assert MyDataClass("hello").output == "hello world"


def test_injecting_into_func_from_func():
    class LoadedDependency(str):
        ...

    def load_dependency() -> LoadedDependency:
        return LoadedDependency("loaded world")

    @tidi.inject
    def my_func(a: str, b: tidi.Injected[LoadedDependency] = tidi.Provider(load_dependency)) -> str:
        return f"{a} {b}"

    assert my_func("hello") == "hello loaded world"


def test_injecting_into_func_from_decorator_context_manager():
    class LoadedDependency(str):
        ...

    mutatable_var = {"state": "before_entering_context"}

    @contextlib.contextmanager
    def dependency_ctx_mgr(mutatable_arg: dict = mutatable_var) -> t.Iterator[LoadedDependency]:
        mutatable_arg["state"] = "after_entering_context"
        yield LoadedDependency("loaded world")
        mutatable_arg["state"] = "after_exiting_context"

    @tidi.inject
    def my_func(
        a: str, b: tidi.Injected[LoadedDependency] = tidi.Provider(dependency_ctx_mgr)
    ) -> str:
        assert mutatable_var["state"] == "after_entering_context"
        return f"{a} {b}"

    assert mutatable_var["state"] == "before_entering_context"
    assert my_func("hello") == "hello loaded world"
    assert mutatable_var["state"] == "after_exiting_context"


def test_injecting_into_func_from_class_context_manager():
    class LoadedDependency(str):
        ...

    class DependencyContextManager:
        class_var = "before_enter"

        @classmethod
        def __enter__(cls):
            cls.class_var = "after_enter_and_before_exit"
            return LoadedDependency("loaded world")

        @classmethod
        def __exit__(cls, *_):
            cls.class_var = "after_exit"

    @tidi.inject
    def my_func(
        a: str, b: tidi.Injected[LoadedDependency] = tidi.Provider(DependencyContextManager)
    ) -> str:
        assert DependencyContextManager.class_var == "after_enter_and_before_exit"
        return f"{a} {b}"

    assert DependencyContextManager.class_var == "before_enter"
    assert my_func("hello") == "hello loaded world"
    assert DependencyContextManager.class_var == "after_exit"


def test_injecting_into_func_from_initialised_class():
    class ClassDependency:
        def __init__(self, value: str = "class world"):
            self.value = value

    @tidi.inject
    def my_func(a: str, b: tidi.Injected[ClassDependency] = tidi.UNSET) -> str:
        return f"{a} {b.value}"

    assert my_func("hello") == "hello class world"


def test_injecting_into_func_from_subclass():
    class ParentClassDependency:
        def __init__(self, value: str):
            self.value = f"{value} parent"

    class ChildClassDependency:
        def __init__(self, value: str):
            self.value = f"{value} child"

    @tidi.inject
    def my_func(a: str, b: tidi.Injected[ParentClassDependency] = tidi.UNSET) -> str:
        return f"{b.value} {a}"

    dependency = ChildClassDependency("hello")
    tidi.register(dependency, type_=ParentClassDependency)

    assert my_func("👋") == "hello child 👋"


def test_injecting_into_func_from_subclass_doesnt_work_when_type_kwarg_not_specified():
    class ParentClassDependency:
        def __init__(self):
            self.value = "hello parent"

    class ChildClassDependency:
        def __init__(self):
            self.value = "hello child"

    @tidi.inject
    def my_func(a: str, b: tidi.Injected[ParentClassDependency] = tidi.UNSET) -> str:
        return f"{b.value} {a}"

    dependency = ChildClassDependency()
    tidi.register(dependency)

    assert my_func("👋") != "hello child 👋"
    assert my_func("👋") == "hello parent 👋"


def test_injecting_into_func_from_subclass_fails_when_not_specified():
    class ParentClassDependency:
        def __init__(self, value: str):
            self.value = f"{value} parent"

    class ChildClassDependency:
        def __init__(self, value: str):
            self.value = f"{value} child"

    @tidi.inject
    def my_func(a: str, b: tidi.Injected[ParentClassDependency] = tidi.UNSET) -> str:
        return f"{b.value} {a}"

    dependency = ChildClassDependency("hello")
    tidi.register(dependency)

    with pytest.raises(tidi.resolver.DependencyResolutionError):
        my_func("👋")
