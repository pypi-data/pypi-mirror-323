from __future__ import annotations

import base64
import binascii
import enum
import inspect
import pathlib
import typing as t
import uuid
from datetime import datetime, timedelta
from pathlib import Path

import dateutil.parser

from . import (
    case_convert,
    codegen,
    lazy_wrapper,
    objectid_proxy,
    serde_cache,
    utils,
)
from .objectid_proxy import ObjectId
from .typedefs import Jsonable


def _build_passthrough_handler(
    serde: JsonDeserializationCache,
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
    gen.write(
        f"if not isinstance({value}, {simple_value_type.__name__}):",
        f"    raise SerdeError('Expected {simple_value_type.__name__}, got {{}}'.format({value}))",
    )

    return value


def _build_handler_int_from_int(
    serde: JsonDeserializationCache,
    gen: codegen.Codegen,
    value: t.Any,
    value_type: t.Type,
    type_key: t.Type,
) -> str:
    gen.write(
        f"if not isinstance({value}, int) and not (isinstance({value}, float) and {value}.is_integer()):",
        f"    raise SerdeError('Expected int, got {{}}'.format({value}))",
    )
    return f"int({value})"


def _build_handler_float_from_float(
    serde: JsonDeserializationCache,
    gen: codegen.Codegen,
    value: t.Any,
    value_type: t.Type,
    type_key: t.Type,
) -> str:
    gen.write(
        f"if not isinstance({value}, (int, float)):",
        f"    raise SerdeError('Expected float, got {{}}'.format({value}))",
    )
    return f"float({value})"


def _build_handler_bytes_from_str(
    serde: JsonDeserializationCache,
    gen: codegen.Codegen,
    value: t.Any,
    value_type: t.Type,
    type_key: t.Type,
) -> str:
    result_var = gen.get_new_variable()

    gen.expose_value("base64", base64)
    gen.expose_value("binascii", binascii)

    gen.write(
        f"if not isinstance({value}, str):",
        f"    raise SerdeError('Expected bytes encoded as base64, got {{}}'.format({value}))",
        f"",
        f"try:",
        f"    {result_var} = base64.b64decode({value}.encode('utf-8'))",
        f"except binascii.Error as e:",
        f"    raise SerdeError('Encountered invalid base64 string: {{}}'.format(e)) from None",
    )

    return result_var


def _build_handler_datetime_from_str(
    serde: JsonDeserializationCache,
    gen: codegen.Codegen,
    value: t.Any,
    value_type: t.Type,
    type_key: t.Type,
) -> str:
    result_var = gen.get_new_variable()

    gen.expose_value("dateutil_parser", dateutil.parser)

    gen.write(
        f"if not isinstance({value}, str):",
        f"    raise SerdeError('Expected date/time string, got {{}}'.format({value}))",
        f"",
        f"try:",
        f"  {result_var} = dateutil_parser.isoparse({value})",
        f"except ValueError:",
        f"  raise SerdeError('Invalid date/time string: {{}}'.format({value})) from None",
        f"",
        f"if {result_var}.tzinfo is None:",
        f"    raise SerdeError('The date/time value `{{}}` is missing a timezone.'.format({value}))",
    )

    return result_var


def _build_handler_float_to_timedelta(
    serde: JsonDeserializationCache,
    gen: codegen.Codegen,
    value: t.Any,
    value_type: t.Type,
    type_key: t.Type,
) -> str:
    result_var = gen.get_new_variable()

    gen.expose_value("timedelta", timedelta)

    gen.write(
        f"if not isinstance({value}, float):",
        f"    raise SerdeError('Expected float, got {{}}'.format({value}))",
        f"",
        f"{result_var} = timedelta(seconds={value})",
    )

    return result_var


def _build_handler_list_to_tuple(
    serde: JsonDeserializationCache,
    gen: codegen.Codegen,
    value: t.Any,
    value_type: t.Type,
    type_key: t.Type,
) -> str:
    n_expected_values = len(t.get_args(value_type))
    subtypes = t.get_args(value_type)

    gen.write(
        f"if not isinstance({value}, list):",
        f"    raise SerdeError('Expected list, got {{}}'.format({value}))",
        f"",
        f"if len({value}) != {len(subtypes)}:",
        f"    raise SerdeError('Expected list of length {n_expected_values}, got {{}}'.format(len({value})))",
        f"",
    )

    # Convert the individual values
    subresults: list[str] = []

    for ii, sub_type in enumerate(subtypes):
        subresult = serde._write_single_handler(
            gen,
            f"{value}[{ii}]",
            sub_type,
            utils.get_type_key(sub_type),
        )
        subresults.append(subresult)

    # Return the result
    result_var = gen.get_new_variable()

    gen.write("", f"{result_var} = tuple([{', '.join(subresults)}])")

    return result_var


def _build_handler_list_to_list(
    serde: JsonDeserializationCache,
    gen: codegen.Codegen,
    value: t.Any,
    value_type: t.Type,
    type_key: t.Type,
) -> str:
    result_var = gen.get_new_variable()
    count_var = gen.get_new_variable()

    gen.write(
        f"if not isinstance({value}, list):",
        f"    raise SerdeError('Expected list, got {{}}'.format({value}))",
        f"",
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


def _build_handler_list_to_set(
    serde: JsonDeserializationCache,
    gen: codegen.Codegen,
    value: t.Any,
    value_type: t.Type,
    type_key: t.Type,
) -> str:
    result_var = gen.get_new_variable()
    count_var = gen.get_new_variable()

    gen.write(
        f"if not isinstance({value}, list):",
        f"    raise SerdeError('Expected list, got {{}}'.format({value}))",
        f"",
        f"{result_var} = set()",
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

    gen.write(f"{result_var}.add({subresult})")

    gen.indentation_level -= 1
    return result_var


def _build_handler_dict_to_dict(
    serde: JsonDeserializationCache,
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
        f"if not isinstance({value}, dict):",
        f"    raise SerdeError('Expected dict, got {{}}'.format({value}))",
        f"",
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


def _build_handler_object_id_from_str(
    serde: JsonDeserializationCache,
    gen: codegen.Codegen,
    value: t.Any,
    value_type: t.Type,
    type_key: t.Type,
) -> str:
    result_var = gen.get_new_variable()

    gen.expose_value("bson", objectid_proxy)

    gen.write(
        f"if not isinstance({value}, str):",
        f"    raise SerdeError('Expected str, got {{}}'.format({value}))",
        f"",
        f"try:",
        f"    {result_var} = bson.ObjectId({value})",
        f"except bson.errors.InvalidId as e:",
        f"    raise SerdeError('Invalid ObjectId: {{}}'.format(e)) from None",
    )

    return result_var


def _build_handler_optional(
    serde: JsonDeserializationCache,
    gen: codegen.Codegen,
    value: t.Any,
    value_type: t.Type,
    type_key: t.Type,
) -> t.Any:
    # `Optional` is really just an alias for `Union`. Find the non-`None`
    # subtype
    subtype = utils.get_optional_subtype(value_type)
    subtype_key = utils.get_type_key(subtype)

    # Don't get too clever here. Yes, it would be nice to reuse the same result
    # variable as the subresult, but that would not only require a needless
    # negation in the `if`, but also lead to problems if a subresult doesn't
    # actually return a variable, but say `int(variable)`.
    result_var = gen.get_new_variable()

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
    serde: JsonDeserializationCache,
    gen: codegen.Codegen,
    value: t.Any,
    value_type: t.Type,
    type_key: t.Type,
) -> t.Any:
    return value


def _build_handler_literal_from_str(
    serde: JsonDeserializationCache,
    gen: codegen.Codegen,
    value: t.Any,
    value_type: t.Type,
    type_key: t.Type,
) -> t.Any:
    gen.write(
        f"if not isinstance({value}, str):",
        f"    raise SerdeError('Expected str, got {{}}'.format({value}))",
    )
    return value


def _build_handler_path_from_str(
    serde: JsonDeserializationCache,
    gen: codegen.Codegen,
    value: t.Any,
    value_type: t.Type,
    type_key: t.Type,
) -> str:
    result_var = gen.get_new_variable()

    gen.expose_value("pathlib", pathlib)

    gen.write(
        f"if not isinstance({value}, str):",
        f"    raise SerdeError('Expected str, got {{}}'.format({value}))",
        f"",
        f"{result_var} = pathlib.Path({value})",
    )

    return result_var


def _build_handler_uuid_from_str(
    serde: JsonDeserializationCache,
    gen: codegen.Codegen,
    value: t.Any,
    value_type: t.Type,
    type_key: t.Type,
) -> str:
    result_var = gen.get_new_variable()

    gen.expose_value("uuid", uuid)

    gen.write(
        f"if not isinstance({value}, str):",
        f"    raise SerdeError('Expected str, got {{}}'.format({value}))",
        f"",
        f"try:",
        f"    {result_var} = uuid.UUID({value})",
        f"except ValueError as e:",
        f"    raise SerdeError('Invalid UUID: {{}}'.format(e)) from None",
    )

    return result_var


JSON_HANDLER_BUILDERS = {
    bool: _build_passthrough_handler,
    int: _build_handler_int_from_int,
    float: _build_handler_float_from_float,
    str: _build_passthrough_handler,
    bytes: _build_handler_bytes_from_str,
    datetime: _build_handler_datetime_from_str,
    timedelta: _build_handler_float_to_timedelta,
    tuple: _build_handler_list_to_tuple,
    list: _build_handler_list_to_list,
    set: _build_handler_list_to_set,
    dict: _build_handler_dict_to_dict,
    t.Union: _build_handler_optional,
    t.Any: _build_handler_any_to_any,
    ObjectId: _build_handler_object_id_from_str,
    t.Literal: _build_handler_literal_from_str,
    Path: _build_handler_path_from_str,
    type(Path()): _build_handler_path_from_str,
    uuid.UUID: _build_handler_uuid_from_str,
}


class JsonDeserializationCache(serde_cache.SerdeCache[Jsonable, t.Any]):
    """
    Configuration & cache for deserializing JSON into Python objects.
    """

    def __init__(
        self,
        *,
        custom_handlers: dict[
            t.Type,
            t.Callable[
                [JsonDeserializationCache, t.Any, t.Type],
                Jsonable,
            ],
        ] = {},
        lazy: bool = False,
        python_attribute_name_to_doc_name: t.Callable[
            [str], str
        ] = case_convert.identity,
        python_class_name_to_doc_name: t.Callable[[str], str] = case_convert.identity,
        python_enum_name_to_doc_name: t.Callable[[str], str] = str.lower,
    ) -> None:
        super().__init__(
            eager_class_handler_builders=JSON_HANDLER_BUILDERS,
            lazy_class_handler_builders={},
            override_method_name="_uniserde_from_json_",
            user_provided_handlers=custom_handlers,
            lazy=lazy,
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
        assert inspect.isclass(value_type), value_type
        assert value_type is type_key, (value_type, type_key)

        # Make sure the input is a dictionary. By handling it here the code
        # isn't repeated in every subclass.
        gen.write(
            f"if not isinstance({input_variable_name}, dict):",
            f"    raise SerdeError('Expected class instance stored as object, got {{}}'.format({input_variable_name}))",
            f"",
        )

        # If this class is not serialized `@as_child`, create regular
        # deserialization logic.
        result_var = gen.get_new_variable()

        if not utils.should_serialize_as_child(value_type):
            self._build_field_by_field_class_handler_without_children(
                gen,
                input_variable_name,
                result_var,
                value_type,
            )
            return result_var

        # Otherwise precompute a list of possible classes. Then delegate to a
        # deserializer for every possible child class.
        doc_key_to_child_class = {
            self._python_class_name_to_doc_name(sub_cls.__name__): sub_cls
            for sub_cls in utils.all_subclasses(value_type, True)
        }

        # Which class to deserialize is stored in the `type` field
        type_var = gen.get_new_variable()

        gen.write(
            f"try:",
            f'    {type_var} = {input_variable_name}.pop("type")',
            f"except KeyError:",
            f'    raise SerdeError("Missing `type` field in {value_type.__name__} instance") from None',
            f"",
            f"match {type_var}:",
        )
        gen.indentation_level += 1

        for sub_cls_type_key, sub_cls in doc_key_to_child_class.items():
            gen.write(
                f"case {sub_cls_type_key!r}:",
            )
            gen.indentation_level += 1

            self._build_field_by_field_class_handler_without_children(
                gen,
                input_variable_name,
                result_var,
                sub_cls,
            )

            gen.indentation_level -= 1

        gen.indentation_level -= 1

        # Phew!
        return result_var

    def _build_field_by_field_class_handler_without_children(
        self,
        gen: codegen.Codegen,
        input_variable_name: str,
        result_var: str,
        cls: t.Type,
    ) -> None:
        dict_var = gen.get_new_variable()

        # Go lazy?
        if self._lazy and lazy_wrapper.can_create_lazy_instance(cls):
            lazy_wrapper_var = gen.get_new_variable()
            self_var = gen.get_new_variable()
            cls_var = gen.get_new_variable()

            gen.expose_value(lazy_wrapper_var, lazy_wrapper)
            gen.expose_value(self_var, self)
            gen.expose_value(cls_var, cls)

            gen.write(
                f"{result_var} = {lazy_wrapper_var}.create_lazy_instance({input_variable_name}, {self_var}, {cls_var})",
            )
            return

        # Go eager!
        cls_var = gen.get_new_variable()
        gen.expose_value(cls_var, cls)

        gen.write(
            f"{result_var} = object.__new__({cls_var})",
            f"{dict_var} = vars({result_var})",
            f"",
        )

        # Deserialize all fields
        for field_py_name, field_value_type in utils.get_class_attributes_recursive(
            cls
        ).items():
            field_doc_name = self._python_attribute_name_to_doc_name(field_py_name)
            field_type_key = utils.get_type_key(field_value_type)

            gen.write(f"# {field_py_name}")
            field_var = gen.get_new_variable()
            gen.write(
                f"try:",
                f"    {field_var} = {input_variable_name}.pop({field_doc_name!r})",
                f"except KeyError:",
                f"    raise SerdeError('Missing field {{}}'.format({field_doc_name!r})) from None",
                f"",
            )

            subresult = self._write_single_handler(
                gen,
                field_var,
                field_value_type,
                utils.get_type_key(field_type_key),
            )
            gen.write(f"{dict_var}[{field_py_name!r}] = {subresult}")

        # Make sure no superfluous fields are present
        gen.write(
            f"",
            f"if {input_variable_name}:",
            f"    raise SerdeError('Object contains superfluous fields: {{}}'.format({input_variable_name}.keys()))",
        )

    def _build_flag_enum_handler(
        self,
        gen: codegen.Codegen,
        input_variable_name: str,
        value_type: t.Type[enum.Flag],
        type_key: t.Type[enum.Flag],
    ) -> str:
        result_var = gen.get_new_variable()
        value_type_var = gen.get_new_variable()
        options_var = gen.get_new_variable()
        count_var = gen.get_new_variable()

        gen.expose_value(value_type_var, value_type)

        # Prepare a serialized version of all options. Do this right in the
        # code, so the enum options can already be instantiated.
        gen.write(f"{options_var} = {{")

        for option in value_type:
            # How can opt_py_type be None here? According to VSCode it can be
            assert option.name is not None, option
            option_py_name = option.name
            option_doc_name = self._python_enum_name_to_doc_name(option_py_name)

            gen.write(f"    {option_doc_name!r}: {value_type_var}.{option_py_name},")

        # Look up all received options and add them to the result
        gen.write(
            f"}}",
            f"",
            f"{result_var} = {value_type_var}(0)",
            f"",
            f"for {count_var} in {input_variable_name}:",
            f"    if not isinstance({count_var}, str):",
            f"        raise SerdeError('Expected enumeration value as string, got `{{}}`'.format({count_var}))",
            f"",
            f"    try:",
            f"        {result_var} |= {options_var}[{count_var}]",
            f"    except KeyError:",
            f"        raise SerdeError('Invalid enumeration value `{{}}`'.format({count_var})) from None",
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
        value_type_var = gen.get_new_variable()
        options_var = gen.get_new_variable()

        gen.expose_value(value_type_var, value_type)

        # Prepare a serialized version of all options. Do this right in the
        # code, so the enum options can already be instantiated.
        gen.write(f"{options_var} = {{")

        for option in value_type:
            option_py_name = option.name
            option_doc_name = self._python_enum_name_to_doc_name(option_py_name)

            gen.write(f"    {option_doc_name!r}: {value_type_var}.{option_py_name},")

        # Look up the value
        gen.write(
            f"}}",
            f"",
            f"if not isinstance({input_variable_name}, str):",
            f"    raise SerdeError('Expected enumeration value as string, got `{{}}`'.format({input_variable_name}))",
            f"",
            f"try:",
            f"    {result_var} = {options_var}[{input_variable_name}]",
            f"except KeyError:",
            f"    raise SerdeError('Invalid enumeration value `{{}}`'.format({input_variable_name})) from None",
        )

        return result_var
