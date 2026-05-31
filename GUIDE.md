# CodeTrail CLI — Guide

This single, unified guide documents every CodeTrail CLI command and option.

Quick setup

- Authenticate with GitHub to enable repository and issue operations:

```bash
codetrail login
```

- To remove stored credentials:

```bash
codetrail logout
```

Configuration

- Local config is stored at `~/.codetrail/config.json` (token, caches).
- Skill analysis cache uses an internal version and TTL to avoid stale results.

Top-level commands

- `login` — Store a GitHub personal access token used for API requests.
	- Interactive prompt; token is stored by `ConfigManager`.
- `logout` — Remove the stored token.
- `profile` — Show authenticated GitHub profile information.
	- Option: `--skills` analyze your repositories and display detected languages and frameworks.
 - `find` — Find candidate issues (placeholder command; currently returns no results).
 - `analyze` — Analyze an issue (placeholder command; currently returns no results).
 - `recommend` — Recommend issues for contribution (placeholder command; currently returns no results).
 - `roadmap` — Generate a roadmap for contributions or project planning (placeholder command).

Repository inspection (`repo`)

Usage: `codetrail repo <subcommand> [owner/repo] [--repo owner/repo]`

- `info [owner/repo]` — Show repository metadata: full name, description, stars, forks, primary language, open issues, and commits (commit count may be estimated).
	- If `owner/repo` is omitted the command attempts to detect the current repository via `.git/config` or `git remote`.
- `stack [owner/repo]` — Fast tech stack detection using root-level manifests (e.g., `package.json`, `pyproject.toml`, `requirements.txt`). Shows top languages and detected frameworks.
- `structure [owner/repo]` — List likely important top-level directories and common manifest files (e.g., `src`, `test`, `README.md`, `package.json`).

Issues exploration (`issues`)

Usage: `codetrail issues <subcommand> ...` — repository may be provided positionally or via `--repo`.

- `list [owner/repo] [--limit N] [--page P]` — List open issues (defaults: `--limit 30`, `--page 1`). Outputs `#<number>  <title>` per line.
- `show <number> [owner/repo]` — Show details for a single issue. Supports flexible argument orders:
	- `codetrail issues show 123` (uses current repo)
	- `codetrail issues show 123 owner/repo`
	- `codetrail issues show owner/repo 123`
	- `codetrail issues show 123 --repo owner/repo`
- `search <query> [owner/repo] [--limit N] [--page P]` — Search issue titles and bodies for `query`. Supports `query owner/repo` or `owner/repo query` ordering. Results are printed as `#<number>  <title>`; pagination available via `--limit`/`--page`.
- `filter <label> [owner/repo] [--limit N] [--page P]` — Show open issues matching `label` (client-side label filtering is used as a fallback).

Argument and repository resolution rules

- Priority: explicit positional `owner/repo` → `--repo` option → detect current Git repository → error with guidance.
- To avoid shell quoting issues (e.g., PowerShell), use `--repo owner/repo` instead of a positional `owner/repo`.

Behavioral notes

- The CLI favors fast, shallow inspections by default to keep interactions snappy (root-level manifest checks, not whole-tree crawling).
- GitHub API rate limits apply; authenticated requests (via `codetrail login`) increase limits.
- Pagination: many list/search commands accept `--limit N` and `--page P` to control result size and paging. Some operations page client-side when server-side paging is not used.

Examples

```bash
# Authenticate once
codetrail login

# Profile and skills
codetrail profile
codetrail profile --skills

# Inspect local repository (auto-detected)
cd myproject
codetrail repo info
codetrail repo stack
codetrail repo structure

# Inspect remote repository explicitly
codetrail repo info microsoft/vscode
codetrail repo stack --repo microsoft/vscode

# Issues: list, search, show
codetrail issues list
codetrail issues list --repo microsoft/vscode --limit 50 --page 2
codetrail issues search bug --repo microsoft/vscode
codetrail issues show 123 --repo microsoft/vscode
codetrail issues filter good-first-issue --repo microsoft/vscode
```
Development & testing

- Unit tests live in `tests/` (run with `pytest -q`).
- CI: `.github/workflows/ci.yml` runs tests on push and pull requests.
	- `--full` on `issues show` prints full issue body and timestamps; without it the output shows a truncated summary (first ~1000 chars).

	- Framework detection inspects remote manifest files and reports evidence counts and a confidence score (0-100). A `Testing` section lists detected test frameworks.
- If repository detection fails, pass the repository explicitly with `--repo owner/repo`.
- Long-running analysis: `profile --skills` can take time for many repositories; the CLI shows progress updates. You can skip deep analysis by omitting `--skills`.

Further enhancements

- Consider `--json` output for scripting and machine-readable integration.
- Add optional deeper scans (recursive manifest discovery) behind a `--deep` flag for advanced analysis.

