from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template

app = Flask(__name__)

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
    return render_template("proyectos.html")

# Configuración para arrancar la aplicación
if __name__ == "__main__":
    app.run(debug=True)
