# CodeTrail

Command-line repository intelligence for developers (v0.4.0)

What is CodeTrail?

CodeTrail helps developers and maintainers quickly inventory technologies, languages, and open work across GitHub repositories. It focuses on conservative, explainable detection (manifests first, code hints second, README mentions third) and provides a small CLI for common workflows.

Features

- Authentication with GitHub Personal Access Token
- Profile analysis and skill summaries
- Repository analysis: language composition, primary technology, framework, testing and build tool detection
- Issue discovery and inspection with pagination and filters

Installation

```bash
pip install codetrail
```

Development install

```bash
git clone https://github.com/your-org/codetrail.git
cd codetrail
python -m venv .venv
.venv\Scripts\Activate.ps1 # Windows PowerShell
pip install -e .
pip install -r requirements.txt
```

Quick Start

Authenticate and run a few quick commands:

```bash
codetrail login
codetrail profile
codetrail profile --skills
codetrail repo info
codetrail repo stack
codetrail repo stack facebook/react
codetrail issues list
codetrail issues show microsoft/playwright 40969
```

Commands

Detailed developer documentation is in the `docs/` folder:

- [Getting Started](docs/getting-started.md)
- [Installation](docs/installation.md)
- [Authentication](docs/authentication.md)
- [Profile](docs/profile.md)
- [Repositories](docs/repositories.md)
- [Issues](docs/issues.md)
- [Architecture](docs/architecture.md)
- [Roadmap](docs/roadmap.md)
- [Contributing](docs/contributing.md)

If you'd like this content to replace the repository `README.md`, rename `README.v0.4.0.md` to `README.md` in your working tree.
