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

mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    db.init_app(app)
    mail.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "main.index"

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=False, host="0.0.0.0", port=5000)