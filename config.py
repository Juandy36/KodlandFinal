"""Configuracion de la aplicacion leida desde variables de entorno.

Los valores se leen al instanciar la clase (no al importar el modulo), asi
``create_app`` siempre ve el entorno actual y las pruebas pueden modificarlo.
"""
import os
import secrets

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")


def _env_flag(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name, default):
    value = os.environ.get(name)
    if value is None or value.strip() == "":
        return default
    try:
        number = int(value)
    except ValueError as exc:
        raise RuntimeError(f"La variable {name} debe ser un numero entero.") from exc
    if number <= 0:
        raise RuntimeError(f"La variable {name} debe ser mayor que cero.")
    return number


class Config:
    """Valores comunes a todos los entornos."""

    DEBUG = False
    TESTING = False

    def __init__(self):
        self.SECRET_KEY = os.environ.get("SECRET_KEY") or None
        self.SQLALCHEMY_DATABASE_URI = os.environ.get(
            "DATABASE_URL",
            "sqlite:///" + os.path.join(INSTANCE_DIR, "img.db"),
        )
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False
        # Limite total de la peticion. Flask responde 413 si se supera.
        self.MAX_CONTENT_LENGTH = _env_int("MAX_UPLOAD_MB", 5) * 1024 * 1024
        self.SESSION_COOKIE_HTTPONLY = True
        self.SESSION_COOKIE_SAMESITE = "Lax"


class DevelopmentConfig(Config):
    def __init__(self):
        super().__init__()
        # El debug solo se activa si se pide de forma explicita.
        self.DEBUG = _env_flag("FLASK_DEBUG", False)
        if not self.SECRET_KEY:
            # Clave aleatoria por proceso: suficiente para desarrollo local.
            self.SECRET_KEY = secrets.token_hex(32)


class ProductionConfig(Config):
    def __init__(self):
        super().__init__()
        self.DEBUG = False
        self.SESSION_COOKIE_SECURE = _env_flag("SESSION_COOKIE_SECURE", True)
        if not self.SECRET_KEY:
            raise RuntimeError(
                "SECRET_KEY es obligatoria en produccion. "
                "Definela como variable de entorno (ver .env.example)."
            )


class TestingConfig(Config):
    TESTING = True

    def __init__(self):
        super().__init__()
        self.SECRET_KEY = "clave-solo-para-pruebas"
        self.SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


CONFIGS = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}


def get_config(name=None):
    """Devuelve una instancia de configuracion.

    Si no se indica nombre se usa ``APP_ENV`` y, por seguridad, ``production``
    cuando tampoco existe.
    """
    name = (name or os.environ.get("APP_ENV") or "production").strip().lower()
    try:
        config_class = CONFIGS[name]
    except KeyError as exc:
        opciones = ", ".join(sorted(CONFIGS))
        raise RuntimeError(f"APP_ENV desconocido: {name!r}. Usa uno de: {opciones}.") from exc
    return config_class()
