from __future__ import annotations

import sys
from collections import UserDict
from dataclasses import dataclass

from griffe import ExprName, Object

from griffe_generics.types import Expression
from griffe_generics.utils import path_of, type_path_of

_dataclass_options = {}
if sys.version_info >= (3, 10):
    _dataclass_options["slots"] = True


@dataclass(frozen=True, **_dataclass_options)
class TypeParameter:
    name: ExprName
    scope: Object

    @property
    def type_path(self) -> str:
        return type_path_of(self.name, self.scope)

    @property
    def path(self) -> str:
        return f"{self.name.path}@{self.scope.name}"

    def __repr__(self) -> str:
        return f"{type(self).__name__}(path={self.path!r})"


@dataclass(frozen=True, **_dataclass_options)
class BoundType:
    expression: Expression
    scope: Object

    @property
    def type_path(self) -> str:
        return type_path_of(self.expression, self.scope)

    @property
    def path(self) -> str:
        return f"{path_of(self.expression)}@{self.scope.name}"

    def __repr__(self) -> str:
        return f"{type(self).__name__}(path={self.path!r})"


if sys.version_info >= (3, 9):
    TypeOfBoundTypes = UserDict[str, BoundType]
else:
    TypeOfBoundTypes = UserDict


class BoundTypes(TypeOfBoundTypes):
    def resolve(self, expression: Expression, scope: Object) -> tuple[Expression, Object]:
        type_path = type_path_of(expression, scope)
        if type_path not in self.data:
            return expression, scope

        while type_path in self.data:
            bound_type = self.data[type_path]
            type_path = bound_type.type_path

        return bound_type.expression, bound_type.scope
