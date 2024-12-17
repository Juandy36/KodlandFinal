from flask import Flask, render_template, request, Response, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from db import db, db_init
from unidecode import unidecode
from models import Img
import os

# Crear la aplicación Flask
app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(BASE_DIR, "instance", "img.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Inicializar la base de datos
db_init(app)

# Función para simular respuestas del bot
def obtener_respuesta(usuario_message):
    respuestas = {
    'hola': '¡Hola! ¿En qué puedo ayudarte?, si tienes alguna duda escribe comandos y se te dara una opcion para que revises en tu carro, recuerda que solo te damos una posible solucion, la opcion ideal seria llevar al mecanico',
    'problema con el motor': '¿Puedes describir el problema con el motor? dalo en solo 1 palabra ejemplo: aceleracion',
    'aceleracion': ('¿Has revisado el sistema de combustible o las bujías?', 'Otra opción podría ser revisar el sistema de escape. ¿Quieres intentar eso?'),
    'velocidad maxima': '¿El motor suena normal cuando alcanzas alta velocidad?',
    'ruido raro': '¿El ruido se escucha al arrancar o cuando el auto está en movimiento? si es un sonido metalico apagalo inmediatamente y llama una grua, se te puede motorear',
    'frenos': '¿Los frenos responden de manera adecuada o hay alguna dificultad para frenarse? si tienes dificultad para frenar prueba a revisar las pastillas o el piston de freno',
    'aceite': '¿Has revisado el nivel de aceite y la calidad del mismo? solo destapa el motor y en la parte superior del motor puedes sacar la tirilla que permite ver el estado del aceite OJO no lo hagas con el motor caliente',
    'agua en el radiador': '¿Has comprobado si hay alguna fuga de agua o si el radiador está sucio? recuerda que esto es vital para su funcionamiento',
    'bateria': '¿La batería se descarga rápidamente o el auto no arranca en la mañana? prueba a ver si tiene fugas de corriente',
    'aire acondicionado': '¿El aire acondicionado está funcionando correctamente o emite ruidos extraños? si es asi prueba a revisar el filtro de aire o sus conexiones',
    'luces': '¿Revisaste el estado de la bateria o las conexiones? las conexiones deja que las revise un mecanico especializado',
    'parabrisas': '¿Ya hiciste un cambio en las plumillas? Prueba con eso',
    'ruedas': '¿Las ruedas están alineadas correctamente? ¿Has revisado la presión de los neumáticos?',
    'cambio de marcha': '¿El cambio de marchas está funcionando sin problemas o hay dificultades al cambiar?',
    'suspension': '¿Has notado ruidos extraños o una sensación inestable al conducir? manda a revisar tus suspensiones o las ballestas',
    'escapes': '¿El sistema de escape emite ruidos o humo inusual? ¿Hay alguna fuga? dame el color de tu humo ejemplo humo gris, humo azul, humo negro, humo blanco, humo naranja o rojo',
        'humo blanco': '''Si el humo blanco aparece solo al inicio y luego desaparece, es probable que solo sea vapor de agua. 
                     Sin embargo, si persiste, podría ser una fuga en la junta de culata, lo que permitiría que el refrigerante se mezcle con el aceite o el combustible. 
                     Esto podría dañar el motor y generar sobrecalentamiento. Otra posibilidad es que la culata esté agrietada, permitiendo la filtración del refrigerante. 
                     ¿Quieres revisar esto más a fondo?''',
    'humo azul': '''El humo azul generalmente indica que el motor está quemando aceite. Esto puede suceder debido al desgaste de los anillos de pistón o las válvulas, 
                   lo que permite que el aceite entre en los cilindros y se queme. También puede ser causado por guías de válvulas defectuosas. 
                   Si está quemando aceite, es recomendable revisar estas piezas. ¿Quieres que revisemos esto?''',
    'humo negro': '''El humo negro suele indicar que hay una mezcla rica de combustible, es decir, más combustible del necesario. 
                    Esto puede ser causado por inyectores defectuosos, un sensor de oxígeno dañado o un regulador de presión defectuoso. 
                    También puede ser por un filtro de aire obstruido. Si notas que el motor está funcionando de manera ineficiente o que hay un aumento en el consumo de combustible, 
                    puede ser por este problema. ¿Deseas que investiguemos más sobre esto?''',
    'humo gris': '''El humo gris generalmente significa que el motor está quemando aceite. Esto puede ocurrir por desgaste en los anillos de pistón o en las válvulas. 
                   Si tu vehículo tiene un turbo, también podría estar relacionado con un problema en este componente. 
                   Si el humo gris es constante, es importante revisar el sistema de lubricación del motor. ¿Te gustaría revisar estos componentes?''',
    'humo naranja o rojo': '''Aunque es raro, el humo naranja o rojo puede ser una señal de problemas en el sistema de escape o componentes dañados. 
                              Puede que haya algo extraño en el sistema de escape o un componente que necesita revisión. 
                              ¿Quieres que revisemos el sistema de escape en detalle?''',
    'comandos': 'Estos son los comandos disponibles: \n- hola\n- problema con el motor\n- aceleracion\n- velocidad maxima\n- ruido raro\n- frenos\n- aceite\n- agua en el radiador\n- bateria\n- aire acondicionado\n- luces\n- parabrisas\n- ruedas\n- cambio de marcha\n- suspension\n- escapes',

    }
    # Si el mensaje está en las respuestas predefinidas, devuelve la respuesta
    return respuestas.get(usuario_message.lower(), 'Lo siento, no entendí esa pregunta.')

# Ruta para la página principal
@app.route("/")
def home():
    latest_projects = Img.query.order_by(Img.id.desc()).limit(3).all()
    return render_template("index.html", latest_projects=latest_projects)

# Ruta para la página del bot
@app.route('/bot')
def bot_page():
    return render_template('bot.html')

# Ruta para recibir mensajes del usuario en el bot
@app.route('/enviar_mensaje', methods=['POST'])
def enviar_mensaje():
    user_message = request.json.get('message')  # Recibimos el mensaje en formato JSON
    bot_response = obtener_respuesta(user_message)  # Obtenemos la respuesta del bot
    return jsonify({'response': bot_response})  # Respondemos al frontend con la respuesta del bot

# Resto de tus rutas...
@app.route("/mythcar")
def mythcar():
    return render_template("mythcar.html")

@app.route('/politica')
def politica_privacidad():
    return render_template('politica_privacidad.html')

@app.route('/terminos')
def terminos_condiciones():
    return render_template('terminos_condiciones.html')

@app.route("/proyectos")
def proyectos():
    images = Img.query.all()
    return render_template("proyectos.html", images=images)

@app.route("/upload_page")
def upload_page():
    return render_template("upload.html")

@app.route('/upload', methods=['POST'])
def upload():
    pic = request.files['pic']
    project_name = request.form['project_name']
    motor = request.form['motor']
    power = request.form['power']
    acceleration = request.form['acceleration']
    top_speed = request.form['top_speed']

    if not pic:
        return 'No pic uploaded!', 400

    filename = secure_filename(pic.filename)
    mimetype = pic.mimetype
    if not filename or not mimetype:
        return 'Bad upload!', 400

    img = Img(
        img=pic.read(),
        name=filename,
        mimetype=mimetype,
        project_name=project_name,
        motor=motor,
        power=power,
        acceleration=acceleration,
        top_speed=top_speed
    )

    db.session.add(img)
    db.session.commit()
    return redirect(url_for('proyectos'))

@app.route('/<int:id>')
def get_img(id):
    img = Img.query.filter_by(id=id).first()
    if not img:
        return 'Img Not Found!', 404
    return Response(img.img, mimetype=img.mimetype)

if __name__ == "__main__":
    app.run(debug=True)