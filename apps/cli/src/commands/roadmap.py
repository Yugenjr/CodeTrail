from typer import Typer


def register(app: Typer) -> None:
    @app.command(name="roadmap")
    def roadmap() -> None:
        """Generate a roadmap."""
        return None
