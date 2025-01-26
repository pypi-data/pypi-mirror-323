"""
Given a uniserde data model, generates the Rust equivalent for it. This assumes
Rust uses the `serde` library for serialization / deserialization. It doesn't
produce perfect code, but the results are typically a good starting point for
writing your own, final version.

The code will be written to `uniserde_models.rs` in the current working
directory.
"""

import enum
import inspect
import typing as t
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

import uniserde

PYTHON_TYPES_TO_RUST_TYPES = {
    bool: "bool",
    int: "i32",
    float: "f64",
    str: "String",
    bytes: "Vec<u8>",
    datetime: "DateTime<Utc>",
    timedelta: "Duration",
    uuid.UUID: "Uuid",
}


@dataclass
class SubModel:
    id: str
    timestamp: datetime
    reference_to_other_instance: str
    amount: int
    description: str
    events: list[str]


@dataclass
class Model:
    name: str
    subs: list[SubModel]
    sets: set[str]
    timestamp: datetime
    deleted: bool
    duration: float


def get_all_model_classes(value_type: t.Type) -> t.Iterable[type]:
    """
    Given a model class, returns an iterable over all model classes that must be
    generated.
    """
    type_key = uniserde.utils.get_type_key(value_type)

    # These types already exist in Rust and need no further processing
    if type_key in {bool, int, float, str, bytes, datetime}:
        return

    args = t.get_args(value_type)

    # Classes are themselves models, and may contain more
    if inspect.isclass(type_key) and type_key not in {tuple, list, set, dict}:
        yield type_key

        for _, field_type in uniserde.utils.get_class_attributes_recursive(
            type_key
        ).items():
            yield from get_all_model_classes(field_type)

    # Recur into the args
    for arg in args:
        yield from get_all_model_classes(arg)


def write_rust_struct(cls: t.Type, out: t.TextIO) -> None:
    """
    Given a model class, writes the Rust equivalent as a struct.
    """
    assert inspect.isclass(cls), cls

    out.write(
        f"#[derive(Debug, Serialize, Deserialize)]\npub struct {cls.__name__} {{\n"
    )

    for ii, (field_name, field_py_type) in enumerate(
        uniserde.utils.get_class_attributes_recursive(cls).items()
    ):
        if ii != 0:
            out.write("\n")

        # Special cases
        if field_py_type is datetime:
            out.write(f'    #[serde(deserialize_with = "deserialize_iso8601")]\n')
            out.write(f"    {field_name}: DateTime<Utc>,\n")
            continue

        if field_py_type is timedelta:
            out.write(
                f'    #[serde(deserialize_with = "deserialize_duration_from_seconds")]\n'
            )
            out.write(f"    {field_name}: Duration,\n")

        # General case
        field_rust_type = convert_type_to_rust(field_py_type)
        out.write(f"    {field_name}: {field_rust_type},\n")

    out.write("}\n")


def write_rust_enum(cls: t.Type[enum.Enum], out: t.TextIO) -> None:
    """
    Given an enum class, writes the Rust equivalent as an enum.
    """
    assert issubclass(cls, enum.Enum), cls

    out.write(f"#[derive(Debug, Serialize, Deserialize)]\npub enum {cls.__name__} {{\n")

    for member in cls:
        out.write(f"    {member.name},\n")

    out.write("}\n")


def convert_type_to_rust(py_type: type) -> str:
    """
    Given a Python type, returns the equivalent Rust type.
    """
    type_key = uniserde.utils.get_type_key(py_type)
    args = t.get_args(py_type)

    # Simple lookups
    try:
        return PYTHON_TYPES_TO_RUST_TYPES[type_key]
    except KeyError:
        pass

    # More complex types
    if type_key is list:
        return f"Vec<{convert_type_to_rust(args[0])}>"

    if type_key is tuple:
        return f"({', '.join(convert_type_to_rust(arg) for arg in args)})"

    if type_key is set:
        return f"HashSet<{convert_type_to_rust(args[0])}>"

    if type_key is dict:
        return (
            f"HashMap<{convert_type_to_rust(args[0])}, {convert_type_to_rust(args[1])}>"
        )

    if type_key is t.Union:
        subtype = uniserde.utils.get_optional_subtype(py_type)
        return f"Option<{convert_type_to_rust(subtype)}>"

    if inspect.isclass(type_key):
        return type_key.__name__

    raise ValueError(f"Unsupported type: {py_type}")


def main() -> None:
    # Find all models that need porting
    all_model_classes = set(get_all_model_classes(Model))

    with Path("uniserde_models.rs").open("w") as f:
        # Common header code
        f.write(
            """
use serde::{Serialize, Deserialize};
use chrono::{DateTime, Duration, Utc};


fn deserialize_iso8601<'de, D>(deserializer: D) -> Result<DateTime<Utc>, D::Error>
where
    D: Deserializer<'de>,
{
    let s: &str = Deserialize::deserialize(deserializer)?;
    DateTime::parse_from_rfc3339(s)
        .map(|dt| dt.with_timezone(&Utc))
        .map_err(serde::de::Error::custom)
}


fn deserialize_duration_from_seconds<'de, D>(deserializer: D) -> Result<Duration, D::Error>
where
    D: Deserializer<'de>,
{
    let seconds: f64 = Deserialize::deserialize(deserializer)?;
    // Convert seconds (float) to chrono::Duration
    Duration::from_std(std::time::Duration::from_secs_f64(seconds))
        .map_err(serde::de::Error::custom)
}
            """.strip()
            + "\n\n\n"
        )

        # Write the Model Code
        for model_cls in all_model_classes:
            if issubclass(model_cls, enum.Enum):
                write_rust_enum(model_cls, f)
            else:
                write_rust_struct(model_cls, f)

            f.write("\n\n")


if __name__ == "__main__":
    main()
