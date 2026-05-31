from typer import Typer, Argument, Option
from rich.console import Console
from rich.table import Table

from utils.config import ConfigManager
from utils.github_client import GitHubClient
from utils.repo_utils import RepositoryResolver, IssueExplorer


def register(app: Typer) -> None:
    issues_app = Typer()

    @issues_app.command(name="list")
    def list_issues(
        repo: str | None = Argument(None, help="owner/repo to inspect (optional)"),
        repo_opt: str | None = Option(None, "--repo", "-r", help="owner/repo to inspect (optional)"),
        limit: int = 30,
        page: int = 1,
    ) -> None:
        """List open issues for the current or specified repository."""
        console = Console()
        try:
            explicit = repo_opt or repo
            owner, name = RepositoryResolver().resolve(explicit)
        except ValueError as exc:
            console.print(f"[red]{exc}[/red]")
            return

        token = ConfigManager().get_github_token()
        client = GitHubClient(token=token) if token else GitHubClient(token="")
        explorer = IssueExplorer(client=client)
        issues = explorer.list_paginated(owner, name, limit=limit, page=page)

        console.print("[bold]Open Issues[/bold]\n")
        if not issues:
            console.print("No open issues found.")
            return
        for issue in issues[:limit]:
            console.print(f"#{issue.get('number')}  {issue.get('title')}")

    @issues_app.command(name="show")
    def show(
        arg1: str | None = Argument(None, help="Issue number or owner/repo"),
        arg2: str | None = Argument(None, help="Issue number or owner/repo"),
        repo_opt: str | None = Option(None, "--repo", "-r", help="owner/repo to inspect (optional)"),
    ) -> None:
        """Show details for a single issue.

        Supports the following forms:
        - `codetrail issues show 123` (uses current repo)
        - `codetrail issues show 123 owner/repo`
        - `codetrail issues show owner/repo 123`
        - `codetrail issues show 123 --repo owner/repo`
        """
        console = Console()

        def is_int(s: str) -> bool:
            try:
                int(s)
                return True
            except Exception:
                return False

        number: int | None = None
        repo_str: str | None = None

        # Prefer explicit flag
        if repo_opt:
            repo_str = repo_opt

        if arg1 and arg2:
            # two positional args provided; determine which is number
            if "/" in arg1 and is_int(arg2):
                repo_str = repo_str or arg1
                number = int(arg2)
            elif is_int(arg1) and "/" in arg2:
                number = int(arg1)
                repo_str = repo_str or arg2
            elif is_int(arg1) and is_int(arg2):
                # ambiguous: prefer first as number
                number = int(arg1)
            else:
                console.print("[red]Could not parse arguments. Use `issues show 123` or `issues show owner/repo 123`.[/red]")
                return
        elif arg1:
            if is_int(arg1):
                number = int(arg1)
            elif "/" in arg1:
                console.print("[red]Repository provided but issue number is missing. Use `issues show owner/repo 123`.[/red]")
                return
            else:
                console.print("[red]Invalid issue number. Provide a numeric issue ID.[/red]")
                return
        else:
            console.print("[red]Missing issue number.[/red]")
            return

        try:
            owner, name = RepositoryResolver().resolve(repo_str)
        except ValueError as exc:
            console.print(f"[red]{exc}[/red]")
            return

        token = ConfigManager().get_github_token()
        client = GitHubClient(token=token) if token else GitHubClient(token="")
        explorer = IssueExplorer(client=client)
        issue = explorer.show(owner, name, number)
        if not issue:
            console.print("[red]Issue not found[/red]")
            return

        table = Table(title=f"Issue #{issue.get('number')}")
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="white")
        table.add_row("Title", issue.get("title", "-"))
        table.add_row("Author", issue.get("user", {}).get("login", "-"))
        labels = ", ".join([l.get("name", "") for l in issue.get("labels", [])])
        table.add_row("Labels", labels or "-")
        table.add_row("State", issue.get("state", "-"))
        table.add_row("Body", issue.get("body", "-")[:1000])

        console.print(table)

    @issues_app.command(name="search")
    def search(
        arg1: str | None = Argument(None, help="Query or owner/repo"),
        arg2: str | None = Argument(None, help="Query or owner/repo"),
        repo_opt: str | None = Option(None, "--repo", "-r", help="owner/repo to inspect (optional)"),
        limit: int = 30,
        page: int = 1,
    ) -> None:
        """Search open issues for a query. Usage examples:

        - `codetrail issues search bug` (search current repo)
        - `codetrail issues search microsoft/vscode bug`
        - `codetrail issues search bug microsoft/vscode`
        """
        console = Console()

        if not arg1:
            console.print("[red]Missing search query.[/red]")
            return

        # Determine which arg is query vs repo
        query: str
        repo_str: str | None = repo_opt

        def looks_like_repo(s: str) -> bool:
            return "/" in s

        if arg2:
            if looks_like_repo(arg1) and not looks_like_repo(arg2):
                repo_str = repo_str or arg1
                query = arg2
            elif looks_like_repo(arg2) and not looks_like_repo(arg1):
                repo_str = repo_str or arg2
                query = arg1
            else:
                # default: first is query
                query = arg1
        else:
            query = arg1

        try:
            owner, name = RepositoryResolver().resolve(repo_str)
        except ValueError as exc:
            console.print(f"[red]{exc}[/red]")
            return

        token = ConfigManager().get_github_token()
        client = GitHubClient(token=token) if token else GitHubClient(token="")
        explorer = IssueExplorer(client=client)
        results = explorer.search(owner, name, query)
        # apply pagination client side if needed
        start = (max(1, page) - 1) * limit
        results = results[start : start + limit]

        console.print("[bold]Matching Issues[/bold]\n")
        if not results:
            console.print("No matching issues found.")
            return
        for issue in results:
            console.print(f"#{issue.get('number')}  {issue.get('title')}")

    @issues_app.command(name="filter")
    def filter_label(
        label: str,
        repo: str | None = Argument(None, help="owner/repo to inspect (optional)"),
        repo_opt: str | None = Option(None, "--repo", "-r", help="owner/repo to inspect (optional)"),
        limit: int = 30,
        page: int = 1,
    ) -> None:
        """List open issues that have the given label (e.g. `good-first-issue`)."""
        console = Console()
        try:
            explicit = repo_opt or repo
            owner, name = RepositoryResolver().resolve(explicit)
        except ValueError as exc:
            console.print(f"[red]{exc}[/red]")
            return

        token = ConfigManager().get_github_token()
        client = GitHubClient(token=token) if token else GitHubClient(token="")
        explorer = IssueExplorer(client=client)
        issues = explorer.list_paginated(owner, name, state="open", limit=limit, page=page)
        # filter by label client-side as a fallback
        issues = [i for i in issues if label in ",".join([l.get("name", "") for l in i.get("labels", [])])]

        console.print(f"[bold]Issues with label '{label}'[/bold]\n")
        if not issues:
            console.print("No issues found with that label.")
            return
        for issue in issues:
            console.print(f"#{issue.get('number')}  {issue.get('title')}")

    app.add_typer(issues_app, name="issues")