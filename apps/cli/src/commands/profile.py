from typer import Typer


def register(app: Typer) -> None:
    @app.command(name="profile")
    def profile() -> None:
        """Show profile information."""
        return None
