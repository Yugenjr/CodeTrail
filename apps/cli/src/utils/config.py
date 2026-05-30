from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ConfigManager:
    """Manage CodeTrail local configuration."""

    def __init__(self, config_path: Path | None = None) -> None:
        self.config_dir = Path.home() / ".codetrail"
        self.config_path = config_path or self.config_dir / "config.json"

    def load_config(self) -> dict[str, Any]:
        if not self.config_path.exists():
            return {}

        try:
            with self.config_path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
        except json.JSONDecodeError:
            return {}

        return data if isinstance(data, dict) else {}

    def save_config(self, config: dict[str, Any] | None = None) -> None:
        self.config_dir.mkdir(parents=True, exist_ok=True)
        payload = config if config is not None else self.load_config()

        with self.config_path.open("w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")

    def get_github_token(self) -> str | None:
        config = self.load_config()
        token = config.get("github_token")
        return token if isinstance(token, str) and token else None

    def set_github_token(self, token: str) -> None:
        config = self.load_config()
        config["github_token"] = token
        self.save_config(config)

    def remove_github_token(self) -> None:
        config = self.load_config()
        if "github_token" in config:
            del config["github_token"]

        if config:
            self.save_config(config)
            return

        if self.config_path.exists():
            self.config_path.unlink()

    def get_skill_analysis_cache(self) -> dict[str, Any] | None:
        config = self.load_config()
        cache = config.get("skill_analysis_cache")
        return cache if isinstance(cache, dict) else None

    def set_skill_analysis_cache(self, cache: dict[str, Any]) -> None:
        config = self.load_config()
        config["skill_analysis_cache"] = cache
        self.save_config(config)

    def clear_skill_analysis_cache(self) -> None:
        config = self.load_config()
        if "skill_analysis_cache" in config:
            del config["skill_analysis_cache"]

        if config:
            self.save_config(config)
            return

        if self.config_path.exists():
            self.config_path.unlink()