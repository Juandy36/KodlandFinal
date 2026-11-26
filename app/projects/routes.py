from flask import Response, abort, current_app, redirect, render_template, request, url_for
from sqlalchemy.orm import defer

from ..extensions import db
from ..models import Img
from . import bp
from .forms import ALLOWED_EXTENSIONS, detect_image_mimetype, validate_project_form


def render_upload_form(errors=None, form=None, status=200):
    return (
        render_template(
            "upload.html",
            errors=errors or [],
            form=form or {},
            accept=",".join("." + ext for ext in sorted(ALLOWED_EXTENSIONS)),
        ),
        status,
    )


@bp.route("/proyectos")
def proyectos():
    images = db.session.execute(
        db.select(Img).options(defer(Img.img)).order_by(Img.id)
    ).scalars().all()
    return render_template("proyectos.html", images=images)


@bp.route("/upload_page")
def upload_page():
    return render_upload_form()


@bp.route("/upload", methods=["POST"])
def upload():
    data, errors = validate_project_form(
        request.form,
        request.files,
        max_bytes=current_app.config.get("MAX_CONTENT_LENGTH"),
    )
    if errors:
        return render_upload_form(errors=errors, form=request.form, status=400)

    db.session.add(Img(**data))
    db.session.commit()
    return redirect(url_for("projects.proyectos"))


# Se mantiene la URL /<id> por compatibilidad con los enlaces existentes.
@bp.route("/<int:id>")
def get_img(id):
    img = db.session.get(Img, id)
    if img is None:
        abort(404)
    # El tipo se recalcula desde el contenido: los registros antiguos guardaban
    # el mimetype que enviaba el navegador y no es de fiar.
    mimetype = detect_image_mimetype(img.img) or "application/octet-stream"
    response = Response(img.img, mimetype=mimetype)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Content-Security-Policy"] = "default-src 'none'; sandbox"
    return response
