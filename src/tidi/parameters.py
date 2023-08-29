"""Extends functionality of `inspect.Parameter` to help work with `typing.Annotated` function parameters."""

import inspect
import types
import typing as t


class AnnotatedParameter(inspect.Parameter):
    """Subclass of `inspect.Parameter` aimed for parameters with `typing.Annotated` type.

    Has extra properties that are useful when the type hint is `typing.Annotated`.
    """

    def __init__(
        self,
        name: str,
        kind: inspect._ParameterKind,
        *,
        default: t.Any = ...,
        annotation: t.Any = ...,
    ) -> None:
        super().__init__(name, kind, default=default, annotation=annotation)

    @classmethod
    def from_parameter(cls, parameter: inspect.Parameter) -> t.Self:
        """Builds a `AnnotatedParameter` from a normal `inspect.Parameter`

        Args:
            parameter (inspect.Parameter): The normal `inspect.Parameter` to build from

        Returns:
            (AnnotatedParameter): the new `AnnotatedParameter` instance
        """
        return cls(
            name=parameter.name,
            kind=parameter.kind,
            default=parameter.default,
            annotation=parameter.annotation,
        )

    @property
    def is_annotated_type(self) -> bool:
        """`True` if the origin type hint is `typing.Annotated`, otherwise `False`."""
        return t.get_origin(self.annotation) is t.Annotated

    @property
    def base_type(self) -> t.Type:  # type: ignore
        """The _real_ type of the `typing.Annotated` parameter."""
        assert self.is_annotated_type
        match t.get_args(self.annotation)[0]:
            case union if t.get_origin(union) in (t.Union, types.UnionType):
                return t.get_args(union)[0]
            case base_type:
                return base_type

    @property
    def annotated_metadata(self) -> tuple:
        """A tuple of the extra annotations added via the `typing.Annotated` hint."""
        assert self.is_annotated_type
        return t.get_args(self.annotation)[1:]


class AnnotatedParameters(list[AnnotatedParameter]):
    """A list of `AnnotatedParameter` instances."""

    def __init__(self, values: t.Iterable):
        super().__init__(values)

    @classmethod
    def from_func(cls, func: t.Callable) -> t.Self:
        """Builds `AnnotatedParameters` by inspecting a function's signature."""
        return cls(
            ann_param
            for param in inspect.signature(func).parameters.values()
            if (ann_param := AnnotatedParameter.from_parameter(param)).is_annotated_type
        )
