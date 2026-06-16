from flask import Blueprint, request, jsonify, session
from app.models.alert import Alert
from app.models.user import User
from app.services.alert_service import (
    get_unread_alerts,
    mark_alert_read,
    create_alert_for_role,
)

alerts_bp = Blueprint("alerts", __name__)


@alerts_bp.route("/api/alerts", methods=["GET"])
def list_alerts():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "No autenticado"}), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404
    if user.is_oficial_auditoria():
        return jsonify({"error": "No tienes permiso para ver alertas"}), 403

    # Filtrar alertas por usuario o rol
    alerts = get_unread_alerts(user_id=user.id, user_role=user.role)
    return jsonify([a.to_dict() for a in alerts]), 200


@alerts_bp.route("/api/alerts/<int:alert_id>/read", methods=["PATCH"])
def mark_read(alert_id):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "No autenticado"}), 401

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404
    if user.is_oficial_auditoria():
        return jsonify({"error": "No tienes permiso para ver alertas"}), 403

    alert = Alert.query.get(alert_id)
    if not alert:
        return jsonify({"error": "Alerta no encontrada"}), 404

    # Solo puede marcar como leida si es para el o para su rol
    if (alert.recipient_user_id and alert.recipient_user_id != user_id):
        return jsonify({"error": "No tienes permiso"}), 403

    alert.read = True
    from app.extensions import db
    db.session.commit()

    return jsonify(alert.to_dict()), 200
