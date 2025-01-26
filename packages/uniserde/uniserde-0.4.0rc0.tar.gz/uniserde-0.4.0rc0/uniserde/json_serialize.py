from __future__ import annotations

import base64
import enum
import pathlib
import typing as t
import uuid
from datetime import datetime, timedelta
from pathlib import Path

from . import case_convert, codegen, objectid_proxy, serde_cache, utils
from .objectid_proxy import ObjectId
from .typedefs import Jsonable


def _build_passthrough_handler(
    serde: JsonSerializationCache,
    gen: codegen.Codegen,
    value: t.Any,
    simple_value_type: t.Type,
    type_key: t.Type,
) -> str:
    """
    Builds a handler that simply checks the type of the value and raises an
    exception if it is not the expected type.

    The value itself is returned as-is.
    """
    gen.write(f"assert isinstance({value}, {simple_value_type.__name__}), {value}")

    return value


def _build_handler_float_to_float(
    serde: JsonSerializationCache,
    gen: codegen.Codegen,
    value: t.Any,
    value_type: t.Type,
    type_key: t.Type,
) -> str:
    gen.write(f"assert isinstance({value}, (int, float)), {value}")
    return value


def _build_handler_bytes_to_str(
    serde: JsonSerializationCache,
    gen: codegen.Codegen,
    value: t.Any,
    value_type: t.Type,
    type_key: t.Type,
) -> str:
    result_var = gen.get_new_variable()

    gen.expose_value("base64", base64)

    gen.write(
        f"assert isinstance({value}, bytes), {value}",
        f"{result_var} = base64.b64encode({value}).decode('utf-8')",
    )

    return result_var


def _build_handler_datetime_to_str(
    serde: JsonSerializationCache,
    gen: codegen.Codegen,
    value: t.Any,
    value_type: t.Type,
    type_key: t.Type,
) -> str:
    result_var = gen.get_new_variable()

    gen.expose_value("datetime", datetime)

    gen.write(
        f"assert isinstance({value}, datetime), {value}",
        f"assert {value}.tzinfo is not None, 'Encountered datetime without a timezone. Please always set timezones, or expect hard to find bugs.'",
        f"{result_var} = {value}.isoformat()",
    )

    return result_var


def _build_handler_timedelta_to_float(
    serde: JsonSerializationCache,
    gen: codegen.Codegen,
    value: t.Any,
    value_type: t.Type,
    type_key: t.Type,
) -> str:
    result_var = gen.get_new_variable()

    gen.expose_value("timedelta", timedelta)

    gen.write(
        f"assert isinstance({value}, timedelta), {value}",
        f"{result_var} = {value}.total_seconds()",
    )

    return result_var


def _build_handler_tuple_to_list(
    serde: JsonSerializationCache,
    gen: codegen.Codegen,
    value: t.Any,
    value_type: t.Type,
    type_key: t.Type,
) -> str:
    n_expected_values = len(t.get_args(value_type))

    gen.write(
        f"assert isinstance({value}, tuple), {value}",
        f"assert len({value}) == {n_expected_values}, {value}",
        f"",
    )

    # Convert the individual values
    subresults: list[str] = []

    for ii, sub_type in enumerate(t.get_args(value_type)):
        subresult = serde._write_single_handler(
            gen,
            f"{value}[{ii}]",
            sub_type,
            utils.get_type_key(sub_type),
        )
        subresults.append(subresult)

    # Return the result
    result_var = gen.get_new_variable()

    gen.write("", f"{result_var} = [{', '.join(subresults)}]")

    return result_var


def _build_handler_list_to_list(
    serde: JsonSerializationCache,
    gen: codegen.Codegen,
    value: t.Any,
    value_type: t.Type,
    type_key: t.Type,
) -> str:
    result_var = gen.get_new_variable()
    count_var = gen.get_new_variable()

    gen.write(
        f"assert isinstance({value}, list), {value}",
        f"{result_var} = []",
        f"",
        f"for {count_var} in {value}:",
    )

    gen.indentation_level += 1

    subtype = t.get_args(value_type)[0]
    subresult = serde._write_single_handler(
        gen,
        count_var,
        subtype,
        utils.get_type_key(subtype),
    )

    gen.write(f"{result_var}.append({subresult})")

    gen.indentation_level -= 1
    return result_var


