import os
 
class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")
 
    _db_url = os.environ.get("DATABASE_URL", "sqlite:///database.db")
    if _db_url.startswith("postgres://"):
        _db_url = _db_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = _db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
 
    # Gmail SMTP
    MAIL_SERVER   = "smtp.gmail.com"
    MAIL_PORT     = 465
    MAIL_USE_TLS  = False
    MAIL_USE_SSL  = True
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = ("EIA Striges", os.environ.get("MAIL_USERNAME", ""))
 
    ALLOWED_DOMAIN = "@eia.edu.co"