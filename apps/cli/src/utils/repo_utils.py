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


class LanguageAnalyzer:
    """Calculate GitHub language composition percentages for a repository."""

    def __init__(self, client: GitHubClient) -> None:
        self.client = client

    def analyze(self, owner: str, repo: str) -> list[dict[str, Any]]:
        languages = self.client.get_repository_languages(owner, repo) or {}
        total = sum(v for v in languages.values() if isinstance(v, int) and v > 0)
        if total <= 0:
            return []

        rows: list[dict[str, Any]] = []
        for name, bytes_used in sorted(languages.items(), key=lambda kv: kv[1], reverse=True):
            if not isinstance(bytes_used, int) or bytes_used <= 0:
                continue
            pct = round((bytes_used / total) * 100, 1)
            rows.append({"name": name, "bytes": bytes_used, "percentage": pct})
        return rows


class RepositoryIdentityAnalyzer:
    """Infer repository primary framework/type using name, description and topics."""

    framework_aliases: dict[str, tuple[str, ...]] = {
        "React": ("react",),
        "Next.js": ("next", "nextjs", "next.js"),
        "Vue": ("vue", "vuejs"),
        "Angular": ("angular",),
        "Playwright": ("playwright",),
        "FastAPI": ("fastapi",),
        "Django": ("django",),
        "Flask": ("flask",),
        "Spring": ("spring", "spring-boot"),
        "Quarkus": ("quarkus",),
        "Jest": ("jest",),
        "Vitest": ("vitest",),
        "pytest": ("pytest",),
        "Node.js": ("node", "nodejs", "node.js"),
    }

    framework_types: dict[str, str] = {
        "React": "Frontend Library",
        "Next.js": "Frontend Framework",
        "Vue": "Frontend Framework",
        "Angular": "Frontend Framework",
        "Playwright": "Testing Framework",
        "Jest": "Testing Framework",
        "Vitest": "Testing Framework",
        "pytest": "Testing Framework",
        "FastAPI": "Backend Framework",
        "Django": "Backend Framework",
        "Flask": "Backend Framework",
        "Spring": "Backend Framework",
        "Quarkus": "Backend Framework",
        "Node.js": "Runtime Platform",
    }

    def _contains_token(self, text: str, token: str) -> bool:
        import re

        return re.search(rf"\b{re.escape(token)}\b", text.lower()) is not None

    def analyze(
        self,
        owner: str,
        repo: str,
        metadata: dict[str, Any],
        detected_frameworks: set[str] | None = None,
        primary_technology: str | None = None,
    ) -> dict[str, Any]:
        detected_frameworks = detected_frameworks or set()

        score: dict[str, int] = {}
        reasons: dict[str, list[str]] = {}

        repo_name = repo.lower()
        full_name = f"{owner}/{repo}".lower()
        description = str(metadata.get("description") or "").lower()
        topics = metadata.get("topics", [])
        topic_values = [str(t).lower() for t in topics] if isinstance(topics, list) else []

        def add(framework: str, amount: int, why: str) -> None:
            score[framework] = score.get(framework, 0) + amount
            reasons.setdefault(framework, []).append(why)

        for framework, aliases in self.framework_aliases.items():
            for alias in aliases:
                if self._contains_token(repo_name, alias) or self._contains_token(full_name, alias):
                    add(framework, 150, f"name:{alias}")
                if description and self._contains_token(description, alias):
                    add(framework, 80, f"description:{alias}")
                if alias in topic_values:
                    add(framework, 100, f"topic:{alias}")

        # Keep weak detected signals for explainability only; they should not
        # invent repository identity on their own.
        for framework in detected_frameworks:
            add(framework, 5, "detected")

        if not score:
            return {
                "primary_framework": None,
                "repository_type": "CLI Developer Tool" if (primary_technology or "").lower() == "python" else "General Repository",
                "primary_technology": primary_technology,
                "signals": {},
            }

        primary, strongest = max(score.items(), key=lambda kv: kv[1])

        # Strong identity must come from name/description/topics, not just weak
        # detected evidence. Threshold tuned so "detected"-only signals do not win.
        if strongest < 80:
            return {
                "primary_framework": None,
                "repository_type": "CLI Developer Tool" if (primary_technology or "").lower() == "python" else "General Repository",
                "primary_technology": primary_technology,
                "signals": reasons,
            }

        repo_type = self.framework_types.get(primary, "General Repository")
        return {
            "primary_framework": primary,
            "repository_type": repo_type,
            "primary_technology": primary_technology,
            "signals": reasons,
        }


