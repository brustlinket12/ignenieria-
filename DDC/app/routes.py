from flask import Blueprint, render_template, redirect

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    return redirect("/login")

@main_bp.route("/login")
def login():
    return render_template("login.html")

@main_bp.route("/mfa")
def mfa():
    return render_template("mfa.html")

@main_bp.route("/dashboard")
def dashboard():
    usuario = {
        "nombre": "Ana Martínez",
        "rol": "OFICIAL_KYC",
        "sesionId": "sess-DDC-2026-0391",
    }
    return render_template("dashboard.html", usuario=usuario)

@main_bp.route("/ddc/formulario/<cliente_id>")
def ddc_formulario_cliente(cliente_id):
    usuario = {
        "nombre": "Ana Martínez",
        "rol": "OFICIAL_KYC",
        "sesionId": "sess-DDC-2026-0391",
    }
    bloqueado = cliente_id == "c-007"
    return render_template("ddc_form.html", usuario=usuario, cliente_id=cliente_id, bloqueado=bloqueado)

@main_bp.route("/ddc/formulario")
def ddc_formulario():
    usuario = {
        "nombre": "Ana Martínez",
        "rol": "OFICIAL_KYC",
        "sesionId": "sess-DDC-2026-0391",
    }
    return render_template("ddc_form.html", usuario=usuario, cliente_id="c-001", bloqueado=False)

@main_bp.route("/ddc/confirmacion")
def ddc_confirmacion():
    usuario = {
        "nombre": "Ana Martínez",
        "rol": "OFICIAL_KYC",
        "sesionId": "sess-DDC-2026-0391",
    }
    return render_template("ddc_confirmacion.html", usuario=usuario)

@main_bp.route("/historial/<cliente_id>")
def historial_cliente(cliente_id):
    usuario = {
        "nombre": "Ana Martínez",
        "rol": "OFICIAL_KYC",
        "sesionId": "sess-DDC-2026-0391",
    }
    return render_template("historial.html", usuario=usuario, cliente_id=cliente_id)

@main_bp.route("/detalle/<cliente_id>")
def detalle_cliente(cliente_id):
    usuario = {
        "nombre": "Ana Martínez",
        "rol": "OFICIAL_KYC",
        "sesionId": "sess-DDC-2026-0391",
    }
    return render_template("detalle.html", usuario=usuario, cliente_id=cliente_id)

@main_bp.route("/historial")
def historial():
    usuario = {
        "nombre": "Ana Martínez",
        "rol": "OFICIAL_KYC",
        "sesionId": "sess-DDC-2026-0391",
    }
    return render_template("historial.html", usuario=usuario, cliente_id="c-001")
