from .extensions import db

# Longitud maxima de los campos de texto del formulario de proyectos.
TEXT_FIELD_MAX = 100
FILENAME_MAX = 120


class Img(db.Model):
    """Proyecto subido por un usuario, con su imagen guardada en la base."""

    # Se fija el nombre para seguir usando la tabla de instance/img.db.
    __tablename__ = "img"

    id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.LargeBinary, nullable=False)
    name = db.Column(db.String(FILENAME_MAX), nullable=False)
    mimetype = db.Column(db.String(50), nullable=False)
    project_name = db.Column(db.String(TEXT_FIELD_MAX), nullable=False)
    motor = db.Column(db.String(TEXT_FIELD_MAX), nullable=False)
    power = db.Column(db.String(TEXT_FIELD_MAX), nullable=False)
    acceleration = db.Column(db.String(TEXT_FIELD_MAX), nullable=False)
    top_speed = db.Column(db.String(TEXT_FIELD_MAX), nullable=False)

    def __repr__(self):
        return f"<Img {self.id} {self.project_name!r}>"
