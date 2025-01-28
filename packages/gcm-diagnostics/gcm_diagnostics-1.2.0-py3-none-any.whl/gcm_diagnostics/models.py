from __future__ import annotations

from collections.abc import Collection
from enum import StrEnum
from http import HTTPStatus
from typing import Any, ClassVar, Generic, Literal, Optional, Type, TypeVar, Union

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict, Field, SerializeAsAny, create_model

Loc = list[str | int]


class BaseModel(PydanticBaseModel):
    """
    Base model for the diagnostic pydantic models.
    """

    model_config = ConfigDict(extra="forbid")


class GenericError(BaseModel):
    """Generic error model compatible with pydantic diagnostics."""

    loc: Loc = Field(default_factory=list, title="Error location.")
    msg: str = Field(title="Descriptive human readable error message")
    type: str = Field(title="Error type identifier")


class DiagnosticError(GenericError):
    """
    Base class for all diagnostic errors.
    """

    model_config = ConfigDict(extra="allow")

    # This is intentionally protected, as Pydantic does not export protected members to OpenAPI schema,
    # and that is exactly what we want. Status code is not part of the JSON response, but it represents
    # HTTP status code of the error response.
    status_code: ClassVar[int] = HTTPStatus.UNPROCESSABLE_ENTITY

    loc: Loc = Field(default_factory=list, title="Error location")
    msg: str = Field(title="Descriptive human readable error message")
    type: str = Field(title="Error type identifier")


T = TypeVar("T", bound=GenericError)


class DiagnosticResponse(BaseModel, Generic[T]):
    """
    Response returned to user, when any diagnostic error is collected.
    """

    detail: list[SerializeAsAny[T]] = Field(default_factory=list)


class ModelValidationError(GenericError):
    """Base class describing Pydantic validation error."""

    ctx: Optional[dict[str, Any]] = Field(
        None, description="An optional object which contains values required to render the error message."
    )
    input: Any = Field(description="The input provided for validation.")


