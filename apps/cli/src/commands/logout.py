from typer import Typer

from utils.config import ConfigManager


def register(app: Typer) -> None:
    @app.command(name="logout")
    def logout() -> None:
        """Remove the stored GitHub token."""

        ConfigManager().remove_github_token()
        print("Logged out successfully.")