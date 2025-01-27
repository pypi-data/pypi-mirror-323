"""Substitution."""

from __future__ import annotations

import typing
from abc import ABC, abstractmethod

if typing.TYPE_CHECKING:
    from generate.nodes import Node
else:
    Node = typing.Any


class Substitutor(ABC):
    """Substitutor."""

    @abstractmethod
    def substitute(self, code: str, variable: str, bracketed: bool = True) -> str:
        """Substitute."""

    @abstractmethod
    def loop_targets(
        self,
        variable: str,
    ) -> typing.Dict[str, typing.Generator[Substitutor, None, None]]:
        """Get list of loop targets."""


def replace(
    content: str,
    subs: typing.List[typing.Tuple[str, typing.Callable]],
    bracketed: bool = True,
) -> str:
    """Make multiple replacements."""
    if bracketed:
        for a, b in subs:
            if f"{{{{{a}}}}}" in content:
                content = content.replace(f"{{{{{a}}}}}", b())
    else:
        for a, b in subs:
            if a in content:
                content = content.replace(a, b())
    return content


class Float(Substitutor):
    """Substitutor for a floating point number."""

    def __init__(self, value):
        """Initialise."""
        self.value = value

    def substitute(self, code: str, variable: str, bracketed: bool = True) -> str:
        """Substitute."""
        return replace(
            code,
            [
                (f"{variable}", lambda: f"{self.value}"),
            ],
            bracketed,
        )

    def loop_targets(
        self,
        variable: str,
    ) -> typing.Dict[str, typing.Generator[Substitutor, None, None]]:
        """Get list of loop targets."""
        return {}


class IndexedFloat(Substitutor):
    """Substitutor for a floating point number in an array."""

    def __init__(self, value, index):
        """Initialise."""
        self.value = value
        self.index = index

    def substitute(self, code: str, variable: str, bracketed: bool = True) -> str:
        """Substitute."""
        return replace(
            code,
            [
                (f"{variable}", lambda: f"{self.value}"),
                (f"{variable}.index", lambda: f"{self.index}"),
            ],
            bracketed,
        )

    def loop_targets(
        self,
        variable: str,
    ) -> typing.Dict[str, typing.Generator[Substitutor, None, None]]:
        """Get list of loop targets."""
        return {}
