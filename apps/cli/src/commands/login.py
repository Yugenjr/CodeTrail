from typer import Typer


def register(app: Typer) -> None:
    @app.command(name="login")
    def login() -> None:
        """Log in to CodeTrail."""
        return None
