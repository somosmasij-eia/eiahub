from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id         = db.Column(db.Integer, primary_key=True)
    email      = db.Column(db.String(120), unique=True, nullable=False)
    nombre     = db.Column(db.String(200), nullable=False)
    verificado = db.Column(db.Boolean, default=False, nullable=False)

    # Token para verificación de cuenta y magic link
    token            = db.Column(db.String(64), nullable=True, unique=True)
    token_expiracion = db.Column(db.DateTime, nullable=True)

    registros = db.relationship("RegistroRuta", backref="usuario", lazy=True)


class RegistroRuta(db.Model):
    __tablename__ = "registros_ruta"
    id             = db.Column(db.Integer, primary_key=True)
    user_id        = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    ruta           = db.Column(db.String(200), nullable=False)
    horario        = db.Column(db.String(50), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