def _build_handler_set_to_list(
    serde: JsonSerializationCache,
    gen: codegen.Codegen,
    value: t.Any,
    value_type: t.Type,
    type_key: t.Type,
) -> str:
    result_var = gen.get_new_variable()
    count_var = gen.get_new_variable()

    gen.write(
        f"assert isinstance({value}, set), {value}",
        f"{result_var} = []",
        f"",
        f"for {count_var} in {value}:",
    )

    gen.indentation_level += 1

    subtype = t.get_args(value_type)[0]
    subresult = serde._write_single_handler(
        gen,
        count_var,
        subtype,
        utils.get_type_key(subtype),
    )

    gen.write(f"{result_var}.append({subresult})")

    gen.indentation_level -= 1
    return result_var


def _build_handler_dict_to_dict(
    serde: JsonSerializationCache,
    gen: codegen.Codegen,
    value: t.Any,
    value_type: t.Type,
    type_key: t.Type,
) -> str:
    result_var = gen.get_new_variable()
    key_var = gen.get_new_variable()
    value_var = gen.get_new_variable()

    key_subtype, value_subtype = t.get_args(value_type)
    assert key_subtype is str, f"Dict keys must be strings, not `{key_subtype}`"

    gen.write(
        f"assert isinstance({value}, dict), {value}",
        f"{result_var} = {{}}",
        f"",
        f"for {key_var}, {value_var} in {value}.items():",
    )

    gen.indentation_level += 1

    value_result = serde._write_single_handler(
        gen,
        value_var,
        value_subtype,
        utils.get_type_key(value_subtype),
    )

    gen.write(f"{result_var}[{key_var}] = {value_result}")

    gen.indentation_level -= 1
    return result_var


def _build_handler_object_id_to_str(
    serde: JsonSerializationCache,
    gen: codegen.Codegen,
    value: t.Any,
    value_type: t.Type,
    type_key: t.Type,
) -> str:
    result_var = gen.get_new_variable()

    gen.expose_value("bson", objectid_proxy)

    gen.write(
        f"assert isinstance({value}, bson.ObjectId), {value}",
        f"{result_var} = str({value})",
    )

    return result_var


def _build_handler_optional(
    serde: JsonSerializationCache,
    gen: codegen.Codegen,
    value: t.Any,
    value_type: t.Type,
    type_key: t.Type,
) -> t.Any:
    # `Optional` is really just an alias for `Union`. Find the non-`None`
    # subtype
    subtype = utils.get_optional_subtype(value_type)
    subtype_key = utils.get_type_key(subtype)

    result_var = gen.get_new_variable()

    # Don't get too clever here. Yes, it would be nice to reuse the same result
    # variable as the subresult, but that would not only require a needless
    # negation in the `if`, but also lead to problems if a subresult doesn't
    # actually return a variable, but say `int(variable)`.
    gen.write(
        f"if {value} is None:",
        f"    {result_var} = None",
        f"else:",
    )

    gen.indentation_level += 1
    subresult_var = serde._write_single_handler(
        gen,
        value,
        subtype,
        subtype_key,
    )
    gen.write(f"{result_var} = {subresult_var}")
    gen.indentation_level -= 1

    return result_var


def _build_handler_any_to_any(
    serde: JsonSerializationCache,
    gen: codegen.Codegen,
    value: t.Any,
    value_type: t.Type,
    type_key: t.Type,
) -> t.Any:
    return value


def _build_handler_literal_to_str(
    serde: JsonSerializationCache,
    gen: codegen.Codegen,
    value: t.Any,
    value_type: t.Type,
    type_key: t.Type,
) -> t.Any:
    gen.write(f"assert isinstance({value}, str), {value}")
    return value


def _build_handler_path_to_str(
    serde: JsonSerializationCache,
    gen: codegen.Codegen,
    value: t.Any,
    value_type: t.Type,
    type_key: t.Type,
) -> str:
    result_var = gen.get_new_variable()

    gen.expose_value("pathlib", pathlib)

    gen.write(
        f"assert isinstance({value}, pathlib.Path), {value}",
        f"{result_var} = str({value}.absolute())",
    )

    return result_var


def _build_handler_uuid_to_str(
    serde: JsonSerializationCache,
    gen: codegen.Codegen,
    value: t.Any,
    value_type: t.Type,
    type_key: t.Type,
) -> str:
    result_var = gen.get_new_variable()

    gen.expose_value("uuid", uuid)

    gen.write(
        f"assert isinstance({value}, uuid.UUID), {value}",
        f"{result_var} = str({value})",
    )

    return result_var


