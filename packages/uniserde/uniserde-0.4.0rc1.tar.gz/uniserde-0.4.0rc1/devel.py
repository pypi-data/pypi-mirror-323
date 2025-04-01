from __future__ import annotations


import uniserde
import uniserde.compat
from datetime import datetime, timezone
import typing as t
import dataclasses
from bson import ObjectId
import tests.models


serde = uniserde.JsonSerde(
    lazy=True,
)

value_fresh = tests.models.TestClass.create_variant_1()

value_json = serde.as_json(value_fresh)

value_parsed = serde.from_json(value_json, as_type=tests.models.TestClass)
print(value_parsed)


raise SystemExit()


from dataclasses import dataclass
import uniserde
import uniserde.codegen
import uuid
import tests.models
import enum


original = tests.models.ClassWithStaticmethodOverrides.create()


print(f"Original: {original}")

serialized = uniserde.as_bson(original)

print(f"Serialized: {serialized}")

deserialized = uniserde.from_bson(serialized, type(original))

print(f"Deserialized: {deserialized}")
