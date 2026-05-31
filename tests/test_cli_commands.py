import pytest

from typer.testing import CliRunner

from main import app


runner = CliRunner()


@pytest.mark.parametrize(
    "command",
    [
        ["login"],
        ["logout"],
        ["profile"],
        ["repo", "info"],
        ["repo", "stack"],
        ["repo", "structure"],
        ["issues", "list"],
        ["issues", "show"],
        ["issues", "search"],
        ["issues", "filter"],
        ["find"],
        ["analyze"],
        ["recommend"],
        ["roadmap"],
    ],
)
def test_command_help_available(command):
    """Each command/subcommand should expose a `--help` entrypoint."""
    result = runner.invoke(app, [*command, "--help"])  # type: ignore[arg-type]
    assert result.exit_code == 0, f"Help failed for {' '.join(command)}: {result.output}"
