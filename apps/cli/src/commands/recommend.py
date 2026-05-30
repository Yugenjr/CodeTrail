from typer import Typer


def register(app: Typer) -> None:
    @app.command(name="recommend")
    def recommend() -> None:
        """Recommend issues."""
        return None
