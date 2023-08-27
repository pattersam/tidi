import inspect
import typing as t

import pytest

from tidi import parameters

METADATA_OBJ = object()


def test_create_annotated_parameters_from_func():
    def function(
        arg_1: str,
        arg_2: int,
        kwarg_1: str = "a",
        kwarg_2: t.Annotated[int, METADATA_OBJ] = 1,
        kwarg_3: t.Annotated[str | None, METADATA_OBJ, METADATA_OBJ] = None,
    ):
        return

    params = parameters.AnnotatedParameters.from_func(function)
    assert len(params) == 2
    assert params[0].is_annotated_type
    assert params[0].base_type is int
    assert params[0].annotated_metadata == (METADATA_OBJ,)
    assert params[1].is_annotated_type
    assert params[1].base_type is str
    assert params[1].annotated_metadata == (METADATA_OBJ, METADATA_OBJ)


def test_create_zero_annotated_parameters_from_func():
    def function(
        arg_1: str,
        arg_2: int,
        kwarg_1: str = "a",
        kwarg_2: int = 1,
        kwarg_3: str | None = None,
    ):
        return

    params = parameters.AnnotatedParameters.from_func(function)
    assert len(params) == 0


def test_create_annotated_parameter_from_plain_positional_parameter():
    param = parameters.AnnotatedParameter.from_parameter(
        inspect.Parameter(name="arg_1", kind=inspect.Parameter.POSITIONAL_OR_KEYWORD)
    )
    assert not param.is_annotated_type
    with pytest.raises(AssertionError):
        param.base_type
    with pytest.raises(AssertionError):
        param.annotated_metadata


def test_create_annotated_parameter_from_type_hinted_positional_parameter():
    param = parameters.AnnotatedParameter.from_parameter(
        inspect.Parameter(
            name="arg_1", kind=inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=dict | None
        )
    )
    assert not param.is_annotated_type
    with pytest.raises(AssertionError):
        param.base_type
    with pytest.raises(AssertionError):
        param.annotated_metadata


def test_create_annotated_parameter_from_type_hinted_kwarg_parameter():
    param = parameters.AnnotatedParameter.from_parameter(
        inspect.Parameter(
            name="kwarg_1",
            kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
            default=None,
            annotation=dict | None,
        )
    )
    assert not param.is_annotated_type
    with pytest.raises(AssertionError):
        param.base_type
    with pytest.raises(AssertionError):
        param.annotated_metadata


def test_create_annotated_parameter_from_annotated_type_hinted_kwarg_parameter():
    param = parameters.AnnotatedParameter.from_parameter(
        inspect.Parameter(
            name="kwarg_1",
            kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
            default="default",
            annotation=t.Annotated[str, METADATA_OBJ],
        )
    )
    assert param.is_annotated_type
    assert param.base_type is str
    assert param.annotated_metadata == (METADATA_OBJ,)


def test_create_annotated_parameter_from_annotated_union_type_hinted_kwarg_parameter():
    param = parameters.AnnotatedParameter.from_parameter(
        inspect.Parameter(
            name="kwarg_1",
            kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
            default=None,
            annotation=t.Annotated[str | None, METADATA_OBJ],
        )
    )
    assert param.is_annotated_type
    assert param.base_type is str
    assert param.annotated_metadata == (METADATA_OBJ,)
