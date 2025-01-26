from __future__ import annotations

import base64
from datetime import datetime, timezone
from pathlib import Path

import pytest

import tests.models as models
import uniserde


def test_serialize_exact_variant_1() -> None:
    serde = uniserde.JsonSerde()

    value_fresh = models.TestClass.create_variant_1()

    value_json = serde.as_json(value_fresh)

    assert value_json == {
        "id": 1,
        "val_bool": value_fresh.val_bool,
        "val_int": value_fresh.val_int,
        "val_float": value_fresh.val_float,
        "val_bytes": base64.b64encode(value_fresh.val_bytes).decode("utf-8"),
        "val_str": value_fresh.val_str,
        "val_datetime": value_fresh.val_datetime.isoformat(),
        "val_timedelta": value_fresh.val_timedelta.total_seconds(),
        "val_tuple": list(value_fresh.val_tuple),
        "val_list": value_fresh.val_list,
        "val_set": list(value_fresh.val_set),
        "val_dict": value_fresh.val_dict,
        "val_optional": value_fresh.val_optional,
        "val_old_union_optional_1": value_fresh.val_old_union_optional_1,
        "val_old_union_optional_2": value_fresh.val_old_union_optional_2,
        "val_new_union_optional_1": value_fresh.val_new_union_optional_1,
        "val_new_union_optional_2": value_fresh.val_new_union_optional_2,
        "val_any": value_fresh.val_any,
        "val_object_id": str(value_fresh.val_object_id),
        "val_literal": value_fresh.val_literal,
        "val_enum": "one",
        "val_flag": ["one", "two"],
        "val_path": str(value_fresh.val_path),
        "val_uuid": str(value_fresh.val_uuid),
        "val_class": {
            "foo": value_fresh.val_class.foo,
            "bar": value_fresh.val_class.bar,
        },
    }


@pytest.mark.parametrize("lazy", [False, True])
def test_round_trip_variant_1(lazy: bool) -> None:
    serde = uniserde.JsonSerde(lazy=lazy)

    value_fresh = models.TestClass.create_variant_1()

    value_json = serde.as_json(value_fresh)

    value_round_trip = serde.from_json(value_json, as_type=models.TestClass)

    assert value_fresh == value_round_trip


@pytest.mark.parametrize("lazy", [False, True])
def test_round_trip_variant_2(lazy: bool) -> None:
    serde = uniserde.JsonSerde(lazy=lazy)

    value_fresh = models.TestClass.create_variant_2()

    value_json = serde.as_json(value_fresh)

    value_round_trip = serde.from_json(value_json, as_type=models.TestClass)

    assert value_fresh == value_round_trip


@pytest.mark.parametrize("lazy", [False, True])
def test_round_trip_parent(lazy: bool) -> None:
    serde = uniserde.JsonSerde(lazy=lazy)

    value_fresh = models.ParentClass.create_parent_variant_1()

    value_json = serde.as_json(value_fresh)

    value_round_trip = serde.from_json(value_json, as_type=models.ParentClass)

    assert value_fresh == value_round_trip


@pytest.mark.parametrize("lazy", [False, True])
def test_round_trip_child(lazy: bool) -> None:
    serde = uniserde.JsonSerde(lazy=lazy)

    value_fresh = models.ChildClass.create_child_variant_1()

    value_json = serde.as_json(value_fresh)

    value_round_trip = serde.from_json(value_json, as_type=models.ChildClass)

    assert value_fresh == value_round_trip


@pytest.mark.parametrize("lazy", [False, True])
def test_round_trip_child_as_parent(lazy: bool) -> None:
    serde = uniserde.JsonSerde(lazy=lazy)

    value_fresh = models.ChildClass.create_child_variant_1()

    value_json = serde.as_json(value_fresh)

    value_round_trip = serde.from_json(value_json, as_type=models.ParentClass)

    assert isinstance(value_round_trip, models.ChildClass)
    assert value_fresh == value_round_trip


def test_kw_only() -> None:
    serde = uniserde.JsonSerde()

    value_fresh = models.ClassWithKwOnly(1, bar=2)

    value_json = serde.as_json(value_fresh)

    assert isinstance(value_json, dict)
    assert "foo" in value_json
    assert "bar" in value_json
    assert "_" not in value_json
    assert len(value_json) == 2
    assert value_json["foo"] == 1
    assert value_json["bar"] == 2


@pytest.mark.parametrize("lazy", [False, True])
def test_datetime_needs_timezone(lazy: bool) -> None:
    serde = uniserde.JsonSerde(lazy=lazy)

    with pytest.raises(uniserde.SerdeError, match="is missing a timezone."):
        serde.from_json("2020-01-01T01:02:03.000004", as_type=datetime)


