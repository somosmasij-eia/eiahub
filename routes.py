from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import db, RegistroRuta

main_bp = Blueprint("main", __name__)

RUTAS = [
    "San Antonio",
    "Sofasa - Aguacatala - Zuñiga",
    "Rionegro",
    "Mayorca",
    "Palacé",
    "Clínica Las Américas - Palacé",
    "Éxito de Robledo - Palacé",
]


@main_bp.route("/splash")
def splash():
    return render_template("splash.html")


@main_bp.route("/")
def index():
    return render_template("login.html")


@main_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


@main_bp.route("/conoce")
@login_required
def conoce():
    return render_template("conoce.html")


@main_bp.route("/carpool")
@login_required
def carpool():
    # Mapa con Leaflet.js — sin API key necesaria
    return render_template("carpool.html")


@main_bp.route("/transporte")
@login_required
def transporte():
    return render_template("transporte.html", rutas=RUTAS)


@main_bp.route("/transporte/registro", methods=["GET", "POST"])
@login_required
def registro_ruta():
    if request.method == "POST":
        ruta     = request.form.get("ruta")
        horario  = request.form.get("horario")
        terminos = request.form.get("terminos")

        if not terminos:
            flash("Debes aceptar los términos.", "error")
        elif ruta not in RUTAS:
            flash("Ruta inválida.", "error")
        elif horario not in ("Mañana", "Tarde"):
            flash("Horario inválido.", "error")
        else:
            db.session.add(RegistroRuta(user_id=current_user.id, ruta=ruta, horario=horario))
            db.session.commit()
            flash(f"Registrado en {ruta} — {horario}.", "success")
            return redirect(url_for("main.transporte"))

    return render_template("registro_ruta.html", rutas=RUTAS)