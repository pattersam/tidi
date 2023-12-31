from dataclasses import dataclass, field

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


def test_injecting_into_func_from_initialised_class():
    class ClassDependency:
        def __init__(self, value: str = "class world"):
            self.value = value

    @tidi.inject
    def my_func(a: str, b: tidi.Injected[ClassDependency] = tidi.UNSET) -> str:
        return f"{a} {b.value}"

    assert my_func("hello") == "hello class world"
