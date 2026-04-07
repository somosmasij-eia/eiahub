import threading
from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from werkzeug.middleware.proxy_fix import ProxyFix
from config import Config
from models import db, User
from auth import auth_bp
from routes import main_bp

# 1. Declarar Mail de forma global para que el hilo pueda verlo
mail = Mail()

# 2. Función para que el correo se envíe sin que la página se quede cargando
def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            print(f"Error en envío de correo: {e}")

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Necesario para que Flask genere URLs con https:// en Render
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    db.init_app(app)
    
    # 3. Inicializar mail con la app
    mail.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login" # Asegúrate que coincida con tu Blueprint

    @login_manager.user_loader
    def load_user(user_id):
        # Usar session.get() es más moderno en SQLAlchemy 2.0
        return db.session.get(User, int(user_id))

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=False, host="0.0.0.0", port=5000)