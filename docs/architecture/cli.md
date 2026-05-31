# CLI

CodeTrail's CLI is implemented using `Typer` with Rich for console rendering. The CLI organizes commands into logical groups (auth, profile, repo, issues) and exposes flags such as `--debug` and `--full` for verbose output.

Key points:

- Commands are registered under `apps/cli/src/main.py`.
- Implementations live in `apps/cli/src/commands/`.
- Use `codetrail <group> --help` to view available commands and flags.
