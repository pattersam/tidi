"""Wraps `inspect.Parameter` to help working with `typing.Annotated` function parameters."""

import inspect
import types
import typing as t


class AnnotatedParameter(inspect.Parameter):
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
        return cls(
            name=parameter.name,
            kind=parameter.kind,
            default=parameter.default,
            annotation=parameter.annotation,
        )

    @property
    def is_annotated_type(self) -> bool:
        return t.get_origin(self.annotation) is t.Annotated

    @property
    def base_type(self) -> t.Type:  # type: ignore
        assert self.is_annotated_type
        match t.get_args(self.annotation)[0]:
            case union if t.get_origin(union) in (t.Union, types.UnionType):
                return t.get_args(union)[0]
            case base_type:
                return base_type

    @property
    def annotated_metadata(self) -> tuple:
        assert self.is_annotated_type
        return t.get_args(self.annotation)[1:]


class AnnotatedParameters(list[AnnotatedParameter]):
    def __init__(self, values: t.Iterable):
        super().__init__(values)

    @classmethod
    def from_func(cls, func: t.Callable) -> t.Self:
        return cls(
            ann_param
            for param in inspect.signature(func).parameters.values()
            if (ann_param := AnnotatedParameter.from_parameter(param)).is_annotated_type
        )
