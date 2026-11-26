"""Pruebas de rutas y plantillas del rediseno (pytest).

Uso local: pip install -r requeriments.txt pytest  y luego  python -m pytest tests
Nota: no se ejecutaron en el contenedor de revision (no tiene Python).
"""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from app import app, obtener_respuesta  # noqa: E402

PAGES = ["/", "/mythcar", "/proyectos", "/upload_page", "/bot", "/politica", "/terminos"]

# Restos del frontend anterior que no deben aparecer en ninguna pagina.
OLD_ASSETS = [
    b"mainpage.css", b"mythcar.css", b"proyectos.css", b"upload.css", b"bot.css",
    b"static\\",
]


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


@pytest.mark.parametrize("url", PAGES)
def test_pagina_responde_200(client, url):
    assert client.get(url).status_code == 200


@pytest.mark.parametrize("url", PAGES)
def test_pagina_usa_base_comun(client, url):
    body = client.get(url).data
    assert b'<html lang="es">' in body
    assert b"css/main.css" in body
    assert b"Saltar al contenido" in body
    assert b'<nav id="site-nav"' in body
    assert b"<footer" in body


@pytest.mark.parametrize("url", PAGES)
def test_pagina_tiene_un_solo_h1(client, url):
    assert client.get(url).data.count(b"<h1") == 1


@pytest.mark.parametrize("url", PAGES)
def test_sin_rutas_ni_css_antiguos(client, url):
    body = client.get(url).data
    for old in OLD_ASSETS:
        assert old not in body, old


def test_enlace_asistencia_apunta_al_bot(client):
    body = client.get("/").data
    assert b'<a href="/bot">Asistencia Virtual</a>' in body
    assert b'href="#">Asistencia Virtual' not in body


def test_pagina_activa_marcada(client):
    assert b'<a href="/mythcar" aria-current="page">' in client.get("/mythcar").data
    assert b'<a href="/mythcar" aria-current="page">' not in client.get("/bot").data


def test_catalogo_tiene_14_coches(client):
    assert client.get("/mythcar").data.count(b'<article class="car"') == 14


def test_bot_tiene_formulario_y_region_en_vivo(client):
    body = client.get("/bot").data
    assert b'id="chat-form"' in body
    assert b'for="user-message"' in body
    assert b'role="log"' in body
    assert b'aria-live="polite"' in body


def test_enviar_mensaje_hola(client):
    res = client.post("/enviar_mensaje", json={"message": "hola"})
    assert res.status_code == 200
    assert res.get_json()["response"].startswith("¡Hola!")


def test_enviar_mensaje_desconocido(client):
    res = client.post("/enviar_mensaje", json={"message": "xyz"})
    assert res.get_json()["response"] == "Lo siento, no entendí esa pregunta."


def test_obtener_respuesta_sin_distinguir_mayusculas():
    assert obtener_respuesta("COMANDOS").startswith("Estos son los comandos")


def test_obtener_respuesta_aceleracion_es_lista():
    respuesta = obtener_respuesta("aceleracion")
    assert isinstance(respuesta, tuple)
    assert len(respuesta) == 2