ALL_PYDANTIC_ERROR_TYPES: dict[str, str] = {
    "arguments_type": "Invalid type for arguments.",
    "assertion_error": "This error is raised when a failing `assert` statement is encountered during validation.",
    "bool_parsing": "This error is raised when the input value is a string that is not valid for coercion to a boolean.",
    "bool_type": "This error is raised when the input value's type is not valid for a `bool` field.",
    "bytes_invalid_encoding": "This error is raised when a `bytes` value is invalid under the configured encoding.",
    "bytes_too_long": "This error is raised when a `bytes` value is longer than the configured maximum length.",
    "bytes_too_short": "This error is raised when a `bytes` value is shorter than the configured minimum length.",
    "bytes_type": "This error is raised when the input value's type is not valid for a `bytes` field.",
    "callable_type": "This error is raised when the input value's type is not valid for a `callable` field.",
    "complex_str_parsing": "This error is raised when the input value is a string but cannot be parsed as a complex number.",
    "complex_type": "This error is raised when the input value's type is not valid for a `complex` field.",
    "dataclass_exact_type": "This error is raised when validating a dataclass with `strict=True` and the input is not an "
    "instance of the dataclass.",
    "dataclass_type": "This error is raised when the input value's type is not valid for a `dataclass` field.",
    "date_from_datetime_inexact": "This error is raised when a `date` value is created from a `datetime` value that is not at "
    "midnight. For a timestamp to parse into a field of type `date`, the time components must all "
    "be zero.",
    "date_from_datetime_parsing": "This error is raised when the input value is a string that cannot be parsed for a date field.",
    "date_future": "This error is raised when the input value provided for a `FutureDate` field is not in the future.",
    "date_parsing": "This error is raised when validating JSON where the input value is string that cannot be parsed for a date "
    "field.",
    "date_past": "This error is raised when the value provided for a `PastDate` field is not in the past.",
    "date_type": "This error is raised when the input value's type is not valid for a `date` field.",
    "datetime_from_date_parsing": "This error is raised when the input value is a string that cannot be parsed for a `datetime` "
    "field.",
    "datetime_future": "This error is raised when the input value provided for a `FutureDatetime` field is not in the future.",
    "datetime_object_invalid": "This error is raised when something about the `datetime` object is not valid.",
    "datetime_parsing": "This error is raised when the input value is a string that cannot be parsed for a `datetime` field.",
    "datetime_past": "This error is raised when the value provided for a `PastDatetime` field is not in the past.",
    "datetime_type": "This error is raised when the input value's type is not valid for a `datetime` field.",
    "decimal_max_digits": "This error is raised when a `Decimal` value has more digits than the configured maximum.",
    "decimal_max_places": "This error is raised when the value provided for a `Decimal` has too many digits after the decimal "
    "point.",
    "decimal_parsing": "This error is raised when the value provided for a `Decimal` could not be parsed as a decimal number.",
    "decimal_type": "This error is raised when the input value's type is not valid for a `Decimal` field.",
    "decimal_whole_digits": "This error is raised when the value provided for a `Decimal` has more digits before the decimal "
    "point than `max_digits - decimal_places` (as long as both are specified).",
    "dict_type": "This error is raised when the input value's type is not valid for a `dict` field.",
    "enum": "This error is raised when the input value is not a valid `enum` member.",
    "extra_forbidden": "This error is raised when the input value has extra fields that are not allowed.",
    "finite_number": "This error is raised when the input value is not a finite number.",
    "float_parsing": "This error is raised when the input value is a string that cannot be parsed as a float.",
    "float_type": "This error is raised when the input value's type is not valid for a `float` field.",
    "frozen_field": "This error is raised when trying to set a value on a frozen field or to delete such a field.",
    "frozen_instance": "This error is raised when trying to set a value of a field on a frozen instance or to delete such an "
    "field.",
    "frozen_set_type": "This error is raised when the input value's type is not valid for a frozenset field.",
    "get_attribute_error": "This error is raised when model_config['from_attributes'] == True and an error is raised while "
    "reading the attributes.",
    "greater_than": "This error is raised when the value is not greater than the field's `gt` constraint.",
    "greater_than_equal": "This error is raised when the value is not greater than or equal to the field's `ge` constraint.",
    "int_from_float": "This error is raised when you provide a `float` value for an `int` field.",
    "int_parsing": "This error is raised when the input value is a string that cannot be parsed as an integer.",
    "int_parsing_size": "This error is raised when the input value is a string that cannot be parsed as an integer because it is "
    "too large.",
    "int_type": "This error is raised when the input value's type is not valid for an `int` field.",
    "invalid_key": "This error is raised when attempting to validate a `dict` that has a key that is not an instance of `str`.",
    "is_instance_of": "This error is raised when the input value is not an instance of the expected type.",
    "is_subclass_of": "This error is raised when the input value is not a subclass of the expected type.",
    "iterable_type": "This error is raised when the input value's type is not valid for an iterable field.",
    "iteration_error": "This error is raised when an error occurs while iterating over the input value.",
    "json_invalid": "This error is raised when the input value is not valid JSON.",
    "json_type": "This error is raised when the input value's type is not valid for a JSON field.",
    "less_than": "This error is raised when the value is not less than the field's `lt` constraint.",
    "less_than_equal": "This error is raised when the value is not less than or equal to the field's `le` constraint.",
    "list_type": "This error is raised when the input value's type is not valid for a `list` field.",
    "literal_error": "This error is raised when the input value is not one of the expected literals.",
    "mapping_type": "This error is raised when the input value's type is not valid for a mapping field.",
    "missing": "This error is raised when a required value is missing.",
    "missing_argument": "This error is raised when a required positional-or-keyword argument is not passed to a function "
    "decorated with `validate_call`.",
    "missing_keyword_only_argument": "This error is raised when a required keyword-only argument is not passed to a function "
    "decorated with `validate_call`.",
    "missing_positional_only_argument": "This error is raised when a required positional-only argument is not passed to a "
    "function decorated with `validate_call`.",
    "model_attributes_type": "This error is raised when the input value is not a valid dictionary, model instance, or instance "
    "that fields can be extracted from.",
    "model_type": "This error is raised when the input to a model is not an instance of the model or dict.",
    "multiple_argument_values": "This error is raised when you provide multiple values for a single argument while calling a "
    "function decorated with `validate_call`.",
    "multiple_of": "This error is raised when the value is not a multiple of the field's `multiple_of` constraint.",
    "needs_python_object": "This type of error is raised when validation is attempted from a format that cannot be converted "
    "to a Python object. For example, we cannot check `isinstance` or `issubclass` from JSON.",
    "no_such_attribute": "This error is raised when the input value does not have the expected attribute.",
    "none_required": "This error is raised when the input value is not `None` for a field that requires `None`.",
    "recursion_loop": "This error is raised when a recursion loop is detected.",
    "set_type": "This error is raised when the input value's type is not valid for a `set` field.",
    "string_pattern_mismatch": "This error is raised when the input value doesn't match the field's `pattern` constraint.",
    "string_sub_type": "This error is raised when the value is an instance of a strict subtype of `str` when the field is "
    "strict.",
    "string_too_long": "This error is raised when the input value is a string whose length is greater than the field's "
    "`max_length` constraint.",
    "string_too_short": "This error is raised when the input value is a string whose length is less than the field's "
    "`min_length` constraint.",
    "string_type": "This error is raised when the input value's type is not valid for a `str` field.",
    "string_unicode": "This error is raised when the value cannot be parsed as a Unicode string.",
    "time_delta_parsing": "This error is raised when the input value is a string that cannot be parsed for a `timedelta` field.",
    "time_delta_type": "This error is raised when the input value's type is not valid for a `timedelta` field.",
    "time_parsing": "This error is raised when the input value is a string that cannot be parsed for a `time` field.",
    "time_type": "This error is raised when the input value's type is not valid for a `time` field.",
    "timezone_aware": "This error is raised when the `datetime` value provided for a timezone-aware `datetime` field doesn't "
    "have timezone information.",
    "timezone_naive": "This error is raised when the `datetime` value provided for a timezone-naive `datetime` field has "
    "timezone information.",
    "too_long": "This error is raised when the value is longer than the field's `max_length` constraint.",
    "too_short": "This error is raised when the value is shorter than the field's `min_length` constraint.",
    "tuple_type": "This error is raised when the input value's type is not valid for a `tuple` field.",
    "unexpected_keyword_argument": "This error is raised when an unexpected keyword argument is passed to a function decorated "
    "with `validate_arguments`.",
    "unexpected_positional_argument": "This error is raised when an unexpected positional argument is passed to a function "
    "decorated with `validate_arguments`.",
    "union_tag_invalid": "This error is raised when the input's discriminator is not one of the expected values.",
    "union_tag_not_found": "This error is raised when it is not possible to extract a discriminator value from the input.",
    "url_parsing": "This error is raised when the input value is a string that cannot be parsed as a URL.",
    "url_scheme": "This error is raised when the URL scheme is not valid for the URL type of the field.",
    "url_syntax_violation": "This error is raised when the URL has a syntax violation.",
    "url_too_long": "This error is raised when the URL length is greater than 2083.",
    "url_type": "This error is raised when the input value's type is not valid for a URL field.",
    "uuid_parsing": "This error is raised when the input value's type is not valid for a UUID field.",
    "uuid_type": "This error is raised when the input value's type is not valid instance for a UUID field (str, bytes or UUID).",
    "uuid_version": "This error is raised when the input value's type is not match UUID version.",
    "value_error": "This error is raised when the input value is not valid.",
}
"""
All possible pydantic error types and their descriptions for creating error models for diagnostic schema.
"""

