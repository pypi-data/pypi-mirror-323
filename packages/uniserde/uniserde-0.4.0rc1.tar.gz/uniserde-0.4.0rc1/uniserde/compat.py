"""
Compatibility module for loading/writing old-style uniserde JSON & BSON.

This module is semi-public. Feel free to use it, but it may change or be dropped
without a deprecation period or semver version bump.
"""

import typing as t
import warnings

import uniserde
from uniserde import Bsonable, BsonDoc, Jsonable, JsonDoc

from . import case_convert

T = t.TypeVar("T")


# Serializer/deserializer instances compatible with the old-school format
def _all_lower_to_camel_case_with_id_exception(name: str) -> str:
    """
    Convert all lower case names to camel case, except for the string "id",
    which becomes "_id".
    """
    if name == "id":
        return "_id"

    return case_convert.all_lower_to_camel_case(name)


OLD_SCHOOL_JSON_SERDE = uniserde.JsonSerde(
    python_attribute_name_to_doc_name=case_convert.all_lower_to_camel_case,
    python_class_name_to_doc_name=case_convert.upper_camel_case_to_camel_case,
    python_enum_name_to_doc_name=case_convert.all_upper_to_camel_case,
    lazy=False,
)


OLD_SCHOOL_BSON_SERDE = uniserde.BsonSerde(
    python_attribute_name_to_doc_name=_all_lower_to_camel_case_with_id_exception,
    python_class_name_to_doc_name=case_convert.upper_camel_case_to_camel_case,
    python_enum_name_to_doc_name=case_convert.all_upper_to_camel_case,
    lazy=False,
)


# Functions to help with updating old-school documents
def bulk_update_json(
    old_document: t.Iterable[JsonDoc],
    as_type: t.Type,
    *,
    new_serde: uniserde.JsonSerde | None,
) -> t.Iterable[JsonDoc]:
    """
    Reads a sequence of old-school JSON documents and returns them as a sequence
    of new-style JSON documents (in the same order).

    If `new_serde` is not provided, a default instance of `JsonSerde` will be
    used.
    """
    # Prepare the serde instances
    if new_serde is None:
        new_serde = uniserde.JsonSerde()

    # Walk the documents
    for doc in old_document:
        # Deserialize the old document
        obj = OLD_SCHOOL_JSON_SERDE.from_json(doc, as_type=as_type)

        # Serialize the new document
        new_doc = new_serde.as_json(obj)
        assert isinstance(new_doc, dict)

        yield new_doc


def bulk_update_bson(
    old_document: t.Iterable[BsonDoc],
    as_type: t.Type,
    *,
    new_serde: uniserde.BsonSerde | None,
) -> t.Iterable[BsonDoc]:
    """
    Reads a sequence of old-school BSON documents and returns them as a sequence
    of new-style BSON documents (in the same order).

    If `new_serde` is not provided, a default instance of `BsonSerde` will be
    used.
    """
    # Prepare the serde instances
    if new_serde is None:
        new_serde = uniserde.BsonSerde()

    # Walk the documents
    for doc in old_document:
        # Deserialize the old document
        obj = OLD_SCHOOL_BSON_SERDE.from_bson(doc, as_type=as_type)

        # Serialize the new document
        new_doc = new_serde.as_bson(obj)
        assert isinstance(new_doc, dict)

        yield new_doc


async def update_mongodb_collection(
    motor_collection,
    as_type: t.Type,
    *,
    new_serde: uniserde.BsonSerde | None = None,
) -> None:
    """
    Updates all documents in a MongoDB collection from the old-school format to
    the new-school format.

    If `new_serde` is not provided, a default instance of `BsonSerde` will be
    used.
    """

    # Prepare the serde instances
    if new_serde is None:
        new_serde = uniserde.BsonSerde()

    # Walk the documents
    async for doc in motor_collection.find():
        # Deserialize the old document
        obj = OLD_SCHOOL_BSON_SERDE.from_bson(doc, as_type=as_type)

        # Serialize the new document
        new_doc = new_serde.as_bson(obj)
        assert isinstance(new_doc, dict)

        # Update the document
        await motor_collection.replace_one({"_id": doc["_id"]}, new_doc)


