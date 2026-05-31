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
        lang_table = Table(title="Languages")
        lang_table.add_column("Language", style="cyan")
        for lang in stack.get("languages", []):
            lang_table.add_row(lang)

        fw_table = Table(title="Frameworks")
        fw_table.add_column("Framework", style="cyan")
        for fw in stack.get("frameworks", []):
            fw_table.add_row(fw)

        console.print(lang_table)
        console.print(fw_table)

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