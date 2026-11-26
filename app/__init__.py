import os

from flask import Flask

from config import BASE_DIR, INSTANCE_DIR, get_config

from .extensions import db


def create_app(config_name=None):
    """App factory: crea y configura una instancia de la aplicacion."""
    app = Flask(
        __name__,
        # Las plantillas y los estaticos siguen en la raiz del proyecto.
        template_folder=os.path.join(BASE_DIR, "templates"),
        static_folder=os.path.join(BASE_DIR, "static"),
        instance_path=INSTANCE_DIR,
    )
    app.config.from_object(get_config(config_name))

    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)

    from .bot import bp as bot_bp
    from .main import bp as main_bp
    from .projects import bp as projects_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(bot_bp)
    app.register_blueprint(projects_bp)

    from .errors import register_error_handlers

    register_error_handlers(app)

    @app.after_request
    def security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        return response

    with app.app_context():
        from . import models  # noqa: F401  (registra los modelos)

        db.create_all()

    return app
