from typing import Optional

from griffe import Attribute, Class, ExprName, Extension, Function, Module, Object

from griffe_generics.inspector import GenericsContext, GenericsInspector
from griffe_generics.models import BoundTypes
from griffe_generics.transforms import transform_expression_of
from griffe_generics.traversal import walk_objects_of
from griffe_generics.types import Expression
from griffe_generics.utils import deepcopy


class GenericsExtension(Extension):
    _context: GenericsContext

    def on_package_loaded(self, *, pkg: Module) -> None:
        self._context = GenericsInspector().inspect(pkg)

        for cls in walk_objects_of(pkg, type=Class):
            self._handle_class(cls)

    def _handle_class(self, cls: Class) -> None:
        bound_types = self._context.bound_types_from_class(cls)
        for base_cls in reversed(cls.mro()):
            for key, member in base_cls.members.items():
                if key in cls.members:
                    continue

                if isinstance(member, Function):
                    member = self._resolve_function(member, base_cls, bound_types=bound_types)
                elif isinstance(member, Attribute):
                    member = self._resolve_attribute(member, base_cls, bound_types=bound_types)
                else:
                    member = None  # type: ignore[assignment]

                if member is not None:
                    cls.set_member(key, member)

    def _resolve_function(self, function: Function, scope: Object, bound_types: BoundTypes) -> Function:
        function = deepcopy(function, shared={"parent"})

        for parameter in function.parameters:
            parameter.annotation = self._resolve_annotation(parameter.annotation, scope, bound_types)

        function.returns = self._resolve_annotation(function.returns, scope, bound_types)

        return function

    def _resolve_attribute(self, attribute: Attribute, scope: Object, bound_types: BoundTypes) -> Attribute:
        attribute = deepcopy(attribute, shared={"parent"})
        attribute.annotation = self._resolve_annotation(attribute.annotation, scope, bound_types)
        return attribute

    def _resolve_annotation(
        self, annotation: Optional[Expression], scope: Object, bound_types: BoundTypes
    ) -> Optional[Expression]:
        if annotation is None:
            return None

        context: list[Object] = [scope]

        def func(name: ExprName) -> Expression:
            resolved, scope = bound_types.resolve(name, context[-1])
            context.append(scope)
            return resolved

        return transform_expression_of(annotation, type=ExprName, func=func)
