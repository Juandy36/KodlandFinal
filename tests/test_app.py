"""Pruebas de la app. Ejecutar desde la raiz del proyecto con:

    python -m unittest discover -s tests -v
"""
import io
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import RESPUESTAS, create_app, obtener_respuesta  # noqa: E402
from db import db  # noqa: E402

# Cabecera minima de un PNG valido de 1x1, suficiente para la prueba
PNG_1X1 = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
    "0000000d4944415478da63f8cfc0f01f0005050201a5b1f0f00000000049454e44ae426082"
)

DATOS_PROYECTO = {
    "project_name": "Proyecto de prueba",
    "motor": "V8 5.0L",
    "power": "450 hp",
    "acceleration": "4.2 segundos",
    "top_speed": "290 km/h",
}


class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite://"})
        self.client = self.app.test_client()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def subir(self, contenido=PNG_1X1, nombre="foto.png", mimetype="image/png", **extra):
        datos = dict(DATOS_PROYECTO, **extra)
        if contenido is not None:
            datos["pic"] = (io.BytesIO(contenido), nombre, mimetype)
        return self.client.post("/upload", data=datos, content_type="multipart/form-data")

    # --- Paginas ---------------------------------------------------------
    def test_paginas_responden_200(self):
        for ruta in ("/", "/mythcar", "/proyectos", "/upload_page", "/bot", "/politica", "/terminos"):
            with self.subTest(ruta=ruta):
                self.assertEqual(self.client.get(ruta).status_code, 200)

    def test_estaticos_existen(self):
        for ruta in ("/static/css/mainpage.css", "/static/css/bot.css", "/static/img/Logo.ico",
                     "/static/img/nsxahora.jpg"):
            with self.subTest(ruta=ruta):
                respuesta = self.client.get(ruta)
                self.assertEqual(respuesta.status_code, 200)
                respuesta.close()

    def test_plantillas_no_usan_barra_invertida(self):
        html = self.client.get("/mythcar").get_data(as_text=True)
        self.assertNotIn("static\\", html)
        self.assertIn("/static/img/f40.jfif", html)

    # --- Asistente -------------------------------------------------------
    def test_chat_responde(self):
        respuesta = self.client.post("/enviar_mensaje", json={"message": "hola"})
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.get_json()["response"], RESPUESTAS["hola"])

    def test_chat_normaliza_acentos_y_mayusculas(self):
        self.assertEqual(obtener_respuesta("  ¡Aceleración!  "), RESPUESTAS["aceleracion"])
        self.assertEqual(obtener_respuesta("Humo   Azul"), RESPUESTAS["humo azul"])

    def test_aceleracion_es_texto(self):
        respuesta = self.client.post("/enviar_mensaje", json={"message": "aceleracion"})
        self.assertIsInstance(respuesta.get_json()["response"], str)

    def test_todas_las_respuestas_son_texto(self):
        for comando, texto in RESPUESTAS.items():
            with self.subTest(comando=comando):
                self.assertIsInstance(texto, str)

    def test_chat_mensaje_desconocido(self):
        respuesta = self.client.post("/enviar_mensaje", json={"message": "xyz"})
        self.assertEqual(respuesta.status_code, 200)
        self.assertIn("no entendí", respuesta.get_json()["response"])

    def test_chat_sin_datos_devuelve_400(self):
        self.assertEqual(self.client.post("/enviar_mensaje", json={}).status_code, 400)
        self.assertEqual(self.client.post("/enviar_mensaje").status_code, 400)
        self.assertEqual(self.client.post("/enviar_mensaje", json={"message": 5}).status_code, 400)
        self.assertEqual(self.client.post("/enviar_mensaje", json=["hola"]).status_code, 400)

    # --- Subida e imagenes -----------------------------------------------
    def test_subida_valida_redirige_y_se_ve(self):
        respuesta = self.subir()
        self.assertEqual(respuesta.status_code, 302)

        imagen = self.client.get("/img/1")
        self.assertEqual(imagen.status_code, 200)
        self.assertEqual(imagen.mimetype, "image/png")
        self.assertEqual(imagen.data, PNG_1X1)

        self.assertIn("Proyecto de prueba", self.client.get("/proyectos").get_data(as_text=True))
        self.assertIn("/img/1", self.client.get("/").get_data(as_text=True))

    def test_subida_sin_imagen_devuelve_400(self):
        self.assertEqual(self.subir(contenido=None).status_code, 400)

    def test_subida_de_no_imagen_devuelve_400(self):
        self.assertEqual(self.subir(contenido=b"hola", nombre="nota.txt", mimetype="text/plain").status_code, 400)

    def test_subida_con_campo_vacio_devuelve_400(self):
        self.assertEqual(self.subir(motor="   ").status_code, 400)

    def test_imagen_inexistente_devuelve_404(self):
        self.assertEqual(self.client.get("/img/999").status_code, 404)


if __name__ == "__main__":
    unittest.main()
