from flask import Blueprint, request, jsonify, session
from app.models.user import User
from app.extensions import db
from marshmallow import ValidationError

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data or "email" not in data or "password" not in data:
        return jsonify({"error": "Email y password son requeridos"}), 400

    user = User.query.filter_by(email=data["email"]).first()

    if not user or not user.check_password(data["password"]):
        return jsonify({"error": "Credenciales invalidas"}), 401

    # Guardar usuario en sesion
    session["user_id"] = user.id
    session["user_email"] = user.email
    session["user_role"] = user.role

    return jsonify({
        "token": f"session_{user.id}",
        "user": user.to_dict()
    }), 200


@auth_bp.route("/api/auth/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Sesion cerrada"}), 200


@auth_bp.route("/api/me", methods=["GET"])
def me():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "No autenticado"}), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404

    return jsonify({"user": user.to_dict()}), 200