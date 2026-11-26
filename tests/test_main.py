import pytest

from app import create_app


@pytest.mark.parametrize(
    "url",
    ["/", "/mythcar", "/proyectos", "/bot", "/politica", "/terminos", "/upload_page"],
)
def test_paginas_principales_responden_200(client, url):
    response = client.get(url)
    assert response.status_code == 200
    assert response.mimetype == "text/html"


def test_cabeceras_de_seguridad(client):
    response = client.get("/")
    assert response.headers["X-Content-Type-Options"] == "nosniff"


def test_ruta_inexistente_devuelve_404_con_plantilla(client):
    response = client.get("/no-existe")
    assert response.status_code == 404
    assert "Error 404" in response.get_data(as_text=True)


def test_404_anidado_no_rompe(client):
    response = client.get("/a/b/c")
    assert response.status_code == 404


def test_metodo_no_permitido(client):
    response = client.get("/upload")
    assert response.status_code == 405


def test_error_500_devuelve_json_al_bot(app, client, monkeypatch):
    import app.bot.routes as bot_routes

    def fallar(_mensaje):
        raise RuntimeError("fallo simulado")

    monkeypatch.setattr(bot_routes, "obtener_respuesta", fallar)
    app.config["PROPAGATE_EXCEPTIONS"] = False
    response = client.post("/enviar_mensaje", json={"message": "hola"})
    assert response.status_code == 500
    assert "response" in response.get_json()


def test_app_env_por_defecto_es_produccion(monkeypatch):
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.delenv("SECRET_KEY", raising=False)
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        create_app()


def test_produccion_sin_secret_key_falla(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    with pytest.raises(RuntimeError, match="SECRET_KEY"):
        create_app("production")


def test_produccion_sin_debug(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "x" * 32)
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setenv("FLASK_DEBUG", "1")
    app = create_app("production")
    assert app.debug is False


def test_desarrollo_debug_desactivado_por_defecto(monkeypatch):
    monkeypatch.delenv("FLASK_DEBUG", raising=False)
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    app = create_app("development")
    assert app.debug is False
    assert app.config["SECRET_KEY"]


def test_app_env_desconocido(monkeypatch):
    with pytest.raises(RuntimeError, match="APP_ENV"):
        create_app("inventado")
