"""Console entry point for CCFT-PyMarkdown."""

import importlib.metadata
import importlib.util
import logging
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import click

from . import utils
from ._clean import clean
from ._restore import restore
from .context_manager import CleanCustomFormattedTables
from .utils import PROJECT_ROOT, FileExclusionMethod

if TYPE_CHECKING:
    from collections.abc import Sequence
    from collections.abc import Set as AbstractSet
    from logging import Logger
    from typing import Final


__all__: "Sequence[str]" = ("run",)

logger: "Final[Logger]" = logging.getLogger("ccft_pymarkdown")


def _callback_verbose(ctx: click.Context, _param: click.Parameter, value: object) -> None:
    if not isinstance(value, int):
        INVALID_OPTION_TYPE_MESSAGE: Final[str] = (
            f"Expected {int}, got {type(value)} for 'verbose' value."
        )
        raise TypeError(INVALID_OPTION_TYPE_MESSAGE)

    if ctx.obj is None:
        ctx.obj = {"verbosity": value}
    elif not isinstance(ctx.obj, dict):
        INVALID_CONTEXT_TYPE_MESSAGE: Final[str] = f"Invalid 'ctx.obj' type: {type(ctx.obj)}."
        raise TypeError(INVALID_CONTEXT_TYPE_MESSAGE)
    else:
        ctx.obj["verbosity"] = value

    utils.setup_logging(value)


def _callback_mutually_exclusive_verbose_and_quiet(
    ctx: click.Context, _param: click.Parameter, value: object
) -> None:
    if not isinstance(value, bool):
        INVALID_OPTION_TYPE_MESSAGE: Final[str] = (
            f"Expected bool, got {type(value)} for 'quiet' value."
        )
        raise TypeError(INVALID_OPTION_TYPE_MESSAGE)

    if not value:
        return

    if ctx.obj is None:
        ctx.obj = {"verbosity": 0}
    elif not isinstance(ctx.obj, dict):
        INVALID_CONTEXT_TYPE_MESSAGE: Final[str] = f"Invalid 'ctx.obj' type: {type(ctx.obj)}."
        raise TypeError(INVALID_CONTEXT_TYPE_MESSAGE)

    if ctx.obj.get("verbosity", 0) > 1:
        raise click.BadOptionUsage(
            option_name="quiet",
            message="cannot use option '--quiet' in addition to '--verbose'.",
            ctx=ctx,
        )

    ctx.obj["verbosity"] = -1

    utils.setup_logging(-1)


def _callback_validate_with_git(
    ctx: click.Context, _param: click.Parameter, value: object
) -> bool:
    if not isinstance(value, bool):
        INVALID_OPTION_TYPE_MESSAGE: Final[str] = (
            f"Expected bool, got {type(value)} for 'with-git' value."
        )
        raise TypeError(INVALID_OPTION_TYPE_MESSAGE)

    if importlib.util.find_spec("git") is None and value:
        raise click.BadOptionUsage(
            option_name="with-git",
            message="Cannot use '--with-git' when the [git-python] extra is not installed.",
            ctx=ctx,
        )

    return value


def _callback_validate_exclude_hidden(
    ctx: click.Context, _param: click.Parameter, value: object
) -> bool:
    WITH_GIT: Final[object] = ctx.params["with_git"]
    if not isinstance(WITH_GIT, bool):
        raise TypeError

    if value is None:
        return not WITH_GIT

    if not isinstance(value, bool):
        INVALID_OPTION_TYPE_MESSAGE: Final[str] = (
            f"Expected bool, got {type(value)} for 'exclude-hidden' value."
        )
        raise TypeError(INVALID_OPTION_TYPE_MESSAGE)

    if WITH_GIT and value:
        raise click.BadOptionUsage(
            option_name="with-git",
            message="Cannot use '--exclude-hidden' if using '--with-git'.",
            ctx=ctx,
        )

    if not WITH_GIT and not value:
        click.confirm(
            text=(
                "Scanning all files without git "
                "and without using manual hidden-file exclusion rules "
                f"can lead to cleaning many additional files{
                    ' (For example files within the .venv/ directory)'
                    if PROJECT_ROOT.joinpath('.venv').is_dir()
                    else ''
                }. Are you sure you wish to continue scanning all files?"
            ),
            abort=True,
            err=False,
        )

    return value


def _callback_dry_run(_ctx: click.Context, _param: click.Parameter, value: object) -> bool:
    if not isinstance(value, bool):
        INVALID_OPTION_TYPE_MESSAGE: Final[str] = (
            f"Expected bool, got {type(value)} for 'dry-run' value."
        )
        raise TypeError(INVALID_OPTION_TYPE_MESSAGE)

    if value:
        logger.info(
            "Running in dry-run mode; "
            "although log messages will be sent about editing/deleting files, "
            "the filesystem will not be affected"
        )

    return value


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    help=f"{
        (
            importlib.metadata.metadata('CCFT-PyMarkdown').get('Summary') or 'CCFT-PyMarkdown'
        ).strip('.')
    }.",
)
@click.version_option(None, "-V", "--version")
@click.option(
    "-v",
    "--verbose",
    count=True,
    callback=_callback_verbose,
    expose_value=False,
)
@click.option(
    "-q",
    "--quiet",
    is_flag=True,
    callback=_callback_mutually_exclusive_verbose_and_quiet,
    expose_value=False,
)
def run() -> None:
    """Run cli entry-point."""