IGNORED_PYDANTIC_ERROR_TYPES: set[str] = {
    "arguments_type",
    "callable_type",
    "dataclass_exact_type",
    "dataclass_type",
    "datetime_object_invalid",
    "get_attribute_error",
    "is_instance_of",
    "is_subclass_of",
    "model_attributes_type",
    "model_type",
    "needs_python_object",
    "missing_argument",
    "missing_keyword_only_argument",
    "missing_positional_only_argument",
    "multiple_argument_values",
    "no_such_attribute",
    "recursion_loop",
    "unexpected_keyword_argument",
    "unexpected_positional_argument",
}
"""
List of error types that are not included by default in the schema, only if explicitly requested.
"""

_MODEL_VALIDATION_SCHEMA_CACHE: dict[frozenset[str], Type[ModelValidationError]] = {}
_SCHEMA_CACHE: dict[frozenset[Any], Type[DiagnosticResponse[GenericError]]] = {}


def _pydantic_error_factory(include_pydantic_errors: Literal[True] | Collection[str]) -> Type[GenericError]:
    error_types: set[str] = (
        (set(ALL_PYDANTIC_ERROR_TYPES.keys()) - IGNORED_PYDANTIC_ERROR_TYPES)
        if include_pydantic_errors is True
        else set(include_pydantic_errors)
    )

    cache_key = frozenset(error_types)
    if cache_key not in _MODEL_VALIDATION_SCHEMA_CACHE:
        error_desc = "\n".join(f" - `{error_type}`: {ALL_PYDANTIC_ERROR_TYPES[error_type]}" for error_type in error_types)

        _MODEL_VALIDATION_SCHEMA_CACHE[cache_key] = create_model(
            "ModelValidationError",
            __doc__=f"Model validation error. Possible types are:\n\n{error_desc}",
            __base__=ModelValidationError,
            type=(StrEnum("ErrorTypes", [(error_type, error_type) for error_type in error_types]), ...),
        )

    return _MODEL_VALIDATION_SCHEMA_CACHE[cache_key]


