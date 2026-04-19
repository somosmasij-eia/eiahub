import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-super-segura")

    # --- Configuración de Base de Datos ---
    # Este fix es vital para que SQLAlchemy no falle con PostgreSQL en Render
    _db_url = os.environ.get("DATABASE_URL", "sqlite:///database.db")
    if _db_url.startswith("postgres://"):
        _db_url = _db_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = _db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Gmail SMTP (Versión Robusta para la Nube) ---
    MAIL_SERVER   = "smtp.gmail.com"
    MAIL_PORT     = 465           # <--- CAMBIO: Puerto SSL (más estable en Render)
    MAIL_USE_TLS  = False         # <--- CAMBIO: Desactivamos TLS
    MAIL_USE_SSL  = True          # <--- CAMBIO: Activamos SSL
    
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "").strip()
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "").replace(" ", "")  # Usa la "Contraseña de Aplicación"
    
    # Esto ayuda a que los correos no lleguen a Spam
    MAIL_DEFAULT_SENDER = ("EIA Hub", MAIL_USERNAME)

    # --- Dominio Institucional ---
    ALLOWED_DOMAIN = "@eia.edu.co"