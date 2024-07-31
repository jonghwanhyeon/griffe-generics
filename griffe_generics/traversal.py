from __future__ import annotations

import dataclasses
from collections import deque
from typing import Any, Callable, Iterable, Optional, Sequence, TypeVar

from griffe import Alias, Expr, Object
from typing_extensions import TypeGuard

from griffe_generics.predicates import instance_of
from griffe_generics.types import ChildrenIterable, Expression, Predicate

T = TypeVar("T")
O = TypeVar("O", bound=Object)  # noqa: E741
E = TypeVar("E", bound=Expression)


def iter_children_from_object(object: Object) -> ChildrenIterable[Object]:
    for key in object.members.keys():
        value = object.get_member(key)

        if isinstance(value, Alias):
            continue

        yield key, value


def iter_children_from_expression(expression: Expression) -> ChildrenIterable[Expression]:
    if isinstance(expression, str):
        return

    for field in dataclasses.fields(expression):
        if field.name == "parent":
            continue

        value = getattr(expression, field.name)
        if isinstance(value, (str, Expr, Sequence)):
            yield field.name, value


def walk(node: T, iter_children: Callable[[T], ChildrenIterable[T]]) -> Iterable[T]:
    queue: deque[T] = deque([node])

    while queue:
        left = queue.popleft()

        for _, child in iter_children(left):
            if isinstance(child, Sequence):
                queue.extend(child)
            else:
                queue.append(child)

        yield left


def default_predicate(value: Any) -> TypeGuard[Any]:
    return True


def walk_objects(object: Object, predicate: Predicate[O] = default_predicate) -> Iterable[O]:
    for node in walk(object, iter_children_from_object):
        if predicate(node):
            yield node


def walk_objects_of(object: Object, type: type[O]) -> Iterable[O]:
    return walk_objects(object, predicate=instance_of(type))


def walk_expressions(expression: Expression, predicate: Predicate[E] = default_predicate) -> Iterable[E]:
    for node in walk(expression, iter_children_from_expression):
        if predicate(node):
            yield node


def walk_expressions_of(expression: Expression, type: type[E]) -> Iterable[E]:
    return walk_expressions(expression, predicate=instance_of(type))


def descendant(expression: Expression, type: type[E]) -> Optional[E]:
    try:
        return next(iter(walk_expressions_of(expression, type)))
    except StopIteration:
        return None


def chain(expression: E, field: str) -> Iterable[E]:
    node = expression
    while type(node) is type(expression):
        yield node
        node = getattr(node, field)
