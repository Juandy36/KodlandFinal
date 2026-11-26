"""Validacion del formulario de subida de proyectos.

No se confia en el mimetype que envia el navegador: el tipo real se obtiene
de los primeros bytes del archivo (firma o "magic bytes").
"""
import os

from werkzeug.utils import secure_filename

from ..models import FILENAME_MAX, TEXT_FIELD_MAX

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
ALLOWED_MIMETYPES = {"image/png", "image/jpeg", "image/gif", "image/webp"}

# Campos de texto del formulario y su etiqueta para los mensajes de error.
TEXT_FIELDS = {
    "project_name": "Nombre del proyecto",
    "motor": "Motor",
    "power": "Potencia",
    "acceleration": "0-100 Km/h",
    "top_speed": "Velocidad máxima",
}


def detect_image_mimetype(data):
    """Devuelve el mimetype segun la firma del contenido, o None si no es valido."""
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if data.startswith((b"GIF87a", b"GIF89a")):
        return "image/gif"
    if len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    return None


def _extension(filename):
    return os.path.splitext(filename)[1].lower().lstrip(".")


def validate_project_form(form, files, max_bytes=None):
    """Valida el formulario.

    Devuelve ``(datos, errores)``. Si ``errores`` esta vacio, ``datos`` trae
    los campos listos para crear un ``Img``.
    """
    errors = []
    data = {}

    for field, label in TEXT_FIELDS.items():
        value = (form.get(field) or "").strip()
        if not value:
            errors.append(f"El campo «{label}» es obligatorio.")
        elif len(value) > TEXT_FIELD_MAX:
            errors.append(f"El campo «{label}» no puede superar {TEXT_FIELD_MAX} caracteres.")
        data[field] = value

    pic = files.get("pic")
    if pic is None or not pic.filename:
        errors.append("Selecciona una imagen.")
        return data, errors

    ext = _extension(pic.filename)
    if ext not in ALLOWED_EXTENSIONS:
        permitidas = ", ".join(sorted(ALLOWED_EXTENSIONS))
        errors.append(f"Formato no permitido. Usa una imagen: {permitidas}.")
        return data, errors

    content = pic.read()
    if not content:
        errors.append("La imagen está vacía.")
        return data, errors
    if max_bytes is not None and len(content) > max_bytes:
        errors.append(f"La imagen supera el tamaño máximo de {max_bytes // (1024 * 1024)} MB.")
        return data, errors

    mimetype = detect_image_mimetype(content)
    if mimetype is None:
        errors.append("El archivo no es una imagen válida.")
        return data, errors

    name = secure_filename(pic.filename)
    if _extension(name) != ext:
        # secure_filename puede vaciar nombres solo con caracteres no ASCII.
        name = f"imagen.{ext}"
    if len(name) > FILENAME_MAX:
        name = name[: FILENAME_MAX - len(ext) - 1] + "." + ext

    data.update(img=content, name=name, mimetype=mimetype)
    return data, errors
