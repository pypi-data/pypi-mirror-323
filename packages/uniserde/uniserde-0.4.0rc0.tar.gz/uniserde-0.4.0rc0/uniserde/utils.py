from __future__ import annotations

import dataclasses
import inspect
import sys
import types
import typing as t

__all__ = [
    "as_child",
    "get_class_attributes_recursive",
]


T = t.TypeVar("T")


# Caches results of the `get_type_key` function to speed up lookups.
TYPE_KEY_CACHE: dict[t.Type, t.Type] = {}


def as_child(cls: t.Type[T]) -> t.Type[T]:
    """
    Marks the class to be serialized as one of its children. This will add an
    additional "type" field in the result, so the child can be deserialized
    properly.

    This decorator applies to children of the class as well, i.e. they will also
    be serialized with the "type" field.
    """
    assert inspect.isclass(cls), cls
    cls._uniserde_serialize_as_child_ = cls  # type: ignore
    return cls


def should_serialize_as_child(cls: t.Type) -> bool:
    """
    Checks whether the given class should be serialized as a child, i.e. it, or
    any parent has been marked with the `as_child` decorator.
    """
    assert inspect.isclass(cls), cls
    return hasattr(cls, "_uniserde_serialize_as_child_")


def get_type_key(cls: t.Type) -> t.Type:
    """
    Given a type, derive the key to use in caches. This effectively standardizes
    the type, by e.g. converting new-style unions to old-style (`a | b` ->
    `Union[a, b]`).
    """
    # Is this type already in the cache?
    try:
        return TYPE_KEY_CACHE[cls]
    except KeyError:
        pass

    # See what `get_origin` can do
    result: t.Any = t.get_origin(cls)

    if result is None:
        result = cls

    # Convert new-style unions to old-style
    if result is types.UnionType:
        result = t.Union

    # Cache the result
    TYPE_KEY_CACHE[cls] = result

    # Pass through the rest
    return result


def all_subclasses(cls: t.Type, include_class: bool) -> t.Iterable[t.Type]:
    """
    Yields all classes directly or indirectly inheriting from `cls`. Does not
    perform any sort of cycle checks. If `include_class` is `True`, the class
    itself is also yielded.
    """

    if include_class:
        yield cls

    for subclass in cls.__subclasses__():
        yield from all_subclasses(subclass, True)


def _get_class_attributes_local(
    cls: t.Type,
    result: dict[str, t.Type],
) -> None:
    """
    Gets all annotated attributes in the given class, without considering any
    parent classes. Applies the same rules as `get_class_attributes_recursive`.

    Instead of returning a result, the attributes are added to the given
    dictionary. If the dictionary already contains an attribute, it is not
    overwritten.
    """
    assert inspect.isclass(cls), cls

    # Get all annotated attributes
    try:
        annotations = cls.__annotations__
    except AttributeError:
        return

    if not isinstance(annotations, dict):
        return

    # Process them individually
    global_ns = sys.modules[cls.__module__].__dict__
    local_ns = vars(cls)

    for name, hint in annotations.items():
        # Because we're going in method resolution order, any previous
        # definitions win
        if name in result:
            continue

        # Resolve string annotations
        if isinstance(hint, str):
            try:
                hint = eval(hint, global_ns, local_ns)
            except NameError:
                raise ValueError(
                    f"Could not resolve string annotation `{hint}` in {cls.__name__}.{name}. Are you missing an import?"
                )

        # By convention, `dataclasses.KW_ONLY` is used as though it were a
        # type hint, but it's not actually valid for that.
        if hint is dataclasses.KW_ONLY:
            continue

        # Convert new-style unions to old-style ones
        if isinstance(hint, types.UnionType):
            subresult = t.Union[t.get_args(hint)]

        # Other types can stay as they are
        else:
            subresult = hint

        # Store the result
        result[name] = subresult  # type: ignore


def get_class_attributes_recursive(cls: t.Type) -> dict[str, t.Type]:
    """
    Returns the names and types of all attributes in the given class, including
    inherited ones. Attributes are determined from type hints, with some custom
    logic applied:

    - fields annotated with `dataclasses.KW_ONLY` are silently dropped

    - New-style unions are converted to old-style (`types.UnionType` ->
      `t.Union`).
    """
    assert inspect.isclass(cls), cls

    result: dict[str, t.Type] = {}

    for subcls in cls.__mro__:
        _get_class_attributes_local(subcls, result)

    return result


def get_optional_subtype(typ: t.Type) -> t.Type:
    """
    Given a `Union` type hint, return the one type that is not `None`.

    ## Raises

    `ValueError`: If the type hint is not a `Union` type hint with exactly one
        `None` and one non-`None` subtype.
    """
    assert t.get_origin(typ) is t.Union, typ

    # Split into `None` and non-`None` subtypes
    n_nones: int = 0
    non_nones: list[t.Type] = []

    for arg in t.get_args(typ):
        if arg is type(None):
            n_nones += 1
        else:
            non_nones.append(arg)

    if n_nones != 1 or len(non_nones) != 1:
        raise ValueError(
            f"General `Union` types are not supported - only `Optional` types are. The type should have exactly one `None` subtype and one other, not {typ}."
        )

    return non_nones[0]