@pytest.mark.parametrize("lazy", [False, True])
def test_datetime_parses_timezone(lazy: bool) -> None:
    serde = uniserde.JsonSerde(lazy=lazy)

    value_parsed = serde.from_json("2020-01-01T01:02:03.000004Z", as_type=datetime)

    assert isinstance(value_parsed, datetime)
    assert value_parsed.tzinfo is not None
    assert value_parsed == datetime(2020, 1, 1, 1, 2, 3, 4, timezone.utc)


@pytest.mark.parametrize("lazy", [False, True])
def test_int_is_float(lazy: bool) -> None:
    serde = uniserde.JsonSerde(lazy=lazy)

    serde.from_json(1, as_type=float)


@pytest.mark.parametrize("lazy", [False, True])
def test_paths_are_made_absolute(lazy: bool) -> None:
    serde = uniserde.JsonSerde(lazy=lazy)

    path_relative = Path.home() / "folder"
    path_relative = path_relative.relative_to(Path.home())
    assert not path_relative.is_absolute()

    path_absolute = path_relative.absolute()
    assert path_absolute.is_absolute()

    path_serialized = serde.as_json(path_relative)
    assert path_serialized == str(path_absolute)

    path_deserialized = serde.from_json(path_serialized, as_type=Path)
    assert path_deserialized == path_absolute


def test_catch_superfluous_value() -> None:
    serde = uniserde.JsonSerde()

    with pytest.raises(uniserde.SerdeError, match="Object contains superfluous fields"):
        serde.from_json(
            {
                "foo": 1,
                "bar": "one",
                "invalidKey": True,
            },
            models.SimpleClass,
        )


def test_overridden_as_json() -> None:
    serde = uniserde.JsonSerde()

    value_fresh = models.ClassWithStaticmethodOverrides.create()

    value_json = serde.as_json(value_fresh)

    assert value_json == {
        "value": "overridden during serialization",
        "format": "json",
    }


@pytest.mark.parametrize("lazy", [False, True])
def test_overridden_from_json_staticmethod(lazy: bool) -> None:
    serde = uniserde.JsonSerde(lazy=lazy)

    value_json = {
        "value": "stored value",
        "format": "json",
    }

    value_parsed = serde.from_json(
        value_json, as_type=models.ClassWithStaticmethodOverrides
    )

    assert isinstance(value_parsed, models.ClassWithStaticmethodOverrides)
    assert value_parsed.value == "overridden during deserialization"
    assert value_parsed.format == "json"


@pytest.mark.parametrize("lazy", [False, True])
def test_overridden_from_json_classmethod(lazy: bool) -> None:
    serde = uniserde.JsonSerde(lazy=lazy)

    value_json = {
        "value": "stored value",
        "format": "json",
    }

    value_parsed = serde.from_json(
        value_json, as_type=models.ClassWithClassmethodOverrides
    )

    assert isinstance(value_parsed, models.ClassWithClassmethodOverrides)
    assert value_parsed.value == "overridden during deserialization"
    assert value_parsed.format == "json"


def test_serialize_with_custom_handlers() -> None:
    """
    Provides custom handlers for some types during serialization.
    """
    serde = uniserde.JsonSerde(
        custom_serializers={
            int: lambda serde, val, as_type: val + 1,
        },
    )

    value_fresh = models.SimpleClass(1, "one")

    value_json = serde.as_json(value_fresh)

    assert value_json == {
        "foo": 2,
        "bar": "one",
    }


@pytest.mark.parametrize("lazy", [False, True])
def test_deserialize_with_custom_handlers(lazy: bool) -> None:
    """
    Provides custom handlers for some types during deserialization.
    """
    serde = uniserde.JsonSerde(
        lazy=lazy,
        custom_deserializers={
            int: lambda serde, val, as_type: val + 1,
        },
    )

    value_json = {
        "foo": 1,
        "bar": "one",
    }

    value_parsed = serde.from_json(value_json, as_type=models.SimpleClass)

    assert value_parsed == models.SimpleClass(2, "one")


def test_is_not_lazy_if_not_requested() -> None:
    """
    Make sure that when asking for eager deserialization, we get eager
    deserialization.
    """
    serde = uniserde.JsonSerde(lazy=False)

    value_fresh = models.TestClass.create_variant_1()
    value_json = serde.as_json(value_fresh)
    value_parsed = serde.from_json(value_json, as_type=models.TestClass)

    assert "_uniserde_remaining_fields_" not in vars(value_parsed)


def test_is_lazy_if_requested() -> None:
    """
    Make sure that when asking for eager deserialization, we get eager
    deserialization.
    """
    serde = uniserde.JsonSerde(lazy=True)

    value_fresh = models.TestClass.create_variant_1()
    value_json = serde.as_json(value_fresh)
    value_parsed = serde.from_json(value_json, as_type=models.TestClass)

    assert "_uniserde_remaining_fields_" in vars(value_parsed)
