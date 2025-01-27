"""Suppress custom-formatted table errors when linting using PyMarkdown in Markdown files."""

from typing import TYPE_CHECKING

from ._clean import clean
from ._restore import restore
from .console import run
from .context_manager import CleanCustomFormattedTables

if TYPE_CHECKING:
    from collections.abc import Sequence

__all__: "Sequence[str]" = (
    "CleanCustomFormattedTables",
    "clean",
    "restore",
    "run",
)
