"""Custom context manager to clean custom-formatted tables only inside the context."""

from typing import TYPE_CHECKING

from . import utils
from ._clean import clean
from ._restore import restore
from .utils import CONVERSION_FILE_SUFFIX, FileExclusionMethod

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence
    from collections.abc import Set as AbstractSet
    from pathlib import Path
    from types import TracebackType
    from typing import Final, Self

__all__: "Sequence[str]" = ("CleanCustomFormattedTables",)


class CleanCustomFormattedTables:
    """Context manager to clean custom-formatted tables only inside the context."""

    def __init__(
        self,
        files: "Iterable[Path] | None" = None,
        file_exclusion_method: FileExclusionMethod = FileExclusionMethod.WITH_GIT,
        *,
        skip_errors: bool = False,
    ) -> None:
        """Initialise the context manager with the given selected files to clean."""
        self.skip_errors: bool = skip_errors
        self.file_exclusion_method: FileExclusionMethod = file_exclusion_method
        self.files: Iterable[Path] = (
            files
            if files is not None
            else utils.get_markdown_files(file_exclusion_method=file_exclusion_method)
        )
        self._cleaned_files: AbstractSet[Path] | None = None
        self._restored_files: AbstractSet[Path] | None = None

    def __enter__(self) -> "Self":
        """Clean custom-formatted tables before entering the context."""
        self._cleaned_files = clean(
            self.files,
            self.file_exclusion_method,
            skip_errors=self.skip_errors,
        )

        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: "TracebackType | None",  # noqa: PYI036
    ) -> None:
        """Restore Markdown files back to their original state."""
        self._restored_files = restore(
            file_path.parent / f"{file_path.name}{CONVERSION_FILE_SUFFIX}"
            for file_path in self.cleaned_files
        )

    @property
    def cleaned_files(self) -> "AbstractSet[Path]":
        """Rerieve the number of cleaned files after entering the context manager."""
        if self._cleaned_files is None:
            CANNOT_VIEW_MESSAGE: Final[str] = (
                "Cannot view 'cleaned_files' until the context manager has been entered."
            )
            raise RuntimeError(CANNOT_VIEW_MESSAGE)

        return self._cleaned_files

    @property
    def restored_files(self) -> "AbstractSet[Path]":
        """Rerieve the number of restored files after exiting the context manager."""
        if self._restored_files is None:
            CANNOT_VIEW_MESSAGE: Final[str] = (
                "Cannot view 'restored_files' until the context manager has been exited."
            )
            raise RuntimeError(CANNOT_VIEW_MESSAGE)

        return self._restored_files