class RepositoryAnalyzer:
    """Analyze repository metadata, tech stack, and structure using GitHub API."""

    important_files = {"package.json", "pyproject.toml", "README.md", "Dockerfile", "tsconfig.json", "requirements.txt"}

    def __init__(self, client: GitHubClient) -> None:
        self.client = client

    def metadata(self, owner: str, repo: str) -> dict[str, Any]:
        return self.client.get_repository_info(owner, repo)

    def stack(self, owner: str, repo: str) -> dict[str, Any]:
        language_breakdown = LanguageAnalyzer(self.client).analyze(owner, repo)
        lang_list = [l.get("name", "") for l in language_breakdown]
        metadata = self.metadata(owner, repo)

        # manifest files to inspect via GitHub Contents API
        manifests = [
            "package.json",
            "requirements.txt",
            "pyproject.toml",
            "Cargo.toml",
            "pom.xml",
            "build.gradle",
            "composer.json",
            "go.mod",
            "Gemfile",
            "pubspec.yaml",
        ]

        # mapping of keywords to framework display names
        keyword_map = {
            # JS/TS
            "react": "React",
            "next": "Next.js",
            "nuxt": "Nuxt",
            "vue": "Vue",
            "angular": "Angular",
            "express": "Express",
            "nestjs": "NestJS",
            "electron": "Electron",
            "playwright": "Playwright",
            "jest": "Jest",
            "vitest": "Vitest",
            # Python
            "fastapi": "FastAPI",
            "django": "Django",
            "flask": "Flask",
            "pytest": "pytest",
            "sqlalchemy": "SQLAlchemy",
            "pydantic": "Pydantic",
            "celery": "Celery",
            "streamlit": "Streamlit",
            "ruff": "Ruff",
            "black": "Black",
            "mypy": "mypy",
            "poetry": "Poetry",
            "setuptools": "setuptools",
            # Java
            "spring": "Spring",
            "spring-boot": "Spring Boot",
            "quarkus": "Quarkus",
            # Rust
            "actix": "Actix",
            "rocket": "Rocket",
            "tokio": "Tokio",
            # Go
            "gin": "Gin",
            "fiber": "Fiber",
            "echo": "Echo",
            # Dart/Flutter
            "flutter": "Flutter",
        }

        category_map: dict[str, str] = {
            # User-facing frameworks
            "React": "frameworks",
            "Next.js": "frameworks",
            "Nuxt": "frameworks",
            "Vue": "frameworks",
            "Angular": "frameworks",
            "Express": "frameworks",
            "NestJS": "frameworks",
            "Electron": "frameworks",
            "FastAPI": "frameworks",
            "Django": "frameworks",
            "Flask": "frameworks",
            "SQLAlchemy": "frameworks",
            "Pydantic": "frameworks",
            "Celery": "frameworks",
            "Streamlit": "frameworks",
            "Spring": "frameworks",
            "Spring Boot": "frameworks",
            "Quarkus": "frameworks",
            "Actix": "frameworks",
            "Rocket": "frameworks",
            "Gin": "frameworks",
            "Fiber": "frameworks",
            "Echo": "frameworks",
            "Flutter": "frameworks",
            "Node.js": "frameworks",
            # Testing
            "Playwright": "testing",
            "Jest": "testing",
            "Vitest": "testing",
            "pytest": "testing",
            # Developer tools
            "Ruff": "developer_tools",
            "Black": "developer_tools",
            "mypy": "developer_tools",
            # Build tools
            "Poetry": "build_tools",
            "setuptools": "build_tools",
        }

        # allowed manifest files and code extensions per framework display name
        allowed_manifests: dict[str, set[str]] = {
            "React": {"package.json"},
            "Next.js": {"package.json"},
            "Nuxt": {"package.json"},
            "Vue": {"package.json"},
            "Angular": {"package.json"},
            "Express": {"package.json"},
            "NestJS": {"package.json"},
            "Electron": {"package.json"},
            "Playwright": {"package.json"},
            "Jest": {"package.json"},
            "Vitest": {"package.json"},
            "FastAPI": {"requirements.txt", "pyproject.toml"},
            "Django": {"requirements.txt", "pyproject.toml"},
            "Flask": {"requirements.txt", "pyproject.toml"},
            "pytest": {"requirements.txt", "pyproject.toml"},
            "SQLAlchemy": {"requirements.txt", "pyproject.toml"},
            "Pydantic": {"requirements.txt", "pyproject.toml"},
            "Celery": {"requirements.txt", "pyproject.toml"},
            "Streamlit": {"requirements.txt", "pyproject.toml"},
            "Ruff": {"requirements.txt", "pyproject.toml"},
            "Black": {"requirements.txt", "pyproject.toml"},
            "mypy": {"requirements.txt", "pyproject.toml"},
            "Poetry": {"pyproject.toml", "requirements.txt"},
            "setuptools": {"pyproject.toml", "requirements.txt"},
            "Spring": {"pom.xml", "build.gradle"},
            "Spring Boot": {"pom.xml", "build.gradle"},
            "Quarkus": {"pom.xml", "build.gradle"},
            "Actix": {"Cargo.toml"},
            "Rocket": {"Cargo.toml"},
            "Tokio": {"Cargo.toml"},
            "Gin": {"go.mod"},
            "Fiber": {"go.mod"},
            "Echo": {"go.mod"},
            "Flutter": {"pubspec.yaml"},
            "Node.js": {"package.json"},
        }

        allowed_exts: dict[str, set[str]] = {
            "React": {".js", ".jsx", ".ts", ".tsx"},
            "Next.js": {".js", ".jsx", ".ts", ".tsx"},
            "Nuxt": {".js", ".ts"},
            "Vue": {".js", ".vue", ".ts"},
            "Angular": {".ts"},
            "Express": {".js", ".ts"},
            "NestJS": {".ts"},
            "Electron": {".js", ".ts"},
            "Playwright": {".js", ".ts", ".py"},
            "Jest": {".js", ".ts"},
            "Vitest": {".js", ".ts"},
            "FastAPI": {".py"},
            "Django": {".py"},
            "Flask": {".py"},
            "pytest": {".py"},
            "SQLAlchemy": {".py"},
            "Pydantic": {".py"},
            "Celery": {".py"},
            "Streamlit": {".py"},
            "Ruff": {".py"},
            "Black": {".py"},
            "mypy": {".py"},
            "Poetry": {".py"},
            "setuptools": {".py"},
            "Spring": {".java"},
            "Spring Boot": {".java"},
            "Quarkus": {".java"},
            "Actix": {".rs"},
            "Rocket": {".rs"},
            "Tokio": {".rs"},
            "Gin": {".go"},
            "Fiber": {".go"},
            "Echo": {".go"},
            "Flutter": {".dart"},
            "Node.js": {".js", ".ts"},
        }

        # Evidence tracking structures
        # sources: framework -> {source_type: count}
        sources: dict[str, dict[str, int]] = {}
        weighted_scores: dict[str, int] = {}

        TIER_WEIGHTS = {"tier1": 100, "tier2": 30, "tier3": 5}

        def add_evidence(name: str, source: str, tier: str, count: int = 1) -> None:
            nonlocal sources, weighted_scores
            if name not in sources:
                sources[name] = {}
            sources[name][source] = sources[name].get(source, 0) + count
            weighted_scores[name] = weighted_scores.get(name, 0) + TIER_WEIGHTS.get(tier, 0) * count

        import re

        def dep_matches_keyword(dep_name: str, kw: str) -> bool:
            # match exact package name, scoped names, or path segments like github.com/x/kw
            dep_name = dep_name.lower()
            kw = kw.lower()
            # exact match
            if dep_name == kw:
                return True
            # scoped or names like @org/kw or org/kw
            if dep_name.endswith(f"/{kw}"):
                return True
            # kebab variants like kw-core, kw-server
            if re.match(rf"^{re.escape(kw)}([\-@/].*)?$", dep_name):
                return True
            return False

        # Tier 1: dependency declarations (high confidence)
        for fname in manifests:
            text = self.client.get_repository_file_text(owner, repo, fname)
            if not text:
                continue
            blob = text.lower()

            if fname == "package.json":
                try:
                    import json

                    parsed = json.loads(text)
                    deps = {}
                    for key in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
                        section = parsed.get(key) or {}
                        if isinstance(section, dict):
                            for k in section.keys():
                                deps[k.lower()] = key

                    for dep_name, origin in deps.items():
                        for kw, display in keyword_map.items():
                            if dep_matches_keyword(dep_name, kw):
                                # only add package.json evidence if this framework accepts package.json
                                allowed = allowed_manifests.get(display, set())
                                if "package.json" in allowed or not allowed:
                                    add_evidence(display, f"package.json ({origin})", "tier1", 1)
                                    # also mark testing frameworks specially (no-op if not applicable)
                                    if kw in ("jest", "vitest", "playwright", "pytest"):
                                        add_evidence(display, "package.json (testing)", "tier1", 0)
                except Exception:
                    pass
            else:
                # generic structured manifests: look for known tokens/identifiers
                lines = [l.strip().lower() for l in text.splitlines() if l.strip()]
                for line in lines:
                    for kw, display in keyword_map.items():
                        if re.search(rf"\b{re.escape(kw)}\b", line):
                            allowed = allowed_manifests.get(display, set())
                            if fname in allowed:
                                add_evidence(display, f"{fname}", "tier1", 1)

        # Tier 2: actual code usage (imports / require / from ... import)
        # Try to scan a limited set of likely source files to avoid heavy API usage
        try:
            tree = self.client.get_repository_tree(owner, repo)
        except Exception:
            tree = []

        code_exts = (".js", ".ts", ".jsx", ".tsx", ".py", ".go", ".java", ".rs", ".dart", ".rb")
        excluded_prefixes = ("docs/", "doc/", "examples/", "example/", "fixtures/", "benchmarks/", "generated/", "dist/", "build/")
        candidate_files = [p for p in tree if p.lower().endswith(code_exts) and not p.startswith(excluded_prefixes)] if tree else []
        # prioritize files in src/, lib/, packages/
        priority = [p for p in candidate_files if p.startswith("src/") or p.startswith("lib/") or p.startswith("packages/")]
        others = [p for p in candidate_files if p not in priority]
        files_to_check = (priority + others)[:200]

        # Use regex to extract module paths from import/require statements
        module_regex = re.compile(r"['\"]([^'\"\s]+)['\"]")
        for path in files_to_check:
            text = self.client.get_repository_file_text(owner, repo, path)
            if not text:
                continue
            blob = text
            # find quoted module strings and check module base names
            modules = module_regex.findall(blob)
            file_ext = Path(path).suffix.lower()
            for mod in modules:
                mod_lower = mod.lower()
                base = mod_lower.split("/")[-1]
                for kw, display in keyword_map.items():
                    allowed_e = allowed_exts.get(display)
                    if allowed_e and file_ext not in allowed_e:
                        continue
                    if dep_matches_keyword(base, kw) or dep_matches_keyword(mod_lower, kw):
                        # count as tier2 evidence for code usage
                        add_evidence(display, f"code:{path}", "tier2", 1)

        # Tier 3: documentation references (README, docs)
        readme = self.client.get_repository_file_text(owner, repo, "README.md") or ""
        if readme:
            blob = readme
            for kw, display in keyword_map.items():
                cnt = len(re.findall(rf"\b{re.escape(kw)}\b", blob.lower()))
                if cnt:
                    add_evidence(display, "README.md", "tier3", cnt)

        # infer Node.js presence from languages
        if any(l.lower() in ("javascript", "typescript") for l in lang_list):
            add_evidence("Node.js", "languages", "tier1", 1)

        primary_technology = lang_list[0] if lang_list else None
        identity = RepositoryIdentityAnalyzer().analyze(
            owner,
            repo,
            metadata,
            set(weighted_scores.keys()),
            primary_technology=primary_technology,
        )
        primary_framework = identity.get("primary_framework")
        if isinstance(primary_framework, str) and primary_framework:
            weighted_scores[primary_framework] = weighted_scores.get(primary_framework, 0) + 250
            add_evidence(primary_framework, "identity", "tier1", 1)

        # Build technology list with aggregated evidence and compute normalized scores
        technologies: list[dict[str, object]] = []
        if weighted_scores:
            max_weight = max(weighted_scores.values())
            for name, weight in sorted(weighted_scores.items(), key=lambda kv: kv[1], reverse=True):
                # normalize to 40..95
                score = 40
                if max_weight > 0:
                    score += int((weight / max_weight) * 55)
                score = min(100, score)
                # count tier1 sources
                srcs = sources.get(name, {})
                tier1_count = sum(v for s, v in srcs.items() if any(m in s for m in manifests) or "package.json" in s or s == "languages")
                category = category_map.get(str(name), "frameworks")
                technologies.append({
                    "name": name,
                    "weighted": weight,
                    "score": score,
                    "sources": srcs,
                    "tier1_count": tier1_count,
                    "category": category,
                })

        frameworks_list = [item for item in technologies if item.get("category") == "frameworks"]
        testing_list = [item for item in technologies if item.get("category") == "testing"]
        developer_tools_list = [item for item in technologies if item.get("category") == "developer_tools"]
        build_tools_list = [item for item in technologies if item.get("category") == "build_tools"]

        # Include sources for debugging transparency
        return {
            "identity": identity,
            "languages": language_breakdown[:10],
            "frameworks": frameworks_list,
            "testing": testing_list,
            "developer_tools": developer_tools_list,
            "build_tools": build_tools_list,
            "sources": sources,
        }

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
