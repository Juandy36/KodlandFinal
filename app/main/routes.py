from flask import render_template
from sqlalchemy.orm import defer

from ..extensions import db
from ..models import Img
from . import bp


@bp.route("/")
def home():
    # No se carga el BLOB de la imagen: se sirve aparte en /<id>.
    latest_projects = db.session.execute(
        db.select(Img).options(defer(Img.img)).order_by(Img.id.desc()).limit(3)
    ).scalars().all()
    return render_template("index.html", latest_projects=latest_projects)


@bp.route("/mythcar")
def mythcar():
    return render_template("mythcar.html")


@bp.route("/politica")
def politica_privacidad():
    return render_template("politica_privacidad.html")


@bp.route("/terminos")
def terminos_condiciones():
    return render_template("terminos_condiciones.html")
