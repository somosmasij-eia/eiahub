import random
import threading # <--- IMPORTANTE
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

# --- NUEVA FUNCIÓN ASÍNCRONA ---
def _enviar_email_async(app, msg):
    """Envía el correo usando el contexto de la aplicación en un hilo aparte"""
    with app.app_context():
        try:
            # Obtenemos la extensión mail directamente del objeto app
            mail = app.extensions.get('mail')
            mail.send(msg)
            print(f"✅ Correo enviado en segundo plano.")
        except Exception as e:
            print(f"❌ Error enviando correo: {e}")

def _preparar_y_enviar_email(destinatario, asunto, cuerpo_html):
    """Crea el mensaje y lanza el hilo para no bloquear el servidor"""
    app = current_app._get_current_object() # Obtenemos la instancia real de la app
    msg = Message(asunto, recipients=[destinatario])
    msg.html = cuerpo_html
    
    # LANZAR EL HILO: El código sigue de largo sin esperar a Gmail
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
            flash("Este correo ya está registrado. Inicia sesión.", "info")
            return redirect(url_for("auth.login"))

        if not user:
            user = User(email=email, nombre=nombre)
            db.session.add(user)

        codigo = _generar_codigo()
        user.token = codigo
        user.token_expiracion = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRY_MINUTES)
        db.session.commit()

        # LLAMADA AL NUEVO SISTEMA VELOZ
        _preparar_y_enviar_email(
            email,
            "Tu código de verificación — EIA Hub",
            f"<h2>Hola {nombre},</h2><p>Tu código es: <strong>{codigo}</strong></p>"
        )

        session['verify_email'] = email
        flash("Código enviado. Revisa tu correo (puede tardar un momento).", "success")
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

        # ENVÍO VELOZ TAMBIÉN AQUÍ
        _preparar_y_enviar_email(
            email,
            "Tu código de acceso — EIA Hub",
            f"<h2>Hola {user.nombre},</h2><p>Tu código es: <strong>{codigo}</strong></p>"
        )

        session['verify_email'] = email
        flash("Código enviado. Revisa tu correo.", "success")
        return redirect(url_for("auth.verify"))

    return render_template("login.html")

# (El resto de tus rutas verify y logout se quedan igual...)
    return render_template("register.html")

#
def verify():
    # Recuperamos el correo temporalmente guardado
    email = session.get('verify_email')
    
    if not email:
        flash("Sesión expirada o inválida. Intenta de nuevo.", "error")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        codigo = request.form.get("codigo", "").strip()
        user = User.query.filter_by(email=email).first()

        # Validación del código
        if not user or user.token != codigo or user.token_expiracion < datetime.utcnow():
            flash("Código inválido o expirado. Revisa bien o pide uno nuevo.", "error")
            return render_template("verify.html", email=email)

        # Si el código es correcto, verificamos la cuenta y limpiamos el token
        user.verificado = True
        user.token = None
        user.token_expiracion = None
        db.session.commit()

        # Iniciamos sesión y borramos el email temporal
        login_user(user)
        session.pop('verify_email', None)
        
        flash("¡Acceso exitoso!", "success")
        return redirect(url_for("main.dashboard")) 

    return render_template("verify.html", email=email)

# ── Logout ────────────────────────────────────────────────────────────────────
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada.", "info")
    return redirect(url_for("main.index"))