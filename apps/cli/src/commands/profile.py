from rich.console import Console
from rich.table import Table
from typer import Exit, Typer

from utils.config import ConfigManager
from utils.github_client import GitHubClient


def register(app: Typer) -> None:
    @app.command(name="profile")
    def profile() -> None:
        """Show the authenticated GitHub profile."""

        token = ConfigManager().get_github_token()
        if not token:
            Console().print("[red]No stored GitHub token found. Run 'codetrail login' first.[/red]")
            raise Exit(code=1)

        client = GitHubClient(token=token)
        if not client.validate_token():
            Console().print("[red]Stored GitHub token is invalid. Run 'codetrail login' again.[/red]")
            raise Exit(code=1)

        user = client.get_user()
        table = Table(title="GitHub Profile", show_lines=False)
        table.add_column("Field", style="cyan", no_wrap=True)
        table.add_column("Value", style="white")
        table.add_row("Username", str(user.get("login", "-")))
        table.add_row("Name", str(user.get("name") or "-"))
        table.add_row("Public repositories", str(user.get("public_repos", 0)))
        table.add_row("Followers", str(user.get("followers", 0)))
        table.add_row("Following", str(user.get("following", 0)))

        Console().print(table)
