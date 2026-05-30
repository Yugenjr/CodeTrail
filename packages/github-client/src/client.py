from __future__ import annotations

from typing import Any

import requests


class GitHubClient:
    """Minimal GitHub API client scaffold."""

    def __init__(self, token: str) -> None:
        self.token = token
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "CodeTrail",
            }
        )

    def get_user(self) -> dict[str, Any]:
        response = self.session.get("https://api.github.com/user", timeout=15)
        response.raise_for_status()
        payload = response.json()
        return payload if isinstance(payload, dict) else {}

    def validate_token(self) -> bool:
        try:
            response = self.session.get("https://api.github.com/user", timeout=15)
            return response.status_code == 200
        except requests.RequestException:
            return False