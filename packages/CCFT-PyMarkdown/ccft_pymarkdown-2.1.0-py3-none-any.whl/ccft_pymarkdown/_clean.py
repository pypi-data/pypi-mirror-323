"""Perform the cleaning of custom-formatted tables from Markdown files."""

import logging
import shutil
from typing import TYPE_CHECKING

from . import utils
from .utils import CONVERSION_FILE_SUFFIX, FileExclusionMethod

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence
    from collections.abc import Set as AbstractSet
    from logging import Logger
    from pathlib import Path
    from typing import Final, Literal, TextIO


__all__: "Sequence[str]" = ("clean",)

logger: "Final[Logger]" = logging.getLogger("ccft-pymarkdown")


if TYPE_CHECKING:

    class CopiedPath(Path): ...


def _copy_file(original_file_path: "Path") -> tuple["CopiedPath", "Path"]:
    copied_path: CopiedPath = shutil.copy2(
        original_file_path,
        original_file_path.parent / f"{original_file_path.name}{CONVERSION_FILE_SUFFIX}",
    )
    return copied_path, original_file_path


def _clean_single_file(original_file_path: "Path") -> None:
    """Clean custom-formatted tables within a Markdown file at a given path."""
    new_file_path: CopiedPath
    new_file_path, original_file_path = _copy_file(original_file_path)

    original_file: TextIO
    new_file: TextIO
    with original_file_path.open("r") as original_file, new_file_path.open("w") as new_file:
        line: str
        for line in original_file:
            new_file.write(
                line.replace(
                    "<br>* ",
                    "<br> ",
                )
                .replace(
                    "<br/>* ",
                    "<br/> ",
                )
                .replace(
                    "| * ",
                    "| ",
                ),
            )


def _check_file(file_path: "Path") -> "Literal[True]":
    logger.debug("Checking file '%s'", file_path)

    if file_path.suffix != ".md":
        INVALID_FILE_SUFFIX_MESSAGE: Final[str] = "File is not a markdown file."
        raise ValueError(INVALID_FILE_SUFFIX_MESSAGE)

    if not file_path.is_file():
        raise FileNotFoundError

    original_file_path: Path = file_path.parent / f"{file_path.name}{CONVERSION_FILE_SUFFIX}"
    if original_file_path.exists():
        ORIGINAL_FILE_ALREADY_EXISTS_MESSAGE: str = (
            "Cannot clean custom-formatted tables from Markdown files: "
            f"'{original_file_path}' already exists."
        )
        raise FileExistsError(ORIGINAL_FILE_ALREADY_EXISTS_MESSAGE)

    return True


def clean(
    files: "Iterable[Path]",
    file_exclusion_method: FileExclusionMethod = FileExclusionMethod.WITH_GIT,
    *,
    skip_errors: bool = False,
    dry_run: bool = False,
) -> "AbstractSet[Path]":
    """Clean custom-formatted tables within each given Markdown file."""
    cleaned_files: set[Path] = set()

    file_path: Path
    for file_path in files:
        if file_path in cleaned_files:
            logger.debug("Skipping file '%s': already processed", file_path)
            continue

        if file_path.is_dir():
            logger.debug("Recursing into directory '%s'", file_path)
            cleaned_files.update(
                clean(
                    utils.get_markdown_files(file_path, file_exclusion_method),
                    file_exclusion_method,
                    skip_errors=skip_errors,
                    dry_run=dry_run,
                )
            )
            continue

        e: Exception
        try:
            _check_file(file_path)
        except (FileNotFoundError, FileExistsError, OSError) as e:
            if not skip_errors:
                raise e from e

            logger.error(  # noqa: TRY400
                "Skipping '%s': %s", file_path, utils.format_exception_to_log_message(e)
            )
            continue

        logger.debug("File '%s' passed pre-cleaning checks", file_path)

        if not dry_run:
            try:
                _clean_single_file(file_path)
            except (OSError, ValueError, RuntimeError, TypeError) as e:
                logger.error(  # noqa: TRY400
                    "Error while cleaning '%s': %s",
                    file_path,
                    utils.format_exception_to_log_message(e),
                )
                continue

        cleaned_files.add(file_path)

        logger.debug("Successfully cleaned file: '%s'", file_path)

    return cleaned_files
