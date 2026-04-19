import random
import threading
from datetime import datetime, timedelta
from flask import Blueprint, redirect, request, url_for, flash, render_template, current_app, session
from flask_login import login_user, logout_user, login_required
from flask_mail import Message
from models import db, User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

ALLOWED_DOMAIN = "@eia.edu.co"
TOKEN_EXPIRY_MINUTES = 15

def _generar_codigo():
    return str(random.randint(100000, 999999))


def _enviar_email_async(app, msg):
    with app.app_context():
        try:
            mail = app.extensions.get('mail')
            mail.send(msg)
<<<<<<< Updated upstream
            print(f"✅ Correo enviado a {msg.recipients}")
        except Exception as e:
            print(f"❌ Error enviando correo: {type(e).__name__}: {e}")
=======
            app.logger.info("Correo enviado con éxito a %s", msg.recipients)
        except Exception as e:
            app.logger.error("Error enviando correo: %s", e, exc_info=True)
>>>>>>> Stashed changes

def _preparar_y_enviar_email(destinatario, asunto, cuerpo_html):
    app = current_app._get_current_object()
    msg = Message(asunto, recipients=[destinatario])
    msg.html = cuerpo_html
    threading.Thread(target=_enviar_email_async, args=(app, msg)).start()

# ── Registro ──────────────────────────────────────────────────────────────────
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email  = request.form.get("email", "").strip().lower()
        nombre = request.form.get("nombre", "").strip()

        if not email.endswith(ALLOWED_DOMAIN):
            flash("Solo correos @eia.edu.co pueden registrarse.", "error")
            return render_template("register.html")

        user = User.query.filter_by(email=email).first()
        if user and user.verificado:
            flash("Este correo ya está registrado.", "info")
            return redirect(url_for("auth.login"))

        if not user:
            user = User(email=email, nombre=nombre)
            db.session.add(user)

        codigo = _generar_codigo()
        user.token = codigo
        user.token_expiracion = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRY_MINUTES)
        db.session.commit()

        _preparar_y_enviar_email(
            email,
            "Tu código de verificación — EIA Hub",
            f"<h2>Hola {nombre},</h2><p>Tu código es: <strong>{codigo}</strong></p>"
        )

        session['verify_email'] = email
        flash("Código enviado. Revisa tu correo.", "success")
        # --- AQUÍ ESTABA EL ERROR: ESTA RUTA DEBE EXISTIR ABAJO ---
        return redirect(url_for("auth.verify"))

    return render_template("register.html")

# ── Login ─────────────────────────────────────────────────────────────────────
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        user = User.query.filter_by(email=email).first()

        if not user or not user.verificado:
            flash("Correo no registrado o no verificado.", "error")
            return render_template("login.html")

        codigo = _generar_codigo()
        user.token = codigo
        user.token_expiracion = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRY_MINUTES)
        db.session.commit()

        _preparar_y_enviar_email(
            email,
            "Tu código de acceso — EIA Hub",
            f"<h2>Hola {user.nombre},</h2><p>Tu código es: <strong>{codigo}</strong></p>"
        )

        session['verify_email'] = email
        return redirect(url_for("auth.verify"))

    return render_template("login.html")

# ── Verificación (ESTO ES LO QUE FALTABA) ──────────────────────────────────────
@auth_bp.route("/verify", methods=["GET", "POST"])
def verify():
    email = session.get('verify_email')
    if not email:
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        codigo = request.form.get("codigo", "").strip()
        user = User.query.filter_by(email=email).first()

        if not user or user.token != codigo or user.token_expiracion < datetime.utcnow():
            flash("Código inválido o expirado.", "error")
            return render_template("verify.html", email=email)

        user.verificado = True
        user.token = None
        user.token_expiracion = None
        db.session.commit()

        login_user(user)
        session.pop('verify_email', None)
        return redirect(url_for("main.dashboard")) 

    return render_template("verify.html", email=email)

# ── Logout ────────────────────────────────────────────────────────────────────
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))
