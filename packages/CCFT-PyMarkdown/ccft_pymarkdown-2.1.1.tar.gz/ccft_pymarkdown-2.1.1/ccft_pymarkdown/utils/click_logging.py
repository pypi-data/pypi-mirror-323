"""Logging setup for use in combination with the click framework."""

import logging
from typing import TYPE_CHECKING, override

import click

if TYPE_CHECKING:
    from collections.abc import Sequence
    from logging import Logger
    from typing import Final


__all__: "Sequence[str]" = (
    "LOGGED_USE_GIT_PYTHON",
    "ClickHandler",
    "ColourFormatter",
    "setup_logging",
)


logger: "Final[Logger]" = logging.getLogger("ccft_pymarkdown")

LOGGED_USE_GIT_PYTHON: bool = False


class ColourFormatter(logging.Formatter):
    """Simple log message formatter that applies click's colour styling."""

    @override
    def format(self, record: logging.LogRecord) -> str:
        if not record.exc_info:
            PREFIX: Final[str] = click.style(
                f"{record.levelname.upper()}: ",
                fg=(
                    "red"
                    if record.levelno >= logging.ERROR
                    else "yellow"
                    if record.levelno >= logging.WARNING
                    else "blue"
                ),
            )
            return "\n".join(f"{PREFIX}{line}" for line in super().format(record).splitlines())

        return super().format(record)


class ClickHandler(logging.Handler):
    """Simple console stream logging handler to export log messages as a click echo."""

    @override
    def emit(self, record: logging.LogRecord) -> None:
        try:
            click.echo(self.format(record), err=True)
        except Exception:  # noqa: BLE001
            self.handleError(record)
            return


def setup_logging(verbosity: int) -> None:
    """Set up logging using click's echo messaging at the given verbosity."""
    logger.disabled = False
    logger.setLevel(
        logging.DEBUG if verbosity > 0 else logging.INFO if verbosity == 0 else logging.WARNING
    )
    logger.propagate = False
    click_handler: logging.Handler = ClickHandler()
    click_handler.formatter = ColourFormatter()
    logger.handlers = [click_handler]