def diagnostic_schema(
    types: Optional[Collection[Type[DiagnosticError]]] = None, include_pydantic_errors: bool | Collection[str] = True
) -> dict[int | str, dict[str, Any]]:
    """
    Create a diagnostic response schema for the given error types. Usefull for documenting
    API endpoint diagnostic responses for OpenAPI schema.

    Usage with FastAPI:

    >>> from fastapi import FastAPI
    >>> from gcm_diagnostics.models import diagnostic_schema
    >>> from gcm_diagnostics.errors import EntityNotFound, EntityAlreadyExists
    >>>
    >>> app = FastAPI()
    >>>
    >>>
    >>> @app.get("/", responses=diagnostic_schema([EntityNotFound, EntityAlreadyExists]))
    >>> async def index():
    >>>     pass

    :param types: Collection of diagnostic error types for which the response schema should be generated.
    :param include_pydantic_errors: Include pydantic's default error schema for 422.
       If True, include all pydantic error types. If False, does not include any. If a collection of strings,
       only specified error types will be included.
    :return: Diagnostic response schema suitable for FastAPI endpoint.
    """
    if not types:
        types = []

    errors_by_status: dict[int, list[Type[GenericError]]] = {}

    if include_pydantic_errors:
        pydantic_model = _pydantic_error_factory(include_pydantic_errors)
        errors_by_status[HTTPStatus.UNPROCESSABLE_ENTITY] = [pydantic_model]

    # Group errors by status code.
    for t in types:
        errors_by_status.setdefault(t.status_code, []).append(t)

    # Create schema for each status code.
    out: dict[int | str, dict[str, Any]] = {}

    for status, errors in errors_by_status.items():
        model_key = frozenset(errors)

        if model_key not in _SCHEMA_CACHE:
            _SCHEMA_CACHE[model_key] = create_model(
                f"DiagnosticResponse{status}",
                __doc__=f"Error response for HTTP status {status}.",
                # mypy does not like union unpacking, in runtime it works as expected.
                __base__=DiagnosticResponse[Union[*errors]],  # type: ignore[valid-type]
            )

        out[status] = {"model": _SCHEMA_CACHE[model_key]}

    return out
