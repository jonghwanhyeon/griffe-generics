from __future__ import annotations

from griffe import Extensions, temporary_visited_package
from utils import annotations_from_function

from griffe_generics import GenericsExtension


def test_generics() -> None:
    with temporary_visited_package(
        "package",
        modules={
            "__init__.py": """
                from typing import Generic, TypeVar

                A = TypeVar("A")
                B = TypeVar("B")
                C = TypeVar("C")


                class Parent(Generic[A, B, C]):
                    def p1(self, a: A) -> A:
                        return a

                    def p2(self, b: B) -> B:
                        return b

                    def p3(self, c: C) -> C:
                        return c


                class Intermediate(Parent[int, float, A], Generic[A]):
                    def i1(self, a: A) -> A:
                        return a


                class Child(Intermediate[Parent[int, float, int]]):
                    pass
            """,
        },
        extensions=Extensions(GenericsExtension()),
    ) as package:
        Parent = package["Parent"]
        assert tuple(annotations_from_function(Parent["p1"])) == ("None", "A", "A")
        assert tuple(annotations_from_function(Parent["p2"])) == ("None", "B", "B")
        assert tuple(annotations_from_function(Parent["p3"])) == ("None", "C", "C")

        Intermediate = package["Intermediate"]
        assert tuple(annotations_from_function(Intermediate["p1"])) == ("None", "int", "int")
        assert tuple(annotations_from_function(Intermediate["p2"])) == ("None", "float", "float")
        assert tuple(annotations_from_function(Intermediate["p3"])) == ("None", "A", "A")
        assert tuple(annotations_from_function(Intermediate["i1"])) == ("None", "A", "A")

        Child = package["Child"]
        assert tuple(annotations_from_function(Child["p1"])) == ("None", "int", "int")
        assert tuple(annotations_from_function(Child["p2"])) == ("None", "float", "float")
        assert tuple(annotations_from_function(Child["p3"])) == (
            "None",
            "Parent[int, float, int]",
            "Parent[int, float, int]",
        )
        assert tuple(annotations_from_function(Child["i1"])) == (
            "None",
            "Parent[int, float, int]",
            "Parent[int, float, int]",
        )


def test_complex_generics() -> None:
    with temporary_visited_package(
        "package",
        modules={
            "__init__.py": """
                from typing import Any, Callable, Generic, TypeVar

                A = TypeVar("A")
                B = TypeVar("B")
                C = TypeVar("C")
                D = TypeVar("D")
                E = TypeVar("E")
                F = TypeVar("F")


                class Alpha(Generic[A, B, C]):
                    def a1(self, a: A) -> A:
                        return a

                    def a2(self, b: B) -> B:
                        return b

                    def a3(self, c: C) -> C:
                        return c


                class Bravo(Alpha[C, B, A], Generic[A, B, C]):
                    def b1(self, a: A) -> A:
                        return a

                    def b2(self, b: B) -> B:
                        return b

                    def b3(self, c: C) -> C:
                        return c


                class Charlie(Bravo[D, D, E], Generic[D, E]):
                    def c1(self, d: D) -> D:
                        return d

                    def c2(self, e: E) -> E:
                        return e


                class Delta(Generic[A, B]):
                    def d1(self, a: A) -> A:
                        return a

                    def d2(self, b: B) -> B:
                        return b


                class Echo(Charlie[int, Callable[..., Any]], Delta[str, int]):
                    pass
            """,
        },
        extensions=Extensions(GenericsExtension()),
    ) as package:
        Alpha = package["Alpha"]
        assert tuple(annotations_from_function(Alpha["a1"])) == ("None", "A", "A")
        assert tuple(annotations_from_function(Alpha["a2"])) == ("None", "B", "B")
        assert tuple(annotations_from_function(Alpha["a3"])) == ("None", "C", "C")

        Bravo = package["Bravo"]
        assert tuple(annotations_from_function(Bravo["a1"])) == ("None", "C", "C")
        assert tuple(annotations_from_function(Bravo["a2"])) == ("None", "B", "B")
        assert tuple(annotations_from_function(Bravo["a3"])) == ("None", "A", "A")
        assert tuple(annotations_from_function(Bravo["b1"])) == ("None", "A", "A")
        assert tuple(annotations_from_function(Bravo["b2"])) == ("None", "B", "B")
        assert tuple(annotations_from_function(Bravo["b3"])) == ("None", "C", "C")

        Charlie = package["Charlie"]
        assert tuple(annotations_from_function(Charlie["a1"])) == ("None", "E", "E")
        assert tuple(annotations_from_function(Charlie["a2"])) == ("None", "D", "D")
        assert tuple(annotations_from_function(Charlie["a3"])) == ("None", "D", "D")
        assert tuple(annotations_from_function(Charlie["b1"])) == ("None", "D", "D")
        assert tuple(annotations_from_function(Charlie["b2"])) == ("None", "D", "D")
        assert tuple(annotations_from_function(Charlie["b3"])) == ("None", "E", "E")
        assert tuple(annotations_from_function(Charlie["c1"])) == ("None", "D", "D")
        assert tuple(annotations_from_function(Charlie["c2"])) == ("None", "E", "E")

        Delta = package["Delta"]
        assert tuple(annotations_from_function(Delta["d1"])) == ("None", "A", "A")
        assert tuple(annotations_from_function(Delta["d2"])) == ("None", "B", "B")

        Echo = package["Echo"]
        assert tuple(annotations_from_function(Echo["a1"])) == ("None", "Callable[..., Any]", "Callable[..., Any]")
        assert tuple(annotations_from_function(Echo["a2"])) == ("None", "int", "int")
        assert tuple(annotations_from_function(Echo["a3"])) == ("None", "int", "int")
        assert tuple(annotations_from_function(Echo["b1"])) == ("None", "int", "int")
        assert tuple(annotations_from_function(Echo["b2"])) == ("None", "int", "int")
        assert tuple(annotations_from_function(Echo["b3"])) == ("None", "Callable[..., Any]", "Callable[..., Any]")
        assert tuple(annotations_from_function(Echo["c1"])) == ("None", "int", "int")
        assert tuple(annotations_from_function(Echo["c2"])) == ("None", "Callable[..., Any]", "Callable[..., Any]")
        assert tuple(annotations_from_function(Echo["d1"])) == ("None", "str", "str")
        assert tuple(annotations_from_function(Echo["d2"])) == ("None", "int", "int")
