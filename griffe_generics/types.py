from typing import Any, Callable, Iterable, Sequence, Tuple, TypeVar, Union

from griffe import Expr
from typing_extensions import TypeGuard

T = TypeVar("T")
R = TypeVar("R")

ChildrenIterable = Iterable[Tuple[str, Union[T, Sequence[T]]]]

Predicate = Callable[[Any], TypeGuard[R]]

Expression = Union[str, Expr]
