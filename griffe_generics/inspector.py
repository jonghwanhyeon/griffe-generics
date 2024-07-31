from __future__ import annotations

import sys
from dataclasses import dataclass, field
from typing import Iterable, Union

from griffe import Class, ExprName, ExprSubscript, Module

from griffe_generics.models import BoundType, BoundTypes, TypeParameter
from griffe_generics.predicates import is_sequence
from griffe_generics.traversal import descendant, walk_expressions_of, walk_objects_of
from griffe_generics.types import Expression
from griffe_generics.utils import canonical_path_of

_dataclass_options = {}
if sys.version_info >= (3, 10):
    _dataclass_options["slots"] = True


@dataclass(frozen=True, **_dataclass_options)
class GenericsContext:
    type_parameters_by_class: dict[str, list[TypeParameter]] = field(default_factory=dict)
    bound_types_by_class: dict[str, dict[str, BoundType]] = field(default_factory=dict)

    def is_generic_class(self, cls: Union[Expression, Class]) -> bool:
        return canonical_path_of(cls) in self.type_parameters_by_class

    def type_parameters_from_class(self, cls: Class) -> Iterable[TypeParameter]:
        for base_cls in [cls, *cls.mro()]:
            yield from self.type_parameters_by_class.get(base_cls.canonical_path, [])

    def bound_types_from_class(self, cls: Class) -> BoundTypes:
        bound_types = BoundTypes()
        for base_cls in [cls, *cls.mro()]:
            bound_types.update(self.bound_types_by_class.get(base_cls.canonical_path, {}).items())

        return bound_types


class GenericsInspector:
    def inspect(self, module: Module) -> GenericsContext:
        context = GenericsContext()

        for cls in walk_objects_of(module, type=Class):
            parameters = [*self._inspect_type_parameters(cls)]
            if parameters:
                context.type_parameters_by_class[cls.canonical_path] = [*parameters]

        for cls in walk_objects_of(module, type=Class):
            bound_types = dict(self._inspect_bound_types(cls, context))
            if bound_types:
                context.bound_types_by_class[cls.canonical_path] = bound_types

        return context

    def _inspect_type_parameters(self, cls: Class) -> Iterable[TypeParameter]:
        for base in cls.bases:
            for subscript in walk_expressions_of(base, type=ExprSubscript):
                if subscript.canonical_name not in {"Generic", "Protocol"}:
                    continue

                for name in walk_expressions_of(subscript.slice, type=ExprName):
                    yield TypeParameter(name=name, scope=cls)

    def _inspect_bound_types(self, cls: Class, context: GenericsContext) -> Iterable[tuple[str, BoundType]]:
        for base in cls.bases:
            subscript = descendant(base, ExprSubscript)
            if subscript is None:
                continue

            left, slice = subscript.left, subscript.slice

            path = canonical_path_of(left)
            if not context.is_generic_class(path):
                continue

            expressions = slice.elements if is_sequence(slice) else [slice]
            for parameter, expression in zip(context.type_parameters_by_class[path], expressions):
                yield parameter.type_path, BoundType(expression=expression, scope=cls)
