from flask import Blueprint

bp = Blueprint("bot", __name__)

from . import routes  # noqa: E402,F401
