from __future__ import annotations


import uniserde
from datetime import datetime, timezone
from dataclasses import dataclass
from bson import ObjectId


@dataclass
class Person:
    id: ObjectId
    name: str
    birth_date: datetime


betty = Person(
    id=ObjectId(),
    name="Betty",
    birth_date=datetime(year=1988, month=12, day=1, tzinfo=timezone.utc),
)

serde = uniserde.JsonSerde()
print(serde.as_json(betty))


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
