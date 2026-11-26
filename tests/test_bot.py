from app.bot.responses import RESPUESTA_POR_DEFECTO, RESPUESTAS


def enviar(client, message):
    return client.post("/enviar_mensaje", json={"message": message})


def test_saludo(client):
    response = enviar(client, "hola")
    assert response.status_code == 200
    assert response.get_json()["response"] == RESPUESTAS["hola"]


def test_mensaje_desconocido(client):
    response = enviar(client, "algo que el bot no conoce")
    assert response.status_code == 200
    assert response.get_json()["response"] == RESPUESTA_POR_DEFECTO


def test_tildes_mayusculas_y_espacios(client):
    response = enviar(client, "  Batería  ")
    assert response.get_json()["response"] == RESPUESTAS["bateria"]

    response = enviar(client, "Velocidad   MÁXIMA")
    assert response.get_json()["response"] == RESPUESTAS["velocidad maxima"]


def test_aceleracion_devuelve_texto(client):
    response = enviar(client, "aceleracion")
    assert isinstance(response.get_json()["response"], str)


def test_sin_json_devuelve_400(client):
    response = client.post("/enviar_mensaje", data="hola", content_type="text/plain")
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_json_invalido_devuelve_400(client):
    response = client.post("/enviar_mensaje", data="{no es json", content_type="application/json")
    assert response.status_code == 400


def test_sin_message_devuelve_400(client):
    response = client.post("/enviar_mensaje", json={"otro": "campo"})
    assert response.status_code == 400


def test_message_no_texto_devuelve_400(client):
    response = client.post("/enviar_mensaje", json={"message": 123})
    assert response.status_code == 400


def test_message_demasiado_largo(client):
    response = enviar(client, "a" * 501)
    assert response.status_code == 400
