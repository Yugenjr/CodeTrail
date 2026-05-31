from typer import Typer, Argument, Option
from rich.console import Console
from rich.table import Table

from utils.config import ConfigManager
from utils.github_client import GitHubClient
from utils.repo_utils import RepositoryResolver, RepositoryAnalyzer


def register(app: Typer) -> None:
    repo_app = Typer()

    @repo_app.command(name="info")
    def info(
        repo: str | None = Argument(None, help="owner/repo to inspect (optional)"),
        repo_opt: str | None = Option(None, "--repo", "-r", help="owner/repo to inspect (optional)"),
    ) -> None:
        """Show basic repository metadata for the current or an explicit repository.

        If `owner/repo` is omitted the command will attempt to detect the repository
        from the local `.git` configuration or `git remote get-url origin`.
        """
        console = Console()
        try:
            explicit = repo_opt or repo
            owner, name = RepositoryResolver().resolve(explicit)
        except ValueError as exc:
            console.print(f"[red]{exc}[/red]")
            return

        token = ConfigManager().get_github_token()
        client = GitHubClient(token=token) if token else GitHubClient(token="")
        analyzer = RepositoryAnalyzer(client=client)
        meta = analyzer.metadata(owner, name)

        if not meta:
            console.print("[red]Repository not found[/red]")
            return

        table = Table(title="Repository")
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="white")
        table.add_row("Full Name", meta.get("full_name", f"{owner}/{name}"))
        table.add_row("Description", str(meta.get("description") or "-"))
        table.add_row("Stars", str(meta.get("stargazers_count", 0)))
        table.add_row("Forks", str(meta.get("forks_count", 0)))
        table.add_row("Primary Language", str(meta.get("language") or "-"))
        table.add_row("Open Issues", str(meta.get("open_issues_count", 0)))
        # commit count (may be estimated via Link header)
        commit_count = None
        try:
            commit_count = client.get_commit_count(owner, name)
        except Exception:
            commit_count = None
        table.add_row("Commits", str(commit_count) if isinstance(commit_count, int) else "-")

        console.print(table)

    @repo_app.command(name="stack")
    def stack(
        repo: str | None = Argument(None, help="owner/repo to inspect (optional)"),
        repo_opt: str | None = Option(None, "--repo", "-r", help="owner/repo to inspect (optional)"),
        debug: bool = Option(False, "--debug", help="Show detailed framework evidence and sources"),
    ) -> None:
        """Detect high-level languages and frameworks for a repository.

        Uses root-level manifests for a fast, shallow detection (keeps analysis quick).
        """
        console = Console()
        try:
            explicit = repo_opt or repo
            owner, name = RepositoryResolver().resolve(explicit)
        except ValueError as exc:
            console.print(f"[red]{exc}[/red]")
            return

        token = ConfigManager().get_github_token()
        client = GitHubClient(token=token) if token else GitHubClient(token="")
        analyzer = RepositoryAnalyzer(client=client)
        stack = analyzer.stack(owner, name)

        console.print("[bold]Repository Stack[/bold]\n")
        identity = stack.get("identity", {}) or {}
        console.print("[bold]Repository Identity[/bold]")
        console.print(f"Primary Framework: {identity.get('primary_framework') or 'Unknown'}")
        if identity.get("primary_technology"):
            console.print(f"Primary Technology: {identity.get('primary_technology')}")
        console.print(f"Repository Type: {identity.get('repository_type') or '-'}\n")

        lang_table = Table(title="Languages")
        lang_table.add_column("Language", style="cyan")
        lang_table.add_column("Percent", justify="right")
        for lang in stack.get("languages", []):
            if isinstance(lang, dict):
                lang_table.add_row(str(lang.get("name", "-")), f"{lang.get('percentage', 0):.1f}%")
            else:
                lang_table.add_row(str(lang), "-")

        console.print(lang_table)

        def render_scored_table(title: str, items: list[dict]) -> None:
            if not items:
                return
            table = Table(title=title)
            table.add_column("Name", style="cyan")
            table.add_column("Evidence", justify="right")
            table.add_column("Score", justify="right")
            for item in items:
                if isinstance(item, dict):
                    name = str(item.get("name", "-"))
                    score = str(item.get("score", "-"))
                    srcs = item.get("sources", {}) or {}
                    tier1 = item.get("tier1_count", 0) or 0
                    total_sources = sum(v for v in srcs.values()) if isinstance(srcs, dict) else 0
                    evidence_display = f"{tier1} deps" if tier1 > 0 else str(total_sources or "-")
                else:
                    name = str(item)
                    evidence_display = "-"
                    score = "-"
                table.add_row(name, evidence_display, score)
            console.print(table)

        render_scored_table("Frameworks", stack.get("frameworks", []))
        render_scored_table("Testing", stack.get("testing", []))
        render_scored_table("Developer Tools", stack.get("developer_tools", []))
        render_scored_table("Build Tools", stack.get("build_tools", []))

        if debug:
            console.print("\n[bold]Framework Evidence Details[/bold]")
            for fw in stack.get("frameworks", []):
                if not isinstance(fw, dict):
                    continue
                console.print(f"\n[underline]{fw.get('name')}[/underline]")
                console.print(f"Score: {fw.get('score')}    Weighted: {fw.get('weighted')}")
                console.print("Evidence Sources:")
                srcs = fw.get("sources", {}) or {}
                for sname, cnt in srcs.items():
                    console.print(f"- {sname}: {cnt}")

        # Category tables above already include testing/developer/build tool details.

    @repo_app.command(name="structure")
    def structure(
        repo: str | None = Argument(None, help="owner/repo to inspect (optional)"),
        repo_opt: str | None = Option(None, "--repo", "-r", help="owner/repo to inspect (optional)"),
    ) -> None:
        """Show important top-level directories and files for a repository.

        This lists likely important directories (`src`, `test`, `extensions`, etc.) and
        common manifest files (`package.json`, `pyproject.toml`, `README.md`).
        """
        console = Console()
        try:
            explicit = repo_opt or repo
            owner, name = RepositoryResolver().resolve(explicit)
        except ValueError as exc:
            console.print(f"[red]{exc}[/red]")
            return

        token = ConfigManager().get_github_token()
        client = GitHubClient(token=token) if token else GitHubClient(token="")
        analyzer = RepositoryAnalyzer(client=client)
        struct = analyzer.structure(owner, name)

        console.print("[bold]Important Directories[/bold]")
        for d in struct.get("important_directories", []):
            console.print(f"- {d}")

        console.print("\n[bold]Important Files[/bold]")
        for f in struct.get("important_files", []):
            console.print(f"- {f}")

    app.add_typer(repo_app, name="repo")