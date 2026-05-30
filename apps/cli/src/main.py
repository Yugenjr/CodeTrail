from typer import Typer

from commands.login import register as register_login
from commands.logout import register as register_logout
from commands.profile import register as register_profile

app = Typer(add_completion=False, no_args_is_help=True, help="CodeTrail CLI")

register_login(app)
register_logout(app)
register_profile(app)