# Keep the old API alive
def as_json(
    value: t.Any,
    *,
    as_type: t.Optional[t.Type] = None,
    custom_serializers: dict[t.Type, t.Callable[[t.Any], t.Any]] = {},
) -> JsonDoc:
    warnings.warn("This method is deprecated.", DeprecationWarning)
    assert not custom_serializers, "Custom serializers are not supported here"
    return OLD_SCHOOL_JSON_SERDE.as_json(value, as_type=as_type)


def from_json(
    document: t.Any,
    as_type: t.Type,
    *,
    custom_deserializers: dict[t.Type, t.Callable[[Jsonable], t.Any]] = {},
    lazy: bool = False,
) -> t.Any:
    warnings.warn("This method is deprecated.", DeprecationWarning)
    assert not custom_deserializers, "Custom deserializers are not supported here"
    return OLD_SCHOOL_JSON_SERDE.from_json(document, as_type)


def as_bson(
    value: t.Any,
    *,
    as_type: t.Optional[t.Type] = None,
    custom_serializers: dict[t.Type, t.Callable[[t.Any], t.Any]] = {},
) -> BsonDoc:
    warnings.warn("This method is deprecated.", DeprecationWarning)
    assert not custom_serializers, "Custom serializers are not supported here"
    return OLD_SCHOOL_BSON_SERDE.as_bson(value, as_type=as_type)


def from_bson(
    document: t.Any,
    as_type: t.Type,
    *,
    custom_deserializers: dict[t.Type, t.Callable[[Bsonable], t.Any]] = {},
    lazy: bool = False,
) -> t.Any:
    warnings.warn("This method is deprecated.", DeprecationWarning)
    assert not custom_deserializers, "Custom deserializers are not supported here"
    return OLD_SCHOOL_BSON_SERDE.from_bson(document, as_type)


class Serde:
    def __init_subclass__(cls) -> None:
        warnings.warn(
            "This class is deprecated - there is no direct replacement in the new API.",
            DeprecationWarning,
        )

    def as_bson(
        self,
        *,
        as_type: t.Optional[t.Type] = None,
        custom_serializers: dict[t.Type, t.Callable[[t.Any], t.Any]] = {},
    ) -> BsonDoc:
        return as_bson(self, as_type=as_type, custom_serializers=custom_serializers)

    def as_json(
        self,
        *,
        as_type: t.Optional[t.Type] = None,
        custom_serializers: dict[t.Type, t.Callable[[t.Any], t.Any]] = {},
    ) -> JsonDoc:
        return as_json(self, as_type=as_type, custom_serializers=custom_serializers)

    @classmethod
    def from_bson(
        cls: t.Type[T],
        document: BsonDoc,
        *,
        custom_deserializers: dict[t.Type, t.Callable[[t.Any], t.Any]] = {},
        lazy: bool = False,
    ) -> T:
        return from_bson(
            document, as_type=cls, custom_deserializers=custom_deserializers, lazy=lazy
        )

    @classmethod
    def from_json(
        cls: t.Type[T],
        document: JsonDoc,
        *,
        custom_deserializers: dict[t.Type, t.Callable[[t.Any], t.Any]] = {},
        lazy: bool = False,
    ) -> T:
        warnings.warn(
            "This method is deprecated. Use the module-level `from_json` function instead.",
            DeprecationWarning,
        )
        return from_json(
            document, as_type=cls, custom_deserializers=custom_deserializers, lazy=lazy
        )

    @classmethod
    def as_mongodb_schema(
        cls,
        *,
        custom_handlers: dict[t.Type, t.Callable[[t.Any], t.Any]] = {},
    ) -> t.Any:
        raise NotImplementedError(
            "This method is not supported in the compatibility API"
        )
