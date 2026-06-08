from flask import Blueprint, request, jsonify, session
from app.models.alert import Alert
from app.models.user import User

alerts_bp = Blueprint("alerts", __name__)


@alerts_bp.route("/api/alerts", methods=["GET"])
def list_alerts():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "No autenticado"}), 401

    alerts = Alert.query.filter_by(read=False).order_by(Alert.created_at.desc()).all()
    return jsonify([a.to_dict() for a in alerts]), 200


@alerts_bp.route("/api/alerts/<int:alert_id>/read", methods=["PATCH"])
def mark_read(alert_id):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "No autenticado"}), 401

    alert = Alert.query.get(alert_id)
    if not alert:
        return jsonify({"error": "Alerta no encontrada"}), 404

    alert.read = True
    from app.extensions import db
    db.session.commit()

    return jsonify(alert.to_dict()), 200