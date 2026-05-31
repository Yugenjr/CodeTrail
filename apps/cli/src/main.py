from typer import Typer

from commands.login import register as register_login
from commands.logout import register as register_logout
from commands.profile import register as register_profile
from commands.repo import register as register_repo
from commands.issues import register as register_issues
from commands.find import register as register_find
from commands.analyze import register as register_analyze
from commands.recommend import register as register_recommend
from commands.roadmap import register as register_roadmap

app = Typer(add_completion=False, no_args_is_help=True, help="CodeTrail CLI")

register_login(app)
register_logout(app)
register_profile(app)
register_repo(app)
register_issues(app)
register_find(app)
register_analyze(app)
register_recommend(app)
register_roadmap(app)
