import os

from flask import Flask, Response, jsonify, redirect, render_template, request, url_for
from unidecode import unidecode
from werkzeug.utils import secure_filename

from db import db, db_init
from models import Img

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")

# Campos de texto obligatorios del formulario de subida
CAMPOS_PROYECTO = ("project_name", "motor", "power", "acceleration", "top_speed")
LARGO_MAXIMO_CAMPO = 100  # coincide con String(100) en models.py


def create_app(config=None):
    """Crea y configura la aplicacion Flask."""
    app = Flask(__name__, instance_path=INSTANCE_DIR)

    # SQLite no crea carpetas: si instance/ no existe falla con
    # "unable to open database file", asi que la creamos antes.
    os.makedirs(app.instance_path, exist_ok=True)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(app.instance_path, "img.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB por subida

    if config:
        app.config.update(config)

    db_init(app)
    registrar_rutas(app)
    return app


RESPUESTAS = {
    'hola': '¡Hola! ¿En qué puedo ayudarte? Si tienes alguna duda escribe "comandos" y se te dará una opción para que revises en tu carro. Recuerda que solo te damos una posible solución, la opción ideal sería llevarlo al mecánico.',
    'problema con el motor': '¿Puedes describir el problema con el motor? Dalo en solo 1 palabra, ejemplo: aceleracion',
    'aceleracion': '¿Has revisado el sistema de combustible o las bujías? Otra opción podría ser revisar el sistema de escape. ¿Quieres intentar eso?',
    'velocidad maxima': '¿El motor suena normal cuando alcanzas alta velocidad?',
    'ruido raro': '¿El ruido se escucha al arrancar o cuando el auto está en movimiento? Si es un sonido metálico apágalo inmediatamente y llama una grúa, se te puede motorear.',
    'frenos': '¿Los frenos responden de manera adecuada o hay alguna dificultad para frenar? Si tienes dificultad para frenar prueba a revisar las pastillas o el pistón de freno.',
    'aceite': '¿Has revisado el nivel de aceite y la calidad del mismo? Solo destapa el capó y en la parte superior del motor puedes sacar la varilla que permite ver el estado del aceite. OJO: no lo hagas con el motor caliente.',
    'agua en el radiador': '¿Has comprobado si hay alguna fuga de agua o si el radiador está sucio? Recuerda que esto es vital para su funcionamiento.',
    'bateria': '¿La batería se descarga rápidamente o el auto no arranca en la mañana? Prueba a ver si tiene fugas de corriente.',
    'aire acondicionado': '¿El aire acondicionado está funcionando correctamente o emite ruidos extraños? Si es así prueba a revisar el filtro de aire o sus conexiones.',
    'luces': '¿Revisaste el estado de la batería o las conexiones? Las conexiones deja que las revise un mecánico especializado.',
    'parabrisas': '¿Ya hiciste un cambio en las plumillas? Prueba con eso.',
    'ruedas': '¿Las ruedas están alineadas correctamente? ¿Has revisado la presión de los neumáticos?',
    'cambio de marcha': '¿El cambio de marchas está funcionando sin problemas o hay dificultades al cambiar?',
    'suspension': '¿Has notado ruidos extraños o una sensación inestable al conducir? Manda a revisar tus suspensiones o las ballestas.',
    'escapes': '¿El sistema de escape emite ruidos o humo inusual? ¿Hay alguna fuga? Dame el color de tu humo, ejemplo: humo gris, humo azul, humo negro, humo blanco, humo naranja o rojo.',
    'humo blanco': (
        'Si el humo blanco aparece solo al inicio y luego desaparece, es probable que solo sea vapor de agua. '
        'Sin embargo, si persiste, podría ser una fuga en la junta de culata, lo que permitiría que el refrigerante se mezcle con el aceite o el combustible. '
        'Esto podría dañar el motor y generar sobrecalentamiento. Otra posibilidad es que la culata esté agrietada, permitiendo la filtración del refrigerante. '
        '¿Quieres revisar esto más a fondo?'
    ),
    'humo azul': (
        'El humo azul generalmente indica que el motor está quemando aceite. Esto puede suceder debido al desgaste de los anillos de pistón o las válvulas, '
        'lo que permite que el aceite entre en los cilindros y se queme. También puede ser causado por guías de válvulas defectuosas. '
        'Si está quemando aceite, es recomendable revisar estas piezas. ¿Quieres que revisemos esto?'
    ),
    'humo negro': (
        'El humo negro suele indicar que hay una mezcla rica de combustible, es decir, más combustible del necesario. '
        'Esto puede ser causado por inyectores defectuosos, un sensor de oxígeno dañado o un regulador de presión defectuoso. '
        'También puede ser por un filtro de aire obstruido. Si notas que el motor está funcionando de manera ineficiente o que hay un aumento en el consumo de combustible, '
        'puede ser por este problema. ¿Deseas que investiguemos más sobre esto?'
    ),
    'humo gris': (
        'El humo gris generalmente significa que el motor está quemando aceite. Esto puede ocurrir por desgaste en los anillos de pistón o en las válvulas. '
        'Si tu vehículo tiene un turbo, también podría estar relacionado con un problema en este componente. '
        'Si el humo gris es constante, es importante revisar el sistema de lubricación del motor. ¿Te gustaría revisar estos componentes?'
    ),
    'humo naranja o rojo': (
        'Aunque es raro, el humo naranja o rojo puede ser una señal de problemas en el sistema de escape o componentes dañados. '
        'Puede que haya algo extraño en el sistema de escape o un componente que necesita revisión. '
        '¿Quieres que revisemos el sistema de escape en detalle?'
    ),
}

# La lista de comandos se arma sola a partir de las respuestas, asi nunca se desincroniza
RESPUESTAS['comandos'] = 'Estos son los comandos disponibles:\n' + '\n'.join(
    f'- {comando}' for comando in RESPUESTAS
)

RESPUESTA_POR_DEFECTO = 'Lo siento, no entendí esa pregunta. Escribe "comandos" para ver las opciones disponibles.'


def normalizar(texto):
    """Pasa a minusculas, quita acentos, signos sueltos y espacios repetidos."""
    texto = unidecode(texto).lower()
    texto = ''.join(c if c.isalnum() or c.isspace() else ' ' for c in texto)
    return ' '.join(texto.split())


def obtener_respuesta(mensaje_usuario):
    """Devuelve la respuesta del asistente para el mensaje recibido."""
    if not isinstance(mensaje_usuario, str):
        return RESPUESTA_POR_DEFECTO
    return RESPUESTAS.get(normalizar(mensaje_usuario), RESPUESTA_POR_DEFECTO)


def registrar_rutas(app):
    @app.route("/")
    def home():
        latest_projects = Img.query.order_by(Img.id.desc()).limit(3).all()
        return render_template("index.html", latest_projects=latest_projects)

    @app.route("/bot")
    def bot_page():
        return render_template("bot.html")

    @app.route("/enviar_mensaje", methods=["POST"])
    def enviar_mensaje():
        datos = request.get_json(silent=True)
        if not isinstance(datos, dict):
            return jsonify({"error": "Se esperaba un JSON con el campo 'message'."}), 400

        mensaje = datos.get("message")
        if not isinstance(mensaje, str) or not mensaje.strip():
            return jsonify({"error": "El campo 'message' es obligatorio."}), 400

        return jsonify({"response": obtener_respuesta(mensaje)})

    @app.route("/mythcar")
    def mythcar():
        return render_template("mythcar.html")

    @app.route("/politica")
    def politica_privacidad():
        return render_template("politica_privacidad.html")

    @app.route("/terminos")
    def terminos_condiciones():
        return render_template("terminos_condiciones.html")

    @app.route("/proyectos")
    def proyectos():
        images = Img.query.order_by(Img.id.desc()).all()
        return render_template("proyectos.html", images=images)

    @app.route("/upload_page")
    def upload_page():
        return render_template("upload.html")

    @app.route("/upload", methods=["POST"])
    def upload():
        pic = request.files.get("pic")
        if pic is None or not pic.filename:
            return "No se subió ninguna imagen.", 400

        filename = secure_filename(pic.filename)
        mimetype = pic.mimetype or ""
        if not filename or not mimetype.startswith("image/"):
            return "El archivo debe ser una imagen.", 400

        datos = {}
        for campo in CAMPOS_PROYECTO:
            valor = (request.form.get(campo) or "").strip()
            if not valor:
                return f"Falta el campo '{campo}'.", 400
            if len(valor) > LARGO_MAXIMO_CAMPO:
                return f"El campo '{campo}' no puede superar {LARGO_MAXIMO_CAMPO} caracteres.", 400
            datos[campo] = valor

        contenido = pic.read()
        if not contenido:
            return "La imagen está vacía.", 400

        img = Img(img=contenido, name=filename[:120], mimetype=mimetype[:50], **datos)
        db.session.add(img)
        db.session.commit()
        return redirect(url_for("proyectos"))

    @app.route("/img/<int:id>")
    def get_img(id):
        img = db.session.get(Img, id)
        if img is None:
            return "Imagen no encontrada.", 404
        return Response(img.img, mimetype=img.mimetype)

    @app.errorhandler(413)
    def archivo_muy_grande(_error):
        return "La imagen supera el límite de 16 MB.", 413


app = create_app()

if __name__ == "__main__":
    # El modo debug solo se activa si se pide expresamente: FLASK_DEBUG=1
    debug = os.environ.get("FLASK_DEBUG", "0").lower() in ("1", "true", "yes")
    app.run(debug=debug)
