"""Automated test suite for argument parsing within `console.py`."""

import importlib.metadata
import re
from typing import TYPE_CHECKING, Final

from click.testing import CliRunner

from ccft_pymarkdown import console

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence
    from typing import Final

    from click.testing import Result as ClickResult

__all__: "Sequence[str]" = ()


class TestConsoleRun:
    """Test case to unit-test the `run` function."""

    PARTIAL_USAGE_MESSAGES: "Final[Iterable[str]]" = (
        "Usage: ",
        " [OPTIONS] COMMAND [ARGS]...",
    )

    def test_help_when_no_args(self) -> None:
        PARTIAL_EXPECTED_HELP_MESSAGES: Final[Iterable[str]] = (
            "Show this message and exit.",
            "Options:",
            "Commands:",
        )
        RUNNER: CliRunner = CliRunner()

        result: ClickResult = RUNNER.invoke(console.run, ())

        assert result.exit_code == 0
        assert all(
            partial_usage_message in re.sub(r"\s+|\n", " ", result.output)
            for partial_usage_message in self.PARTIAL_USAGE_MESSAGES
        )
        assert all(
            partial_expected_help_message in re.sub(r"\s+|\n", " ", result.output)
            for partial_expected_help_message in PARTIAL_EXPECTED_HELP_MESSAGES
        )

    def test_package_description_in_help(self) -> None:
        package_description: str | None = importlib.metadata.metadata("CCFT-PyMarkdown").get(
            "Summary"
        )

        if package_description is None:
            return

        RUNNER: CliRunner = CliRunner()

        result: ClickResult = RUNNER.invoke(console.run, ("--help",))

        assert result.exit_code == 0
        assert f"{package_description.strip('.')}." in re.sub(r"\s+|\n", " ", result.output)
