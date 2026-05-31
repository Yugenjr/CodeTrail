# Contributing

Thanks for your interest in contributing to CodeTrail. This guide helps you get started developing locally and submitting changes.

Development setup

1. Clone the repository:

```bash
git clone https://github.com/your-org/codetrail.git
cd codetrail
python -m venv .venv
.venv\Scripts\Activate.ps1 # Windows PowerShell
pip install -e .
pip install -r requirements.txt
```

Running tests

Run the CLI help tests and test suite with `pytest`:

```bash
pytest -q
```

Project structure

- `apps/cli/` — CLI entrypoints and command implementations.
- `apps/cli/src/utils/` — core utilities: `github_client.py`, `repo_utils.py`, `skill_analysis.py`.
- `tests/` — unit and integration tests.
- `docs/` — documentation (this folder).

Submitting Pull Requests

1. Fork the repository and create a feature branch.
2. Run tests locally and update/add tests for new behavior.
3. Open a Pull Request with a clear description and link to any relevant issues.
4. CI will run tests; address feedback and iterate.

Coding guidelines

- Keep changes focused and small.
- Add tests for behavior-critical logic (parsing, detection, scoring).
- Maintain existing code style and docstrings.
