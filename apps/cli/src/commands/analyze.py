from typer import Typer


def register(app: Typer) -> None:
    @app.command(name="analyze")
    def analyze() -> None:
        """Analyze an issue."""
        return None
