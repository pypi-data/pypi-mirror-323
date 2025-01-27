"""Common utils made available for use throughout this project."""

import logging
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Final

from . import click_logging
from .click_logging import setup_logging

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence
    from logging import Logger
    from typing import Final, TypedDict

    from git import PathLike

__all__: "Sequence[str]" = (
    "PROJECT_ROOT",
    "FileExclusionMethod",
    "format_exception_to_log_message",
    "get_all_markdown_files",
    "get_all_original_files",
    "setup_logging",
)

if TYPE_CHECKING:

    class CCFTContextObj(TypedDict, total=False):
        verbosity: int


logger: "Final[Logger]" = logging.getLogger("ccft-pymarkdown")
logger.disabled = True

CONVERSION_FILE_SUFFIX: "Final[str]" = ".ccft-original"


class FileExclusionMethod(Enum):
    """
    Choice of file exclusion methods.

    Selectable based on '--with-git' and '--exclude-hidden' CLI options.
    """

    WITH_GIT = object()
    MANUAL_EXCLUSION_RULES = object()  # noqa: PIE796
    NOTHING = object()  # noqa: PIE796

    @classmethod
    def from_flags(cls, *, with_git: bool, exclude_hidden: bool) -> "FileExclusionMethod":
        """Choose the correct default file exclusion method base on the given CLI options."""
        if with_git:
            return cls.WITH_GIT

        if exclude_hidden:
            return cls.MANUAL_EXCLUSION_RULES

        return cls.NOTHING


def _get_project_root() -> "Path":
    try:
        from git import InvalidGitRepositoryError, Repo
    except ImportError:
        logger.warning("GitPython is not installed, falling back to naive file exploration")
        return _get_readme_root()

    try:
        raw_project_root: PathLike | str | None = Repo(
            Path.cwd(),
            search_parent_directories=True,
        ).working_tree_dir
    except InvalidGitRepositoryError:
        raw_project_root = None

    if raw_project_root is None:
        return _get_readme_root()

    return Path(raw_project_root)


def _get_readme_root() -> "Path":
    project_root: Path = Path.cwd()

    for _ in range(8):
        if any(
            (path.stem == "README" and path.is_file())
            or (path.name == ".git" and path.is_dir())
            for path in project_root.iterdir()
        ):
            return project_root

        project_root = project_root.parent

    # noinspection PyFinal
    NO_ROOT_DIRECTORY_MESSAGE: Final[str] = "Could not locate project root directory."
    raise FileNotFoundError(NO_ROOT_DIRECTORY_MESSAGE)


PROJECT_ROOT: "Final[Path]" = _get_project_root()


def _manual_check_hidden(file_path: "Path") -> bool:
    is_hidden: bool = file_path.stem.startswith(".") or any(
        parent.name.startswith(".") for parent in file_path.parents
    )

    if is_hidden:
        logger.debug("File %s is hidden", file_path)

    return is_hidden


def _naive_get_markdown_files(root: "Path", *, exclude_hidden: bool) -> "Iterable[Path]":
    if exclude_hidden and not click_logging.LOGGED_USE_GIT_PYTHON:
        click_logging.LOGGED_USE_GIT_PYTHON = True
        logger.warning(
            "Searching for files using manual hidden rules can lead to unexpected behavior"
        )
        logger.info(
            "It is recommended to instead ensure the [git-python] extra is installed "
            "and provide the path to a git repository"
        )

    return (
        file_path
        for file_path in root.rglob("*.md")
        if not exclude_hidden or not _manual_check_hidden(file_path.relative_to(root))
    )


def get_markdown_files(
    root: "Path" = PROJECT_ROOT,
    file_exclusion_method: FileExclusionMethod = FileExclusionMethod.WITH_GIT,
) -> "Iterable[Path]":
    """
    Retrieve all Markdown files under the root path that may require cleaning.

    Files are excluded based on the 'file_exclusion_method'.
    """
    if not root.is_dir():
        raise NotADirectoryError(root)

    if file_exclusion_method is not FileExclusionMethod.WITH_GIT:
        return _naive_get_markdown_files(
            root,
            exclude_hidden=file_exclusion_method is FileExclusionMethod.MANUAL_EXCLUSION_RULES,
        )

    try:
        from git import InvalidGitRepositoryError, Repo
    except ImportError:
        logger.warning(
            (
                "GitPython is not installed, "
                "falling back to naive file exploration of directory '%s'"
            ),
            root,
        )
        return _naive_get_markdown_files(root, exclude_hidden=True)

    try:
        repo_root: Repo = Repo(root)
    except InvalidGitRepositoryError:
        logger.debug("Path '%s' is not a git repository, using naive file exploration", root)
        return _naive_get_markdown_files(root, exclude_hidden=True)

    logger.debug("Using git for file exploration of directory '%s'", root)

    return (
        file_path
        for file_entry in repo_root.index.entries
        if (file_path := root / file_entry[0]).suffix == ".md"
    )


def get_original_files(root: "Path" = PROJECT_ROOT) -> "Iterable[Path]":
    """Retreive all previously saved original files that require restoration."""
    if not root.is_dir():
        raise NotADirectoryError(root)

    return root.rglob(f"*{CONVERSION_FILE_SUFFIX}")


def format_exception_to_log_message(exception: Exception) -> str:
    """Convert a low-level exception into a useable log message."""
    message: str = str(exception).strip("\n\r\t -.")

    if message:
        return message

    if isinstance(exception, FileNotFoundError):
        return "File does not exist"

    if isinstance(exception, FileExistsError):
        return "File already exists"

    NO_EXCEPTION_MESSAGE: Final[str] = "Exception did not contain a loggable message."
    raise ValueError(NO_EXCEPTION_MESSAGE)
