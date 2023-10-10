"""Provides a `TidiRegistry`, responsible for providing stored dependencies."""

import builtins
import threading
import typing as t

T = t.TypeVar("T")


class _Unknown:
    ...  # pragma: no cover


_unknown = _Unknown()


class RegistrationError(TypeError):
    """Error finding desired type in registry"""


class RegistryLookupError(LookupError):
    """Error finding desired type in registry"""


class _Container(t.Protocol):
    def add(self, obj: T):
        ...  # pragma: no cover

    def get(self, type_: t.Type[T], default: T | None = None) -> T:
        ...  # pragma: no cover


class _PerThreadContainer(threading.local):
    def __init__(self):
        self._map = {}

    def add(self, obj: T):
        self._map[type(obj)] = obj

    def get(self, type_: t.Type[T], default: T | None = None) -> T:
        return self._map.get(type_, default)


class TidiRegistry:
    """A simple registry of objects indexed by their type."""

    def __init__(
        self,
        banned_types: list[t.Type] | None = None,
        container_cls: t.Type[_Container] = _PerThreadContainer,
    ):
        if banned_types is None:
            banned_types = [
                type_ for type_ in builtins.__dict__.values() if isinstance(type_, type)
            ]
        self.banned_types = banned_types
        self._container = container_cls()

    def register(self, obj: t.Any):
        """Register an instance `obj` of class `T` to be available for injection.

        Args:
            obj (typing.Any): The instance to register

        Raises:
            RegistrationError: if trying to register a banned type (a builtin type by default).
        """
        type_ = type(obj)
        if type_ in self.banned_types:
            raise RegistrationError(f"Trying to register a banned type: {type_}")
        self._container.add(obj)

    def get(self, type_: t.Type[T], default: t.Any = _unknown) -> T:
        """Get an instance of type `type_` from the regsitry.

        Args:
            type_ (t.Type[T]): The type of the dependency being looked for.
            default (t.Any, optional): An optional default return value.

        Raises:
            RegistryLookupError: if the instance hasn't been registered and a
                default hasn't been provided.

        Returns:
            (type_ (T)): the registered object, or default value if it was provided.
        """
        obj = self._container.get(type_, default)
        if isinstance(obj, _Unknown):
            raise RegistryLookupError(f"Type has not been registered: {type_}")
        return obj
