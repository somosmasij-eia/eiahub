import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")

    # Fix para Render: SQLAlchemy no acepta "postgres://", solo "postgresql://"
    _db_url = os.environ.get("DATABASE_URL", "sqlite:///database.db")
    if _db_url.startswith("postgres://"):
        _db_url = _db_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = _db_url

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Gmail SMTP (envío de emails)
    MAIL_SERVER   = "smtp.gmail.com"
    MAIL_PORT     = 587
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")  # Contraseña de aplicación de Google

    ALLOWED_DOMAIN = "@eia.edu.co"