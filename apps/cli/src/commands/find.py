from typer import Typer


def register(app: Typer) -> None:
    @app.command(name="find")
    def find() -> None:
        """Find candidate issues."""
        return None
