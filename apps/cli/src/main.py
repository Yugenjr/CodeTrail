from typer import Typer

from commands.analyze import register as register_analyze
from commands.find import register as register_find
from commands.login import register as register_login
from commands.profile import register as register_profile
from commands.recommend import register as register_recommend
from commands.roadmap import register as register_roadmap

app = Typer(add_completion=False, no_args_is_help=True)

register_login(app)
register_profile(app)
register_find(app)
register_recommend(app)
register_analyze(app)
register_roadmap(app)
