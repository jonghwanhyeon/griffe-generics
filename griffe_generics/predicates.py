from __future__ import annotations

from typing import Any, TypeVar, Union

from griffe import ExprList, ExprTuple
from typing_extensions import TypeGuard, overload

from griffe_generics.types import Predicate

T = TypeVar("T")
T1 = TypeVar("T1")
T2 = TypeVar("T2")
T3 = TypeVar("T3")


@overload
def instance_of(type: type[T]) -> Predicate[T]: ...
@overload
def instance_of(type: tuple[type[T1], type[T2]]) -> Predicate[Union[T1, T2]]: ...
@overload
def instance_of(type: tuple[type[T1], type[T2], type[T3]]) -> Predicate[Union[T1, T2, T3]]: ...


def instance_of(type: Any) -> Predicate[Any]:
    def predicate(value: Any) -> TypeGuard[Any]:
        return isinstance(value, type)

    return predicate


is_sequence = instance_of((ExprList, ExprTuple))
