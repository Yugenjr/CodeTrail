from rich.console import Console
from typer import Exit, Typer, prompt

from utils.config import ConfigManager
from utils.github_client import GitHubClient


def register(app: Typer) -> None:
    @app.command(name="login")
    def login() -> None:
        """Log in to CodeTrail using a GitHub personal access token."""

        token = prompt("Enter GitHub Personal Access Token", hide_input=True)
        client = GitHubClient(token=token)

        if not client.validate_token():
            Console().print("[red]Invalid GitHub token. Please try again.[/red]")
            raise Exit(code=1)

        user = client.get_user()
        ConfigManager().set_github_token(token)
        username = user.get("login", "unknown")
        print(f"Authenticated successfully as {username}.")
