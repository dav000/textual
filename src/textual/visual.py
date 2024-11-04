from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import cached_property, lru_cache
from marshal import loads
from typing import Any, Iterable, Protocol, cast

import rich.repr
from rich.console import JustifyMethod, OverflowMethod
from rich.style import Style as RichStyle

from textual.color import TRANSPARENT, Color
from textual.strip import Strip


class SupportsTextualize(Protocol):
    """An object that supports the textualize protocol."""

    def textualize(self, obj: object) -> Visual | None: ...


def textualize(obj: object) -> Visual | None:
    """Get a visual instance from an object.

    Args:
        obj: An object.

    Returns:
        A Visual instance to render the object, or `None` if there is no associated visual.
    """
    textualize = getattr(obj, "textualize", None)
    if textualize is None:
        return None
    visual = textualize()
    if not isinstance(visual, Visual):
        return None
    return visual


@rich.repr.auto
@dataclass(frozen=True)
class Style:
    """Represent a content style (color and other attributes)."""

    background: Color = TRANSPARENT
    foreground: Color = TRANSPARENT
    bold: bool | None = None
    dim: bool | None = None
    italic: bool | None = None
    underline: bool | None = None
    strike: bool | None = None
    link: str | None = None
    _meta: bytes | None = None

    def __rich_repr__(self) -> rich.repr.Result:
        yield None, self.background
        yield None, self.foreground
        yield "bold", self.bold, None
        yield "dim", self.dim, None
        yield "italic", self.italic, None
        yield "underline", self.underline, None
        yield "strike", self.strike, None

    @lru_cache(maxsize=1024)
    def __add__(self, other: object) -> Style:
        if not isinstance(other, Style):
            return NotImplemented
        new_style = Style(
            self.background + other.background,
            self.foreground if other.foreground.is_transparent else other.foreground,
            self.bold if other.bold is None else other.bold,
            self.dim if other.dim is None else other.dim,
            self.italic if other.italic is None else other.italic,
            self.underline if other.underline is None else other.underline,
            self.strike if other.strike is None else other.strike,
            self.link if other.link is None else other.link,
            self._meta if other._meta is None else other._meta,
        )
        return new_style

    @cached_property
    def rich_style(self) -> RichStyle:
        return RichStyle(
            color=(self.background + self.foreground).rich_color,
            bgcolor=self.background.rich_color,
            bold=self.bold,
            dim=self.dim,
            italic=self.italic,
            underline=self.underline,
            strike=self.strike,
            link=self.link,
            meta=self.meta,
        )

    @cached_property
    def without_color(self) -> Style:
        return Style(
            bold=self.bold,
            dim=self.dim,
            italic=self.italic,
            strike=self.strike,
            link=self.link,
            _meta=self._meta,
        )

    @classmethod
    def combine(cls, styles: Iterable[Style]) -> Style:
        """Add a number of styles and get the result."""
        iter_styles = iter(styles)
        return sum(iter_styles, next(iter_styles))

    @property
    def meta(self) -> dict[str, Any]:
        """Get meta information (can not be changed after construction)."""
        return {} if self._meta is None else cast(dict[str, Any], loads(self._meta))


class Visual(ABC):
    """A Textual 'visual' object.

    Analogous to a Rich renderable, but with support for transparency.

    """

    @abstractmethod
    def render_strips(
        self,
        width: int,
        *,
        height: int | None,
        base_style: Style = Style(),
        justify: JustifyMethod = "left",
        overflow: OverflowMethod = "fold",
        no_wrap: bool = False,
        tab_size: int = 8,
    ) -> list[Strip]:
        """Render the visual in to an iterable of strips.

        Args:
            base_style: The base style.
            width: Width of desired render.
            height: Height of desired render.

        Returns:
            An iterable of Strips.
        """

    @abstractmethod
    def get_optimal_width(self, tab_size: int = 8) -> int:
        """Get ideal width of the renderable to display its content.

        Args:
            tab_size: Size of tabs.

        Returns:
            A width in cells.

        """

    @abstractmethod
    def get_minimal_width(self, tab_size: int = 8) -> int:
        """Get the minimal width (the small width that doesn't lose information).

        Args:
            tab_size: Size of tabs.

        Returns:
            A width in cells.
        """

    @abstractmethod
    def get_height(self, width: int) -> int:
        """Get the height of the visual if rendered with the given width.

        Returns:
            A height in lines.
        """
