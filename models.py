from db import db

class Img(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.LargeBinary, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    mimetype = db.Column(db.String(50), nullable=False)
    project_name = db.Column(db.String(100), nullable=False)
    motor = db.Column(db.String(100), nullable=False)
    power = db.Column(db.String(100), nullable=False)
    acceleration = db.Column(db.String(100), nullable=False)
    top_speed = db.Column(db.String(100), nullable=False)
