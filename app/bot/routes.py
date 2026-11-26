from flask import jsonify, render_template, request

from . import bp
from .responses import MAX_MESSAGE_LENGTH, obtener_respuesta


def _error(mensaje, status=400):
    # Tambien se envia en "response" para que bot.html lo muestre en el chat.
    return jsonify({"error": mensaje, "response": mensaje}), status


@bp.route("/bot")
def bot_page():
    return render_template("bot.html")


@bp.route("/enviar_mensaje", methods=["POST"])
def enviar_mensaje():
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        return _error("La petición debe ser JSON con el campo 'message'.")

    mensaje = datos.get("message")
    if not isinstance(mensaje, str) or not mensaje.strip():
        return _error("Escribe un mensaje.")
    if len(mensaje) > MAX_MESSAGE_LENGTH:
        return _error(f"El mensaje no puede superar {MAX_MESSAGE_LENGTH} caracteres.")

    return jsonify({"response": obtener_respuesta(mensaje)})
