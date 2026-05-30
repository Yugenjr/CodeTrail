from __future__ import annotations

from typing import Any

import requests


class GitHubClient:
    """Minimal GitHub API client for local CLI authentication and profile lookup."""

    def __init__(self, token: str) -> None:
        self.token = token
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "CodeTrail CLI",
            }
        )

    def get_user(self) -> dict[str, Any]:
        response = self.session.get("https://api.github.com/user", timeout=15)
        response.raise_for_status()
        payload = response.json()
        return payload if isinstance(payload, dict) else {}

    def get_user_repositories(self) -> list[dict[str, Any]]:
        repositories: list[dict[str, Any]] = []
        page = 1

        while True:
            response = self.session.get(
                "https://api.github.com/user/repos",
                params={
                    "per_page": 100,
                    "page": page,
                    "sort": "updated",
                    "direction": "desc",
                    "visibility": "all",
                },
                timeout=15,
            )
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, list) or not payload:
                break

            repositories.extend(item for item in payload if isinstance(item, dict))
            if len(payload) < 100:
                break
            page += 1

        return repositories

    def get_repository_languages(self, owner: str, repo: str) -> dict[str, int]:
        response = self.session.get(
            f"https://api.github.com/repos/{owner}/{repo}/languages",
            timeout=15,
        )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            return {}

        result: dict[str, int] = {}
        for language, bytes_used in payload.items():
            if isinstance(language, str) and isinstance(bytes_used, int):
                result[language] = bytes_used
        return result

    def get_repository_tree(self, owner: str, repo: str, ref: str | None = None) -> list[str]:
        tree_sha = ref
        if ref:
            branch_response = self.session.get(
                f"https://api.github.com/repos/{owner}/{repo}/branches/{ref}",
                timeout=15,
            )
            if branch_response.status_code == 200:
                branch_payload = branch_response.json()
                if isinstance(branch_payload, dict):
                    commit = branch_payload.get("commit")
                    if isinstance(commit, dict):
                        tree = commit.get("commit")
                        if isinstance(tree, dict):
                            tree_sha = tree.get("tree", {}).get("sha") if isinstance(tree.get("tree"), dict) else None

        if not isinstance(tree_sha, str) or not tree_sha:
            return []

        response = self.session.get(
            f"https://api.github.com/repos/{owner}/{repo}/git/trees/{tree_sha}",
            params={"recursive": 1},
            timeout=15,
        )
        if response.status_code == 404:
            return []
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            return []

        tree = payload.get("tree", [])
        if not isinstance(tree, list):
            return []

        paths: list[str] = []
        for entry in tree:
            if isinstance(entry, dict):
                path = entry.get("path")
                if isinstance(path, str):
                    paths.append(path)
        return paths

    def get_repository_info(self, owner: str, repo: str) -> dict[str, Any]:
        response = self.session.get(f"https://api.github.com/repos/{owner}/{repo}", timeout=15)
        if response.status_code != 200:
            return {}
        payload = response.json()
        return payload if isinstance(payload, dict) else {}

    def get_issues(self, owner: str, repo: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        params = params or {"per_page": 30, "state": "open"}
        try:
            response = self.session.get(f"https://api.github.com/repos/{owner}/{repo}/issues", params=params, timeout=15)
            response.raise_for_status()
            payload = response.json()
            return [item for item in payload if isinstance(item, dict) and "pull_request" not in item]
        except Exception:
            return []

    def get_issue(self, owner: str, repo: str, number: int) -> dict[str, Any] | None:
        try:
            response = self.session.get(f"https://api.github.com/repos/{owner}/{repo}/issues/{number}", timeout=15)
            if response.status_code != 200:
                return None
            payload = response.json()
            return payload if isinstance(payload, dict) else None
        except Exception:
            return None

    def get_commit_count(self, owner: str, repo: str) -> int | None:
        """Estimate commit count using the commits endpoint and Link header."""
        try:
            response = self.session.get(
                f"https://api.github.com/repos/{owner}/{repo}/commits",
                params={"per_page": 1},
                timeout=15,
            )
            if response.status_code != 200:
                return None

            link = response.headers.get("Link")
            if not link:
                # no pagination header, count is the number of items in response (0 or 1)
                payload = response.json()
                if isinstance(payload, list):
                    return len(payload)
                return None

            # parse rel="last" page number
            # Link header format: <...&page=NN&per_page=1>; rel="last", <...>; rel="next"
            parts = [p.strip() for p in link.split(",")]
            for part in parts:
                if 'rel="last"' in part:
                    # extract page param
                    start = part.find("<")
                    end = part.find(">", start)
                    if start == -1 or end == -1:
                        continue
                    url = part[start + 1 : end]
                    # find page= number
                    import urllib.parse as _up

                    qs = _up.urlparse(url).query
                    params = _up.parse_qs(qs)
                    page_vals = params.get("page")
                    if page_vals:
                        try:
                            return int(page_vals[-1])
                        except Exception:
                            return None
            return None
        except Exception:
            return None

    def get_repository_file_text(self, owner: str, repo: str, path: str) -> str | None:
        response = self.session.get(
            f"https://api.github.com/repos/{owner}/{repo}/contents/{path}",
            timeout=15,
        )
        if response.status_code != 200:
            return None

        payload = response.json()
        if not isinstance(payload, dict):
            return None

        content = payload.get("content")
        encoding = payload.get("encoding")
        if not isinstance(content, str) or encoding != "base64":
            return None

        import base64

        try:
            return base64.b64decode(content).decode("utf-8", errors="ignore")
        except (ValueError, UnicodeDecodeError):
            return None

    def validate_token(self) -> bool:
        try:
            response = self.session.get("https://api.github.com/user", timeout=15)
            return response.status_code == 200
        except requests.RequestException:
            return False