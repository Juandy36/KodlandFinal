# KodlandFinal
Pagina dedicada a lo automotriz
## Una página web dedicada a los carros míticos, con un catálogo detallado que incluye configuraciones, especificaciones, logros históricos. Permitirá a los usuarios subir sus proyectos personales, explorarlos en una galería y participar en un foro enfocado en temas de restauración y exhibición. Opcionalmente, incluirá un asistente virtual para resolver dudas mecánicas. Contará con una base de datos robusta para gestionar proyectos, utilizando librerías básicas de Python como:

## -os: Manejar rutas de archivos y directorios.
## -werkzeug.utils (secure_filename): Asegurar nombres seguros para archivos subidos.
## -Response: Enviar respuestas personalizadas desde rutas Flask.
## -redirect: Redirigir al usuario a otra página o ruta.
## -Flask: Crear la aplicación web y manejar rutas.
## -Flask-SQLAlchemy: Conectar y manejar la base de datos SQLite.

---

## Funciones

- **Catálogo** de carros míticos (`/mythcar`).
- **Subida de proyectos** con imagen (`/upload_page`). Solo se aceptan imágenes PNG, JPG, GIF o WEBP de hasta 5 MB. El tipo se comprueba por el contenido del archivo, no por la extensión.
- **Galería** de proyectos (`/proyectos`) y últimos proyectos en la portada (`/`).
- **Asistente virtual** (`/bot`), que responde por `POST /enviar_mensaje` con JSON `{"message": "..."}`. Escribe `comandos` para ver las opciones.

## Requisitos

- Python 3.11 o superior.

## Instalación

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Linux / macOS (bash):**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuración

La configuración se lee de variables de entorno. Para desarrollo, crea un archivo `.env` en la raíz del proyecto. `flask run` lo carga automáticamente gracias a `python-dotenv`. **Nunca lo subas al repositorio**: está en `.gitignore`.

```dotenv
APP_ENV=development
FLASK_DEBUG=1
```

| Variable        | Por defecto                 | Descripción |
|-----------------|-----------------------------|-------------|
| `APP_ENV`       | `production`                | `development`, `production` o `testing`. |
| `SECRET_KEY`    | aleatoria en desarrollo     | **Obligatoria en producción**: la app no arranca sin ella. Genera una con `python -c "import secrets; print(secrets.token_hex(32))"`. |
| `DATABASE_URL`  | `sqlite:///instance/img.db` | URL de SQLAlchemy de la base de datos. |
| `FLASK_DEBUG`   | `0`                         | `1` activa el modo debug. Solo funciona en desarrollo; en producción siempre está desactivado. |
| `MAX_UPLOAD_MB` | `5`                         | Tamaño máximo de subida, en MB. |
| `SESSION_COOKIE_SECURE` | `1` en producción   | Envía la cookie de sesión solo por HTTPS. |

Si no se define `APP_ENV`, la app arranca en modo **producción** y exige `SECRET_KEY`.

## Ejecución

**Desarrollo:**

```bash
flask --app wsgi run
```

Abre <http://127.0.0.1:5000>.

**Producción (Linux):**

```bash
export APP_ENV=production
export SECRET_KEY="tu-clave-secreta"
gunicorn -w 2 -b 0.0.0.0:8000 wsgi:app
```

La base de datos SQLite se crea sola en `instance/img.db` la primera vez.

## Pruebas

```bash
pip install -r requirements-dev.txt
pytest
```

Las pruebas usan una base de datos SQLite en memoria y no tocan `instance/`.

## Estructura del proyecto

```
config.py              Configuración por entorno (variables de entorno)
wsgi.py                Punto de entrada (flask / gunicorn)
app/
  __init__.py          create_app(): app factory
  extensions.py        Instancia de SQLAlchemy
  models.py            Modelo Img (tabla "img")
  errors.py            Manejadores 404 / 413 / 500 (HTML o JSON)
  main/                Inicio, catálogo, política y términos
  projects/            Galería, subida de proyectos y servicio de imágenes
    forms.py           Validación del formulario y de la imagen
  bot/                 Asistente virtual
    responses.py       Respuestas predefinidas
templates/             Plantillas Jinja2
static/                CSS e imágenes
tests/                 Pruebas con pytest
```
