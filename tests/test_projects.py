import io

import pytest

from app.extensions import db
from app.models import Img
from app.projects.forms import detect_image_mimetype

# Cabeceras de firma minimas: la validacion solo mira los primeros bytes.
FIRMAS = {
    "jpg": (b"\xff\xd8\xff\xe0" + b"\0" * 32, "image/jpeg"),
    "jpeg": (b"\xff\xd8\xff\xe0" + b"\0" * 32, "image/jpeg"),
    "gif": (b"GIF89a" + b"\0" * 32, "image/gif"),
    "webp": (b"RIFF\x00\x00\x00\x00WEBP" + b"\0" * 32, "image/webp"),
}

DATOS = {
    "project_name": "McLaren MP4/4",
    "motor": "V6 Biturbo",
    "power": "650 hp",
    "acceleration": "2.4 s",
    "top_speed": "330 km/h",
}


def subir(client, contenido, nombre="coche.png", **campos):
    data = {**DATOS, **campos}
    if contenido is not None:
        data["pic"] = (io.BytesIO(contenido), nombre)
    return client.post("/upload", data=data, content_type="multipart/form-data")


def contar(app):
    with app.app_context():
        return db.session.query(Img).count()


def test_subida_valida_redirige_y_guarda(app, client, png_bytes):
    response = subir(client, png_bytes)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/proyectos")
    assert contar(app) == 1

    with app.app_context():
        img = db.session.query(Img).first()
        assert img.mimetype == "image/png"
        assert img.project_name == DATOS["project_name"]
        img_id = img.id

    response = client.get(f"/{img_id}")
    assert response.status_code == 200
    assert response.mimetype == "image/png"
    assert response.data == png_bytes
    assert response.headers["X-Content-Type-Options"] == "nosniff"

    galeria = client.get("/proyectos").get_data(as_text=True)
    assert DATOS["project_name"] in galeria


@pytest.mark.parametrize("extension", sorted(FIRMAS))
def test_otros_formatos_permitidos(app, client, extension):
    contenido, mimetype = FIRMAS[extension]
    response = subir(client, contenido, f"coche.{extension}")
    assert response.status_code == 302
    with app.app_context():
        img = db.session.query(Img).one()
        assert img.mimetype == mimetype
        assert img.name.endswith("." + extension)


def test_detect_image_mimetype(png_bytes):
    assert detect_image_mimetype(png_bytes) == "image/png"
    assert detect_image_mimetype(FIRMAS["gif"][0]) == "image/gif"
    assert detect_image_mimetype(FIRMAS["webp"][0]) == "image/webp"
    assert detect_image_mimetype(b"<html>") is None
    assert detect_image_mimetype(b"") is None


def test_texto_renombrado_como_png_se_rechaza(app, client):
    response = subir(client, b"<script>alert(1)</script>", "falso.png")
    assert response.status_code == 400
    assert "no es una imagen" in response.get_data(as_text=True)
    assert contar(app) == 0


def test_extension_no_permitida(app, client, png_bytes):
    response = subir(client, png_bytes, "programa.exe")
    assert response.status_code == 400
    assert contar(app) == 0


def test_archivo_vacio(app, client):
    response = subir(client, b"", "vacio.png")
    assert response.status_code == 400
    assert contar(app) == 0


def test_sin_archivo(app, client):
    response = subir(client, None)
    assert response.status_code == 400
    assert contar(app) == 0


def test_campo_faltante_o_vacio(app, client, png_bytes):
    response = subir(client, png_bytes, motor="   ")
    assert response.status_code == 400
    assert "obligatorio" in response.get_data(as_text=True)
    assert contar(app) == 0


def test_campo_demasiado_largo(app, client, png_bytes):
    response = subir(client, png_bytes, project_name="x" * 101)
    assert response.status_code == 400
    assert contar(app) == 0


def test_error_se_escapa_y_conserva_valores(client, png_bytes):
    response = subir(client, b"no imagen", "a.png", project_name="<b>Mi auto</b>")
    html = response.get_data(as_text=True)
    assert "&lt;b&gt;Mi auto&lt;/b&gt;" in html
    assert "<b>Mi auto</b>" not in html


def test_archivo_demasiado_grande_devuelve_413(app, client, png_bytes):
    app.config["MAX_CONTENT_LENGTH"] = 1024
    response = subir(client, png_bytes + b"\0" * 4096)
    assert response.status_code == 413
    assert contar(app) == 0


def test_imagen_inexistente_devuelve_404(client):
    assert client.get("/9999").status_code == 404


def test_registro_antiguo_con_mimetype_peligroso(app, client):
    with app.app_context():
        img = Img(
            img=b"<script>alert(1)</script>",
            name="x.html",
            mimetype="text/html",
            **DATOS,
        )
        db.session.add(img)
        db.session.commit()
        img_id = img.id

    response = client.get(f"/{img_id}")
    assert response.mimetype == "application/octet-stream"
