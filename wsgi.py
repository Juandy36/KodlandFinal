"""Punto de entrada WSGI.

Desarrollo:  flask --app wsgi run
Produccion:  gunicorn wsgi:app
"""
from app import create_app

app = create_app()

if __name__ == "__main__":
    # El modo debug lo decide la configuracion (FLASK_DEBUG), nunca el codigo.
    app.run()