@run.command(name="clean", help="Clean custom-formatted tables from all Markdown files.")
@click.version_option(None, "-V", "--version")
@click.argument(
    "files",
    nargs=-1,
    type=click.Path(exists=True, file_okay=True, dir_okay=True, path_type=Path),
)
@click.option(
    "--with-git/--no-git",
    "--use-git/--without-git",
    is_flag=True,
    default=(importlib.util.find_spec("git") is not None),
    show_default=True,
    help=(
        "Whether to use local repository information (including `.gitignore` file) "
        "to identify which files to clean when recursing directories. "
        "Note: '--with-git' is not available when the [git-python] extra is not installed."
    ),
    is_eager=True,
    callback=_callback_validate_with_git,
)
@click.option(
    "--exclude-hidden/--no-exclude-hidden",
    is_flag=True,
    default=None,
    help=(
        "Use manual exclusion rules to filter out any hidden files "
        "when recursing directories. "
        "Note: these rules are unstable and it is recommended to instead "
        "install the [git-python] extra with a complete repository and `.gitignore` file. "
        "[default: exclude-hidden if using '--no-git', otherwise no-exclude-hidden]"
    ),
    callback=_callback_validate_exclude_hidden,
)
@click.option("--dry-run/--no-dry-run", "-d/", default=False, callback=_callback_dry_run)
@click.pass_context
def _clean(
    ctx: click.Context,
    files: "Sequence[Path]",
    *,
    with_git: bool,
    exclude_hidden: bool,
    dry_run: bool,
) -> None:
    import inflect

    INFLECT_ENGINE: Final[inflect.engine] = inflect.engine()

    file_exclusion_method: FileExclusionMethod = FileExclusionMethod.from_flags(
        with_git=with_git, exclude_hidden=exclude_hidden
    )

    if not files:
        logger.debug("No files explicitly selected, recursing from current working directory")

    clean_tables_file_exists_error: FileExistsError
    try:
        cleaned_files: AbstractSet[Path] = clean(
            files
            if files
            else utils.get_markdown_files(file_exclusion_method=file_exclusion_method),
            file_exclusion_method,
            dry_run=dry_run,
        )

    except FileExistsError as clean_tables_file_exists_error:
        logger.error(str(clean_tables_file_exists_error).strip("\n\r\t -."))  # noqa: TRY400
        logger.info(
            "Use `%s restore` to first restore the files to their original state",
            ctx.parent.info_name if ctx.parent is not None else ctx.info_name,
        )
        return

    logger.info(
        "No files required cleaning"
        if len(cleaned_files) == 0
        else (
            f"Running without '--dry-run' would have cleaned the following {
                INFLECT_ENGINE.plural_noun('file', len(cleaned_files))
            }: {', '.join(f"'{file_path}'" for file_path in cleaned_files)}"
        )
        if dry_run
        else f"Successfully cleaned {INFLECT_ENGINE.no('file', len(cleaned_files))}",
    )


@run.command(name="restore", help="Restore custom-formatted tables from all Markdown files.")
@click.version_option(None, "-V", "--version")
@click.option("--dry-run/--no-dry-run", "-d/", default=False, callback=_callback_dry_run)
def _restore(*, dry_run: bool) -> None:
    import inflect

    INFLECT_ENGINE: Final[inflect.engine] = inflect.engine()

    restored_files: AbstractSet[Path] = restore(utils.get_original_files(), dry_run=dry_run)

    logger.info(
        "No files required restoring"
        if len(restored_files) == 0
        else (
            f"Running without '--dry-run' would have restored the following {
                INFLECT_ENGINE.plural_noun('file', len(restored_files))
            }: {', '.join(f"'{file_path}'" for file_path in restored_files)}"
        )
        if dry_run
        else f"Successfully restored {INFLECT_ENGINE.no('file', len(restored_files))}",
    )


@run.command(
    name="scan-all", help="Lint all Markdown files after removing custom-formatted tables."
)
@click.version_option(None, "-V", "--version")
@click.option(
    "--with-git/--no-git",
    "--use-git/--without-git",
    is_flag=True,
    default=(importlib.util.find_spec("git") is not None),
    show_default=True,
    help=(
        "Whether to use local repository information (including `.gitignore` file) "
        "to identify which files to clean when recursing directories. "
        "Note: '--with-git' is not available when the [git-python] extra is not installed."
    ),
    is_eager=True,
    callback=_callback_validate_with_git,
)
@click.option(
    "--exclude-hidden/--no-exclude-hidden",
    is_flag=True,
    default=None,
    help=(
        "Use manual exclusion rules to filter out any hidden files "
        "when recursing directories. "
        "Note: these rules are unstable and it is recommended to instead "
        "install the [git-python] extra with a complete repository and `.gitignore` file. "
        " [default: exclude-hidden if using '--no-git', otherwise no-exclude-hidden]"
    ),
    callback=_callback_validate_exclude_hidden,
)
@click.pass_context
def _scan_all(ctx: click.Context, *, with_git: bool, exclude_hidden: bool) -> None:
    clean_tables_file_exists_error: FileExistsError
    try:
        with CleanCustomFormattedTables(
            file_exclusion_method=FileExclusionMethod.from_flags(
                with_git=with_git, exclude_hidden=exclude_hidden
            )
        ) as custom_formatted_tables_cleaner:
            if not custom_formatted_tables_cleaner.cleaned_files:
                logger.info("No files to lint")
            else:
                subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "pymarkdown",
                        "--return-code-scheme",
                        "minimal",
                        "scan",
                        *(
                            str(file_path)
                            for file_path in custom_formatted_tables_cleaner.cleaned_files
                        ),
                    ],
                    check=True,
                )

    except FileExistsError as clean_tables_file_exists_error:
        logger.error(str(clean_tables_file_exists_error).strip("\n\r\t -."))  # noqa: TRY400
        logger.info(
            "Use `%s restore` to first restore the files to their original state",
            ctx.parent.info_name if ctx.parent is not None else ctx.info_name,
        )
        return
