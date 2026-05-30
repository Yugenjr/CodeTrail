from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

from utils.config import ConfigManager
from utils.github_client import GitHubClient


SKILL_CACHE_TTL = timedelta(hours=24)


@dataclass(slots=True)
class RepositorySkillSnapshot:
    name: str
    full_name: str
    html_url: str
    languages: dict[str, int]
    frameworks: list[str]
    fork: bool = False


@dataclass(slots=True)
class SkillNode:
    name: str
    category: str
    score: int
    evidence_count: int
    repositories: list[str] = field(default_factory=list)


@dataclass(slots=True)
class SkillAnalysisResult:
    username: str
    display_name: str | None
    repository_count: int
    analyzed_repositories: list[RepositorySkillSnapshot]
    language_totals: dict[str, int]
    framework_counts: dict[str, int]
    nodes: list[SkillNode]
    generated_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "username": self.username,
            "display_name": self.display_name,
            "repository_count": self.repository_count,
            "analyzed_repositories": [
                {
                    "name": repository.name,
                    "full_name": repository.full_name,
                    "html_url": repository.html_url,
                    "languages": repository.languages,
                    "frameworks": repository.frameworks,
                    "fork": repository.fork,
                }
                for repository in self.analyzed_repositories
            ],
            "language_totals": self.language_totals,
            "framework_counts": self.framework_counts,
            "nodes": [
                {
                    "name": node.name,
                    "category": node.category,
                    "score": node.score,
                    "evidence_count": node.evidence_count,
                    "repositories": node.repositories,
                }
                for node in self.nodes
            ],
            "generated_at": self.generated_at,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "SkillAnalysisResult":
        repositories = [
            RepositorySkillSnapshot(
                name=str(item.get("name", "")),
                full_name=str(item.get("full_name", "")),
                html_url=str(item.get("html_url", "")),
                languages={str(key): int(value) for key, value in dict(item.get("languages", {})).items() if isinstance(key, str) and isinstance(value, int)},
                frameworks=[str(value) for value in list(item.get("frameworks", []))],
                fork=bool(item.get("fork", False)),
            )
            for item in list(payload.get("analyzed_repositories", []))
            if isinstance(item, dict)
        ]
        nodes = [
            SkillNode(
                name=str(item.get("name", "")),
                category=str(item.get("category", "")),
                score=int(item.get("score", 0)),
                evidence_count=int(item.get("evidence_count", 0)),
                repositories=[str(value) for value in list(item.get("repositories", []))],
            )
            for item in list(payload.get("nodes", []))
            if isinstance(item, dict)
        ]

        return cls(
            username=str(payload.get("username", "")),
            display_name=payload.get("display_name"),
            repository_count=int(payload.get("repository_count", 0)),
            analyzed_repositories=repositories,
            language_totals={str(key): int(value) for key, value in dict(payload.get("language_totals", {})).items() if isinstance(key, str) and isinstance(value, int)},
            framework_counts={str(key): int(value) for key, value in dict(payload.get("framework_counts", {})).items() if isinstance(key, str) and isinstance(value, int)},
            nodes=nodes,
            generated_at=str(payload.get("generated_at", "")),
        )


