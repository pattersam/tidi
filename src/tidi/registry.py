"""Provides the main `Tidi` class, housing the dependency registry and @inject decorator"""

import builtins
import typing as t

T = t.TypeVar("T")


class _Unknown:
    """Sentinal class / objected used to represent no default selection."""


_unknown = _Unknown()


class RegistrationError(TypeError):
    """Error finding desired type in registry"""


class RegistryLookupError(LookupError):
    """Error finding desired type in registry"""


class TidiRegistry:
    """A simple registry of objects indexed by their type."""

    def __init__(self, banned_types: list[t.Type] | None = None):
        if banned_types is None:
            banned_types = [
                type_ for type_ in builtins.__dict__.values() if isinstance(type_, type)
            ]
        self.banned_types = banned_types
        self._registry: dict = {}

    def register(self, obj: t.Any):
        """Register an instance `obj` of class `T` to be available for injection."""
        type_ = type(obj)
        if type_ in self.banned_types:
            raise RegistrationError(f"Trying to register a banned type: {type_}")
        self._registry[type_] = obj

    def get(self, type_: t.Type[T], default: t.Any = _unknown) -> T:
        """Get an object from the regsitry, optionally try to instantiate it if it isn't registered."""
        obj = self._registry.get(type_, default)
        if isinstance(obj, _Unknown):
            raise RegistryLookupError(f"Type has not been registered: {type_}")
        return obj
