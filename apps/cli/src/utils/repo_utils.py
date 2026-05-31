from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable
import configparser
import subprocess

from utils.github_client import GitHubClient


class RepositoryResolver:
    """Resolve owner/repo from current git repository or explicit argument."""

    def __init__(self, cwd: Path | None = None) -> None:
        self.cwd = cwd or Path.cwd()

    def _from_git_config(self) -> str | None:
        git_config = self.cwd / ".git" / "config"
        if not git_config.exists():
            return None

        parser = configparser.ConfigParser()
        try:
            parser.read(git_config)
            for section in parser.sections():
                if section.startswith("remote \"") and "url" in parser[section]:
                    url = parser[section]["url"]
                    repo = self._parse_remote_url(url)
                    if repo:
                        return repo
        except Exception:
            return None
        return None

    def _from_git_remote(self) -> str | None:
        try:
            result = subprocess.run(["git", "remote", "get-url", "origin"], cwd=self.cwd, capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                url = result.stdout.strip()
                return self._parse_remote_url(url)
        except Exception:
            return None
        return None

    def _parse_remote_url(self, url: str) -> str | None:
        # Support formats: git@github.com:owner/repo.git and https://github.com/owner/repo.git
        if url.startswith("git@"):
            try:
                _, path = url.split(":", 1)
                owner_repo = path.rsplit(".git", 1)[0]
                return owner_repo
            except Exception:
                return None
        if url.startswith("http"):
            try:
                parts = url.split("/")
                owner = parts[-2]
                repo = parts[-1].rsplit(".git", 1)[0]
                return f"{owner}/{repo}"
            except Exception:
                return None
        return None

    def resolve(self, explicit: str | None = None) -> tuple[str, str]:
        if explicit:
            parts = explicit.split("/", 1)
            if len(parts) == 2:
                return parts[0], parts[1]
            raise ValueError("Invalid repository format; expected owner/repo")

        repo = self._from_git_config() or self._from_git_remote()
        if not repo:
            raise ValueError("No git repository detected. Provide a repository explicitly: codetrail repo info owner/repo")
        owner, name = repo.split("/", 1)
        return owner, name


class RepositoryAnalyzer:
    """Analyze repository metadata, tech stack, and structure using GitHub API."""

    important_files = {"package.json", "pyproject.toml", "README.md", "Dockerfile", "tsconfig.json", "requirements.txt"}

    def __init__(self, client: GitHubClient) -> None:
        self.client = client

    def metadata(self, owner: str, repo: str) -> dict[str, Any]:
        return self.client.get_repository_info(owner, repo)

    def stack(self, owner: str, repo: str) -> dict[str, list[str]]:
        languages = self.client.get_repository_languages(owner, repo) or {}
        lang_list = sorted(languages.keys(), key=lambda k: languages.get(k, 0), reverse=True)

        # detect frameworks from root-level manifests
        tree = self.client.get_repository_tree(owner, repo)
        root_files = [p for p in tree if "/" not in p]
        frameworks: set[str] = set()
        for fname in root_files:
            if fname == "package.json":
                text = self.client.get_repository_file_text(owner, repo, fname) or ""
                blob = text.lower()
                for fw in ("react", "next", "vue", "express", "electron", "jest", "playwright"):
                    if fw in blob:
                        frameworks.add(fw.capitalize())
        return {"languages": lang_list[:8], "frameworks": sorted(frameworks)}

    def structure(self, owner: str, repo: str) -> dict[str, list[str]]:
        tree = self.client.get_repository_tree(owner, repo)
        top_dirs = set()
        top_files = set()
        for path in tree:
            if "/" in path:
                top_dir = path.split("/", 1)[0]
                top_dirs.add(top_dir)
            else:
                top_files.add(path)

        important_dirs = sorted([d for d in top_dirs if d.lower() in {"src", "lib", "test", "tests", "extensions", "build"}])
        important_files = sorted([f for f in top_files if f in self.important_files])
        return {"important_directories": important_dirs[:10], "important_files": important_files[:20]}


class IssueExplorer:
    """List, search, filter, and fetch issue details from GitHub."""

    def __init__(self, client: GitHubClient) -> None:
        self.client = client

    def list(self, owner: str, repo: str, state: str = "open", limit: int = 30) -> list[dict[str, Any]]:
        params = {"state": state, "per_page": min(limit, 100)}
        return self.client.get_issues(owner, repo, params=params)

    def list_paginated(self, owner: str, repo: str, state: str = "open", limit: int = 30, page: int = 1) -> list[dict[str, Any]]:
        params = {"state": state, "per_page": min(limit, 100), "page": max(1, int(page))}
        return self.client.get_issues(owner, repo, params=params)

    def show(self, owner: str, repo: str, number: int) -> dict[str, Any] | None:
        return self.client.get_issue(owner, repo, number)

    def search(self, owner: str, repo: str, query: str, state: str = "open") -> list[dict[str, Any]]:
        issues = self.list(owner, repo, state=state, limit=100)
        results = [i for i in issues if query.lower() in (i.get("title", "") + "\n" + (i.get("body") or "")).lower()]
        return results

    def filter_by_label(self, owner: str, repo: str, label: str) -> list[dict[str, Any]]:
        params = {"state": "open", "labels": label, "per_page": 100}
        return self.client.get_issues(owner, repo, params=params)
