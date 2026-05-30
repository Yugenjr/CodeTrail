from rich.console import Console
from rich.table import Table
from typer import Exit, Option, Typer

from utils.config import ConfigManager
from utils.github_client import GitHubClient
from utils.skill_analysis import SkillAnalysisService


def register(app: Typer) -> None:
    @app.command(name="profile")
    def profile(
        skills: bool = Option(False, "--skills", help="Analyze repositories and display detected skills."),
    ) -> None:
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

        console = Console()
        console.print(table)

        if not skills:
            return

        analysis = SkillAnalysisService(client=client).analyze()
        console.print()
        console.print(f"[bold]Skill graph for {analysis.username}[/bold]")

        language_table = Table(title="Languages", show_lines=False)
        language_table.add_column("Language", style="cyan")
        language_table.add_column("Bytes", justify="right")
        language_table.add_column("Score", justify="right")
        for node in [item for item in analysis.nodes if item.category == "language"]:
            language_table.add_row(node.name, str(analysis.language_totals.get(node.name, 0)), f"{node.score}%")

        framework_table = Table(title="Frameworks", show_lines=False)
        framework_table.add_column("Framework", style="cyan")
        framework_table.add_column("Evidence", justify="right")
        framework_table.add_column("Score", justify="right")
        for node in [item for item in analysis.nodes if item.category == "framework"]:
            framework_table.add_row(node.name, str(node.evidence_count), f"{node.score}%")

        console.print(language_table)
        console.print(framework_table)
