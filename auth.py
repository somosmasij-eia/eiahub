import random
from datetime import datetime, timedelta
from flask import Blueprint, redirect, request, url_for, flash, render_template, current_app, session
from flask_login import login_user, logout_user, login_required
from flask_mail import Message
from models import db, User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

ALLOWED_DOMAIN = "@eia.edu.co"
TOKEN_EXPIRY_MINUTES = 15  # 15 min es estándar para códigos

def _generar_codigo():
    # Genera un código aleatorio de 6 dígitos
    return str(random.randint(100000, 999999))

def _enviar_email(destinatario, asunto, cuerpo_html):
    try:
        mail = current_app.extensions.get('mail')
        msg = Message(asunto, recipients=[destinatario])
        msg.html = cuerpo_html
        mail.send(msg)
        print(f"✅ ¡Correo enviado con éxito a {destinatario}!")
    except Exception as e:
        print(f"❌ Error interno enviando correo: {e}")

# ── Registro ──────────────────────────────────────────────────────────────────
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email  = request.form.get("email", "").strip().lower()
        nombre = request.form.get("nombre", "").strip()

        if not email.endswith(ALLOWED_DOMAIN):
            flash("Solo correos @eia.edu.co pueden registrarse.", "error")
            return render_template("register.html")

        if not nombre:
            flash("Por favor ingresa tu nombre.", "error")
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

        _enviar_email(
            email,
            "Tu código de verificación — EIA Hub",
            f"<h2>Hola {nombre},</h2><p>Tu código de seguridad es: <strong><span style='font-size:24px; color:#003087;'>{codigo}</span></strong></p><p>Este código expira en {TOKEN_EXPIRY_MINUTES} minutos. No lo compartas con nadie.</p>"
        )

        # Guardamos el email en sesión temporal para la pantalla de verificación
        session['verify_email'] = email
        flash("Te enviamos un código de 6 dígitos. Revisa tu correo.", "success")
        return redirect(url_for("auth.verify"))

    return render_template("register.html")

# ── Login ─────────────────────────────────────────────────────────────────────
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()

        if not email.endswith(ALLOWED_DOMAIN):
            flash("Solo correos @eia.edu.co pueden acceder.", "error")
            return render_template("login.html")

        user = User.query.filter_by(email=email).first()

        if not user or not user.verificado:
            flash("Correo no registrado o no verificado.", "error")
            return render_template("login.html")

        codigo = _generar_codigo()
        user.token = codigo
        user.token_expiracion = datetime.utcnow() + timedelta(minutes=TOKEN_EXPIRY_MINUTES)
        db.session.commit()

        _enviar_email(
            email,
            "Tu código de acceso — EIA Hub",
            f"<h2>Hola {user.nombre},</h2><p>Tu código de acceso es: <strong><span style='font-size:24px; color:#003087;'>{codigo}</span></strong></p><p>Este código expira en {TOKEN_EXPIRY_MINUTES} minutos.</p>"
        )

        session['verify_email'] = email
        flash("Te enviamos un código de 6 dígitos. Revisa tu correo.", "success")
        return redirect(url_for("auth.verify"))

    return render_template("login.html")

# ── Verificación de Código ────────────────────────────────────────────────────
@auth_bp.route("/verify", methods=["GET", "POST"])
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