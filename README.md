# KodlandFinal - Leyendas Sobre Ruedas

Página web dedicada a los carros míticos, con un catálogo detallado que incluye configuraciones, especificaciones y logros históricos. Los usuarios pueden subir sus proyectos personales y verlos en una galería. Además incluye un asistente virtual para orientar sobre dudas mecánicas básicas.

## Requisitos

- Python 3.9 o superior

## Instalación

```bash
python -m venv .venv
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

> `requeriments.txt` se mantiene por compatibilidad y simplemente incluye `requirements.txt`.

## Ejecución

```bash
python app.py
```

La app queda en http://127.0.0.1:5000. La base de datos SQLite se crea sola en `instance/img.db` la primera vez.

Para activar el modo debug durante el desarrollo, define la variable `FLASK_DEBUG=1` antes de arrancar.

## Pruebas

```bash
python -m unittest discover -s tests -v
```

## Rutas

| Ruta | Descripción |
|------|-------------|
| `/` | Página principal con los últimos proyectos |
| `/mythcar` | Catálogo de carros míticos |
| `/proyectos` | Galería de proyectos subidos |
| `/upload_page` | Formulario para subir un proyecto |
| `/bot` | Asistente virtual (escribe `comandos` para ver las opciones) |
| `/img/<id>` | Imagen de un proyecto |
| `/politica`, `/terminos` | Política de privacidad y términos |

## Librerías usadas

- **Flask**: crear la aplicación web y manejar rutas.
- **Flask-SQLAlchemy**: conectar y manejar la base de datos SQLite.
- **werkzeug.utils (secure_filename)**: asegurar nombres seguros para archivos subidos.
- **Unidecode**: normalizar acentos en los mensajes del asistente.
- **os**: manejar rutas de archivos y directorios.
