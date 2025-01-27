"""Perform the restoration of Markdown files that had custom-formatted tables cleaned."""

import logging
from typing import TYPE_CHECKING

from . import utils
from .utils import CONVERSION_FILE_SUFFIX

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence
    from collections.abc import Set as AbstractSet
    from logging import Logger
    from pathlib import Path
    from typing import Final, Literal

__all__: "Sequence[str]" = ("restore",)

logger: "Final[Logger]" = logging.getLogger("ccft_pymarkdown")


def _check_file(file_path: "Path") -> "Literal[True]":
    logger.debug("Checking file '%s'", file_path)

    if file_path.suffix != CONVERSION_FILE_SUFFIX:
        INVALID_FILE_SUFFIXES_MESSAGE: Final[str] = (
            "File is not a previously converted markdown file."
        )
        raise ValueError(INVALID_FILE_SUFFIXES_MESSAGE)

    if not file_path.is_file():
        raise FileNotFoundError

    return True


def restore(files: "Iterable[Path]", *, dry_run: bool = False) -> "AbstractSet[Path]":
    """Return given Markdown files to their original state before cleaning."""
    restored_files: set[Path] = set()

    file_path: Path
    for file_path in files:
        if file_path in restored_files:
            logger.debug("Skipping file '%s': already processed", file_path)
            continue

        if file_path.is_dir():
            logger.debug("Recursing into directory '%s'", file_path)
            restored_files.update(restore(utils.get_original_files(file_path)))
            continue

        _check_file(file_path)

        logger.debug("File '%s' passed pre-restoring checks", file_path)

        restored_file_path: Path = file_path.parent / file_path.stem
        if restored_file_path.exists():
            logger.debug("Deleting cleaned file: '%s'", restored_file_path)
            if not dry_run:
                restored_file_path.unlink()

        if not dry_run:
            file_path.rename(file_path.parent / file_path.stem)

        restored_files.add(file_path)

        logger.debug("Successfully restored file: '%s'", file_path)

    return restored_files
