from __future__ import annotations

import enum
import inspect
import typing as t
import uuid
from datetime import datetime, timedelta
from pathlib import Path

from . import case_convert, utils
from .objectid_proxy import ObjectId
from .typedefs import Jsonable


class MongodbSchemaConverter:
    def __init__(
        self,
        *,
        custom_handlers: dict[
            t.Type,
            t.Callable[
                [MongodbSchemaConverter, t.Type],
                Jsonable,
            ],
        ] = {},
        python_attribute_name_to_doc_name: t.Callable[
            [str], str
        ] = case_convert.identity_with_id_exception,
        python_class_name_to_doc_name: t.Callable[[str], str] = case_convert.identity,
        python_enum_name_to_doc_name: t.Callable[[str], str] = str.lower,
    ) -> None:
        self._user_provided_handlers = custom_handlers
        self._python_attribute_name_to_doc_name = python_attribute_name_to_doc_name
        self._python_class_name_to_doc_name = python_class_name_to_doc_name
        self._python_enum_name_to_doc_name = python_enum_name_to_doc_name

        # This field can be used to disable UUIDs to be verified. This is useful
        # because the packages that's used in the unit tests to verify the
        # schemas doesn't recognize UUIDs as "binData", even though that's how
        # pymongo treats them.
        self._enable_uuid_verification = True

    def _process(self, value_type: t.Type) -> Jsonable:
        # Find a matching serializer
        key = utils.get_type_key(value_type)

        # Custom handlers take precedence
        try:
            handler = self._user_provided_handlers[key]
        except KeyError:
            pass
        else:
            return handler(self, value_type)

        # Is there a special handler in that class?
        try:
            override_method = getattr(value_type, "_uniserde_as_mongodb_schema_")
        except AttributeError:
            pass
        else:
            return override_method(self, value_type)

        # Plain old default handler
        try:
            handler = self._schema_builders[key]
        except KeyError:
            pass
        else:
            return handler(self, value_type)

        # Flag enum
        if issubclass(value_type, enum.Flag):
            return self._make_schema_flag_enum(value_type)

        # Enum
        if issubclass(value_type, enum.Enum):
            return self._make_schema_enum(value_type)

        # General class
        assert inspect.isclass(value_type), value_type

        if utils.should_serialize_as_child(value_type):
            return self._make_schema_field_by_field_as_child(value_type)
        else:
            return self._make_schema_field_by_field_no_child(value_type)

    def _make_schema_bool_to_bool(self, value_type: t.Type) -> Jsonable:
        return {"type": "boolean"}

    def _make_schema_int_to_int(self, value_type: t.Type) -> Jsonable:
        return {"bsonType": ["int", "long"]}

    def _make_schema_float_to_float(self, value_type: t.Type) -> Jsonable:
        return {"bsonType": ["int", "long", "double"]}

    def _make_schema_bytes_to_bytes(self, value_type: t.Type) -> Jsonable:
        return {"bsonType": "binData"}

    def _make_schema_str_to_str(self, value_type: t.Type) -> Jsonable:
        return {"type": "string"}

    def _make_schema_datetime_to_datetime(self, value_type: t.Type) -> Jsonable:
        return {"bsonType": "date"}

    def _make_schema_timedelta_to_float(self, value_type: t.Type) -> Jsonable:
        return {"bsonType": ["int", "long", "double"]}

    def _make_schema_tuple_to_list(self, value_type: t.Type) -> Jsonable:
        return {
            "type": "array",
            "items": [self._process(subtype) for subtype in t.get_args(value_type)],
        }

    def _make_schema_list_to_list(self, value_type: t.Type) -> Jsonable:
        return {
            "type": "array",
            "items": self._process(t.get_args(value_type)[0]),
        }

    def _make_schema_set_to_list(self, value_type: t.Type) -> Jsonable:
        return {
            "type": "array",
            "items": self._process(t.get_args(value_type)[0]),
        }

    def _make_schema_path_to_str(self, value_type: t.Type) -> Jsonable:
        return {"type": "string"}

    def _make_schema_uuid_to_uuid(self, value_type: t.Type) -> Jsonable:
        if self._enable_uuid_verification:
            return {"bsonType": "binData"}

        return {}

    def _make_schema_dict_to_dict(self, value_type: t.Type) -> Jsonable:
        subtypes = t.get_args(value_type)
        assert subtypes[0] is str, value_type

        return {
            "type": "object",
            "items": self._process(subtypes[1]),
        }

    def _make_schema_object_id_to_object_id(self, value_type: t.Type) -> Jsonable:
        return {"bsonType": "objectId"}

    def _make_schema_literal_to_str(self, value_type: t.Type) -> Jsonable:
        return {"type": "string"}

    def _make_schema_union(self, value_type: t.Type) -> Jsonable:
        # Convert each subtype to a BSON schema
        sub_schemas = []
        for subtype in t.get_args(value_type):
            # Union is used by Python to represent "Optional"
            if subtype is type(None):
                sub_schemas.append({"type": "null"})
                continue

            sub_schemas.append(self._process(subtype))

        # Prettify the result: instead of `{anyof {type ...} {type ...}}` just
        # create one `type`
        types = []
        bson_types = []
        others = []

        for schema in sub_schemas:
            if len(schema) == 1:
                # Standard Json Schema type
                try:
                    type_field = schema["type"]
                except KeyError:
                    pass
                else:
                    if isinstance(type_field, list):
                        types.extend(type_field)
                    else:
                        types.append(type_field)

                    continue

                # BSON type
                try:
                    type_field = schema["bsonType"]
                except KeyError:
                    pass
                else:
                    if isinstance(type_field, list):
                        bson_types.extend(type_field)
                    else:
                        bson_types.append(type_field)

                    continue

            # General case
            others.append(schema)

        # Create new, merged schemas
        sub_schemas = []

        if bson_types:
            sub_schemas.append({"bsonType": types + bson_types})
        elif types:
            sub_schemas.append({"type": types})

        sub_schemas.extend(others)

        if len(sub_schemas) == 1:
            return sub_schemas[0]

        return {"anyOf": sub_schemas}

    def _make_schema_any(self, value_type: t.Type) -> Jsonable:
        return {}

    def _make_schema_field_by_field_no_child(
        self,
        value_type: t.Type,
    ) -> Jsonable:
        doc_field_names = []
        doc_properties = {}
        result = {
            "type": "object",
            "properties": doc_properties,
            "additionalProperties": False,
        }

        for field_py_name, field_type in utils.get_class_attributes_recursive(
            value_type
        ).items():
            field_doc_name = self._python_attribute_name_to_doc_name(field_py_name)

            doc_field_names.append(field_doc_name)
            doc_properties[field_doc_name] = self._process(field_type)

        # The `required` field may only be present if it contains at least one value
        if doc_field_names:
            result["required"] = doc_field_names

        return result

    def _make_schema_field_by_field_as_child(
        self,
        value_type: t.Type,
    ) -> Jsonable:
        assert inspect.isclass(value_type), value_type

        # Case: Class or one of its children
        #
        # Create the schemas for all allowable classes
        sub_schemas = []
        for subtype in utils.all_subclasses(value_type, True):
            schema: t.Any = self._make_schema_field_by_field_no_child(subtype)
            assert schema["type"] == "object", schema

            schema["properties"]["type"] = {
                "enum": [self._python_class_name_to_doc_name(subtype.__name__)]
            }

            required = schema.setdefault("required", [])
            required.insert(0, "type")

            sub_schemas.append(schema)

        # Create the final, combined schema
        if len(sub_schemas) == 1:
            return sub_schemas[0]
        else:
            return {"anyOf": sub_schemas}

    def _make_schema_flag_enum(self, value_type: t.Type[enum.Flag]) -> Jsonable:
        return {
            "type": "array",
            "items": {
                "enum": [
                    self._python_enum_name_to_doc_name(variant.name)  # type: ignore
                    for variant in value_type
                ],
            },
        }

    def _make_schema_enum(self, value_type: t.Type[enum.Enum]) -> Jsonable:
        return {
            "enum": [
                self._python_enum_name_to_doc_name(variant.name)
                for variant in value_type
            ],
        }

    _schema_builders: dict[
        t.Type, t.Callable[[MongodbSchemaConverter, t.Type], Jsonable]
    ] = {
        bool: _make_schema_bool_to_bool,
        int: _make_schema_int_to_int,
        float: _make_schema_float_to_float,
        bytes: _make_schema_bytes_to_bytes,
        str: _make_schema_str_to_str,
        datetime: _make_schema_datetime_to_datetime,
        timedelta: _make_schema_timedelta_to_float,
        list: _make_schema_list_to_list,
        dict: _make_schema_dict_to_dict,
        t.Union: _make_schema_union,
        t.Any: _make_schema_any,
        ObjectId: _make_schema_object_id_to_object_id,
        t.Literal: _make_schema_literal_to_str,
        tuple: _make_schema_tuple_to_list,
        set: _make_schema_set_to_list,
        Path: _make_schema_path_to_str,
        type(Path()): _make_schema_path_to_str,
        uuid.UUID: _make_schema_uuid_to_uuid,
    }  # type: ignore
