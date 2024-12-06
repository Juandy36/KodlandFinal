from flask import Flask, render_template, request, Response, redirect, url_for
from werkzeug.utils import secure_filename
from db import db, db_init
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

# Ruta para la página principal
@app.route("/")
def home():
    return render_template("index.html")

# Ruta para la página de 'mitos de autos'
@app.route("/mythcar")
def mythcar():
    return render_template("mythcar.html")

# Ruta para la página de 'proyectos'
@app.route("/proyectos")
def proyectos():
    images = Img.query.all()  # Obtén todas las imágenes de la base de datos
    return render_template("proyectos.html", images=images)

# Ruta para cargar un proyecto (subir imagen + formulario de datos)
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

    # Crear un objeto Img con la información recibida y la imagen
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

    # Agregar el objeto a la base de datos
    db.session.add(img)
    db.session.commit()

    # Redirigir a la página de proyectos
    return redirect(url_for('proyectos'))

# Ruta para la página de subir proyecto (formulario)
@app.route("/upload_page")
def upload_page():
    return render_template("upload.html")

# Ruta para obtener una imagen específica
@app.route('/<int:id>')
def get_img(id):
    img = Img.query.filter_by(id=id).first()
    if not img:
        return 'Img Not Found!', 404

    return Response(img.img, mimetype=img.mimetype)

# Configuración para arrancar la aplicación
if __name__ == "__main__":
    app.run(debug=True)
