from typing import Iterable, Optional

from griffe import Function

from griffe_generics.types import Expression


def annotations_from_function(function: Function) -> Iterable[Optional[Expression]]:
    for parameter in function.parameters:
        yield str(parameter.annotation)

    yield str(function.returns)