class SkillAnalysisService:
    """Analyze user repositories into a local skill graph."""

    framework_rules = {
        "FastAPI": ("fastapi", "fastapi"),
        "Django": ("django", "django"),
        "Flask": ("flask", "flask"),
        "SQLAlchemy": ("sqlalchemy", "sqlalchemy"),
        "Pytest": ("pytest", "pytest"),
        "Celery": ("celery", "celery"),
        "React": ("react", "react"),
        "Next.js": ("next", "next"),
        "Vue": ("vue", "vue"),
        "Express": ("express", "express"),
        "TypeScript": ("typescript", "typescript"),
        "Pydantic": ("pydantic", "pydantic"),
    }

    manifest_files = {
        "pyproject.toml",
        "requirements.txt",
        "poetry.lock",
        "Pipfile",
        "setup.py",
        "package.json",
        "pnpm-lock.yaml",
        "yarn.lock",
        "package-lock.json",
        "go.mod",
        "Cargo.toml",
        "Gemfile",
    }

    def __init__(self, client: GitHubClient, config: ConfigManager | None = None) -> None:
        self.client = client
        self.config = config or ConfigManager()

    def analyze(self, refresh: bool = False) -> SkillAnalysisResult:
        cached = self.config.get_skill_analysis_cache()
        if not refresh and cached:
            cached_timestamp = str(cached.get("generated_at", ""))
            if self._is_cache_fresh(cached_timestamp):
                return SkillAnalysisResult.from_dict(cached)

        user = self.client.get_user()
        repositories = self.client.get_user_repositories()

        analyzed_repositories: list[RepositorySkillSnapshot] = []
        language_totals: Counter[str] = Counter()
        framework_counts: Counter[str] = Counter()
        framework_sources: dict[str, set[str]] = defaultdict(set)
        language_sources: dict[str, set[str]] = defaultdict(set)

        for repository in repositories:
            owner = self._string_value(repository.get("owner", {}), "login") or str(user.get("login", ""))
            name = str(repository.get("name", ""))
            full_name = str(repository.get("full_name", f"{owner}/{name}"))
            html_url = str(repository.get("html_url", ""))
            fork = bool(repository.get("fork", False))
            weight = 0.5 if fork else 1.0

            repo_languages = self._fetch_repository_languages(owner, name, repository)
            for language, bytes_used in repo_languages.items():
                weighted_bytes = max(1, int(bytes_used * weight))
                language_totals[language] += weighted_bytes
                language_sources[language].add(full_name)

            repo_tree = self._fetch_repository_tree(owner, name, repository)
            repo_content_snippets = self._fetch_repository_manifests(owner, name, repo_tree)
            frameworks = self._detect_frameworks(repo_tree, repo_content_snippets)
            for framework in frameworks:
                framework_counts[framework] += 1
                framework_sources[framework].add(full_name)

            analyzed_repositories.append(
                RepositorySkillSnapshot(
                    name=name,
                    full_name=full_name,
                    html_url=html_url,
                    languages=repo_languages,
                    frameworks=frameworks,
                    fork=fork,
                )
            )

        nodes = self._build_skill_nodes(
            language_totals=language_totals,
            framework_counts=framework_counts,
            language_sources=language_sources,
            framework_sources=framework_sources,
            repository_count=len(analyzed_repositories),
        )

        analysis = SkillAnalysisResult(
            username=str(user.get("login", "")),
            display_name=user.get("name"),
            repository_count=len(analyzed_repositories),
            analyzed_repositories=analyzed_repositories,
            language_totals=dict(language_totals),
            framework_counts=dict(framework_counts),
            nodes=nodes,
            generated_at=self._now_iso(),
        )
        self.config.set_skill_analysis_cache(analysis.to_dict())
        return analysis

    def _fetch_repository_languages(
        self,
        owner: str,
        name: str,
        repository: dict[str, Any],
    ) -> dict[str, int]:
        try:
            languages = self.client.get_repository_languages(owner, name)
        except Exception:
            languages = {}

        if languages:
            return languages

        fallback_language = repository.get("language")
        if isinstance(fallback_language, str) and fallback_language:
            return {fallback_language: 1}
        return {}

    def _fetch_repository_tree(self, owner: str, name: str, repository: dict[str, Any]) -> list[str]:
        default_branch = repository.get("default_branch")
        branch = str(default_branch) if isinstance(default_branch, str) and default_branch else None
        try:
            return self.client.get_repository_tree(owner, name, ref=branch)
        except Exception:
            return []

    def _fetch_repository_manifests(self, owner: str, name: str, tree: list[str]) -> dict[str, str]:
        content: dict[str, str] = {}
        for path in tree:
            filename = path.rsplit("/", 1)[-1]
            if filename not in self.manifest_files:
                continue

            text = self.client.get_repository_file_text(owner, name, path)
            if text:
                content[path] = text[:50000]

        return content

    def _detect_frameworks(self, tree: list[str], manifests: dict[str, str]) -> list[str]:
        detected: list[str] = []
        haystack = "\n".join(tree).lower()
        manifest_blob = "\n".join(manifests.values()).lower()

        for framework, (path_keyword, content_keyword) in self.framework_rules.items():
            if path_keyword in haystack or content_keyword in manifest_blob:
                detected.append(framework)

        if "package.json" in haystack:
            package_json = next((text for path, text in manifests.items() if path.endswith("package.json")), "")
            package_blob = package_json.lower()
            for framework in ("React", "Next.js", "Vue", "Express", "TypeScript"):
                if framework.lower().replace(".", "") in package_blob:
                    if framework not in detected:
                        detected.append(framework)

        if "pyproject.toml" in haystack or "requirements.txt" in haystack or "setup.py" in haystack:
            if "fastapi" in manifest_blob and "FastAPI" not in detected:
                detected.append("FastAPI")
            if "django" in manifest_blob and "Django" not in detected:
                detected.append("Django")
            if "flask" in manifest_blob and "Flask" not in detected:
                detected.append("Flask")
            if "pytest" in manifest_blob and "Pytest" not in detected:
                detected.append("Pytest")

        return detected

    def _build_skill_nodes(
        self,
        *,
        language_totals: Counter[str],
        framework_counts: Counter[str],
        language_sources: dict[str, set[str]],
        framework_sources: dict[str, set[str]],
        repository_count: int,
    ) -> list[SkillNode]:
        total_language_bytes = sum(language_totals.values()) or 1
        nodes: list[SkillNode] = []

        for language, bytes_used in language_totals.most_common():
            share = bytes_used / total_language_bytes
            evidence = len(language_sources.get(language, set()))
            score = min(100, round((share * 70) + ((evidence / max(repository_count, 1)) * 30)))
            nodes.append(
                SkillNode(
                    name=language,
                    category="language",
                    score=score,
                    evidence_count=evidence,
                    repositories=sorted(language_sources.get(language, set()))[:10],
                )
            )

        for framework, count in framework_counts.most_common():
            evidence = len(framework_sources.get(framework, set()))
            score = min(100, (count * 20) + (evidence * 10))
            nodes.append(
                SkillNode(
                    name=framework,
                    category="framework",
                    score=score,
                    evidence_count=evidence,
                    repositories=sorted(framework_sources.get(framework, set()))[:10],
                )
            )

        return nodes

    def _is_cache_fresh(self, timestamp: str) -> bool:
        try:
            parsed = datetime.fromisoformat(timestamp)
        except ValueError:
            return False

        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)

        return datetime.now(timezone.utc) - parsed <= SKILL_CACHE_TTL

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _string_value(payload: Any, key: str) -> str | None:
        if isinstance(payload, dict):
            value = payload.get(key)
            if isinstance(value, str) and value:
                return value
        return None