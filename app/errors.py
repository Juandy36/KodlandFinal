from flask import current_app, jsonify, render_template, request
from werkzeug.exceptions import HTTPException, RequestEntityTooLarge

from .extensions import db

MENSAJES = {
    400: "La petición no es válida.",
    404: "La página que buscas no existe.",
    405: "Método no permitido.",
    413: "El archivo es demasiado grande.",
    500: "Ocurrió un error interno. Inténtalo de nuevo más tarde.",
}


def _wants_json():
    if request.is_json:
        return True
    # Ante un empate (p. ej. "*/*") gana HTML por estar primero.
    best = request.accept_mimetypes.best_match(["text/html", "application/json"])
    return best == "application/json"


def _error_response(code):
    mensaje = MENSAJES.get(code, "Ocurrió un error.")
    if _wants_json():
        # "response" permite que el chat del bot muestre el mensaje.
        return jsonify({"error": mensaje, "response": mensaje}), code
    return render_template("error.html", code=code, message=mensaje), code


def handle_http_exception(error):
    # Las redirecciones de enrutado (308, etc.) tambien son HTTPException.
    if error.code is None or error.code < 400:
        return error
    return _error_response(error.code)


def handle_too_large(error):
    if request.endpoint == "projects.upload" and not _wants_json():
        from .projects.routes import render_upload_form

        max_mb = (current_app.config.get("MAX_CONTENT_LENGTH") or 0) // (1024 * 1024)
        return render_upload_form(
            errors=[f"El archivo supera el tamaño máximo permitido ({max_mb} MB)."],
            status=413,
        )
    return _error_response(413)


def handle_server_error(error):
    db.session.rollback()
    return _error_response(500)


def register_error_handlers(app):
    app.register_error_handler(HTTPException, handle_http_exception)
    app.register_error_handler(RequestEntityTooLarge, handle_too_large)
    app.register_error_handler(500, handle_server_error)