JSON_HANDLER_BUILDERS = {
    bool: _build_passthrough_handler,
    int: _build_passthrough_handler,
    float: _build_handler_float_to_float,
    str: _build_passthrough_handler,
    bytes: _build_handler_bytes_to_str,
    datetime: _build_handler_datetime_to_str,
    timedelta: _build_handler_timedelta_to_float,
    tuple: _build_handler_tuple_to_list,
    list: _build_handler_list_to_list,
    set: _build_handler_set_to_list,
    dict: _build_handler_dict_to_dict,
    t.Union: _build_handler_optional,
    t.Any: _build_handler_any_to_any,
    ObjectId: _build_handler_object_id_to_str,
    t.Literal: _build_handler_literal_to_str,
    Path: _build_handler_path_to_str,
    type(Path()): _build_handler_path_to_str,
    uuid.UUID: _build_handler_uuid_to_str,
}


class JsonSerializationCache(serde_cache.SerdeCache[Jsonable, t.Any]):
    """
    Configuration & cache for serializing JSON into Python objects.
    """

    def __init__(
        self,
        *,
        custom_handlers: dict[
            t.Type,
            t.Callable[
                [JsonSerializationCache, t.Any, t.Type],
                Jsonable,
            ],
        ] = {},
        python_attribute_name_to_doc_name: t.Callable[
            [str], str
        ] = case_convert.identity,
        python_class_name_to_doc_name: t.Callable[[str], str] = case_convert.identity,
        python_enum_name_to_doc_name: t.Callable[[str], str] = str.lower,
    ) -> None:
        super().__init__(
            eager_class_handler_builders=JSON_HANDLER_BUILDERS,
            lazy_class_handler_builders={},
            override_method_name="_uniserde_as_json_",
            user_provided_handlers=custom_handlers,
            lazy=False,
            python_attribute_name_to_doc_name=python_attribute_name_to_doc_name,
            python_class_name_to_doc_name=python_class_name_to_doc_name,
            python_enum_name_to_doc_name=python_enum_name_to_doc_name,
        )

    def _build_field_by_field_class_handler(
        self,
        gen: codegen.Codegen,
        input_variable_name: str,
        value_type: t.Type,
        type_key: t.Type,
    ) -> str:
        result_var = gen.get_new_variable()

        gen.write(
            f"{result_var} = {{}}",
        )

        # Add a type tag?
        if utils.should_serialize_as_child(value_type):
            tag = self._python_class_name_to_doc_name(value_type.__name__)
            gen.write(f"{result_var}['type'] = {tag!r}")

        # Serialize all fields
        for field_py_name, field_value_type in utils.get_class_attributes_recursive(
            type_key
        ).items():
            field_doc_name = self._python_attribute_name_to_doc_name(field_py_name)
            field_type_key = utils.get_type_key(field_value_type)

            gen.write(f"# {field_py_name}")

            subresult = self._write_single_handler(
                gen,
                f"{input_variable_name}.{field_py_name}",
                field_value_type,
                utils.get_type_key(field_type_key),
            )

            gen.write(f"{result_var}[{field_doc_name!r}] = {subresult}")

        return result_var

    def _build_flag_enum_handler(
        self,
        gen: codegen.Codegen,
        input_variable_name: str,
        value_type: t.Type[enum.Flag],
        type_key: t.Type[enum.Flag],
    ) -> str:
        result_var = gen.get_new_variable()
        options_var = gen.get_new_variable()
        value_type_var = gen.get_new_variable()
        count_var = gen.get_new_variable()

        gen.expose_value(value_type_var, value_type)

        # Prepare a serialized version of all options
        option_py_name_to_doc_name: dict[str, str] = {}

        for option in value_type:
            # How can opt_py_type be None here? According to VSCode it can be
            assert option.name is not None, "How can this be None?"

            opt_doc_name = self._python_enum_name_to_doc_name(option.name)
            option_py_name_to_doc_name[option.name] = opt_doc_name

        # Iterate all options and look them up
        gen.write(
            f"{options_var} = {option_py_name_to_doc_name!r}",
            f"{result_var} = []",
            f"",
            f"for {count_var} in {value_type_var}:",
            f"   if {count_var} in {input_variable_name}:",
            f"        {result_var}.append({options_var}[{count_var}.name])",
        )

        return result_var

    def _build_enum_handler(
        self,
        gen: codegen.Codegen,
        input_variable_name: str,
        value_type: t.Type[enum.Enum],
        type_key: t.Type[enum.Enum],
    ) -> str:
        result_var = gen.get_new_variable()
        options_var = gen.get_new_variable()

        # Prepare a serialized version of all options
        option_py_name_to_doc_name = {
            opt.name: self._python_enum_name_to_doc_name(opt.name) for opt in value_type
        }

        # Look up the value
        gen.write(
            f"{options_var} = {option_py_name_to_doc_name!r}",
            f"{result_var} = {options_var}[{input_variable_name}.name]",
        )

        return result_var
