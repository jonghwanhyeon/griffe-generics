from __future__ import annotations

from typing import Callable, Sequence, TypeVar

from griffe_generics.predicates import instance_of
from griffe_generics.traversal import iter_children_from_expression
from griffe_generics.types import ChildrenIterable, Expression, Predicate

T = TypeVar("T")
P = TypeVar("P")
E = TypeVar("E", bound=Expression)


def transform(
    node: T,
    iter_children: Callable[[T], ChildrenIterable[T]],
    predicate: Predicate[P],
    func: Callable[[P], T],
) -> T:
    if predicate(node):
        transformed = func(node)
        if transformed is not node:
            return transform(transformed, iter_children=iter_children, predicate=predicate, func=func)

    for key, child in iter_children(node):  # type: ignore
        if isinstance(child, Sequence):
            if isinstance(child, str):
                continue

            child = [transform(item, iter_children=iter_children, predicate=predicate, func=func) for item in child]
        else:
            child = transform(child, iter_children=iter_children, predicate=predicate, func=func)

        setattr(node, key, child)

    return node  # type: ignore


def transform_expression(
    expression: Expression,
    predicate: Predicate[E],
    func: Callable[[E], Expression],
) -> Expression:
    return transform(
        node=expression,
        iter_children=iter_children_from_expression,
        predicate=predicate,
        func=func,
    )


def transform_expression_of(
    expression: Expression,
    type: type[E],
    func: Callable[[E], Expression],
) -> Expression:
    return transform_expression(
        expression,
        predicate=instance_of(type),
        func=func,
    )
