from flask import Blueprint, request, jsonify, session
from datetime import datetime
from app.models.case_file import CaseFile
from app.models.user import User
from app.models.risk_assessment import RiskAssessment
from app.services import (
    create_case_file,
    update_case_file,
    submit_case_file,
    approve_case_file,
    reject_case_file,
    unblock_case_file,
    get_case_file,
    list_case_files,
    calculate_risk,
    screen_name,
    log_event,
    create_alert,
    block_case_file_if_sanctions,
)
from app.extensions import db

case_files_bp = Blueprint("case_files", __name__)


def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return User.query.get(user_id)


@case_files_bp.route("/api/case-files", methods=["POST"])
def create():
    user = get_current_user()
    if not user:
        return jsonify({"error": "No autenticado"}), 401

    data = request.get_json()
    try:
        case_file = create_case_file(data, user.id)
        log_event(case_file.id, user.id, "CASE_CREATED", {"client": data})
        return jsonify(case_file.to_dict()), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@case_files_bp.route("/api/case-files", methods=["GET"])
def list_all():
    filters = {}
    if request.args.get("status"):
        filters["status"] = request.args.get("status")

    case_files = list_case_files(filters if filters else None)
    return jsonify([cf.to_dict() for cf in case_files]), 200


@case_files_bp.route("/api/case-files/<int:case_file_id>", methods=["GET"])
def get_one(case_file_id):
    case_file = get_case_file(case_file_id)
    if not case_file:
        return jsonify({"error": "Expediente no encontrado"}), 404
    return jsonify(case_file.to_dict()), 200


@case_files_bp.route("/api/case-files/<int:case_file_id>", methods=["PATCH"])
def update_one(case_file_id):
    user = get_current_user()
    if not user:
        return jsonify({"error": "No autenticado"}), 401

    data = request.get_json()
    try:
        case_file = update_case_file(case_file_id, data)
        log_event(case_file_id, user.id, "CASE_UPDATED", data)
        return jsonify(case_file.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@case_files_bp.route("/api/case-files/<int:case_file_id>/submit", methods=["POST"])
def submit(case_file_id):
    user = get_current_user()
    if not user:
        return jsonify({"error": "No autenticado"}), 401

    try:
        case_file = submit_case_file(case_file_id)
        log_event(case_file_id, user.id, "CASE_SUBMITTED", {})
        return jsonify(case_file.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@case_files_bp.route("/api/case-files/<int:case_file_id>/risk-assessment", methods=["POST"])
def risk_assessment(case_file_id):
    user = get_current_user()
    if not user:
        return jsonify({"error": "No autenticado"}), 401

    data = request.get_json()

    # Hacer screening de sanciones primero
    client = CaseFile.query.get(case_file_id).client
    sanctions_result = screen_name(case_file_id, client.name)

    # Mapear resultado de sanctions a score
    sanctions_score_map = {
        "SIN_COINCIDENCIA": 0,
        "COINCIDENCIA_PARCIAL": 1,
        "COINCIDENCIA_CONFIRMADA": 3,
        "ERROR_CONSULTA": 0,
    }
    data["sanctions_score"] = sanctions_score_map.get(sanctions_result.result, 0)

    # Calcular riesgo
    assessment = calculate_risk(case_file_id, data)

    # Si el calculation fue abortado por coincidencia confirmada, bloquear
    if assessment.calculation_aborted:
        block_case_file_if_sanctions(case_file_id, user.id, sanctions_result)
    else:
        log_event(case_file_id, user.id, "RISK_CALCULATED", assessment.to_dict())

    return jsonify(assessment.to_dict()), 200


@case_files_bp.route("/api/case-files/<int:case_file_id>/approve", methods=["POST"])
def approve(case_file_id):
    user = get_current_user()
    if not user:
        return jsonify({"error": "No autenticado"}), 401

    try:
        case_file = approve_case_file(case_file_id, user.id)
        log_event(case_file_id, user.id, "CASE_APPROVED", {})
        return jsonify(case_file.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@case_files_bp.route("/api/case-files/<int:case_file_id>/reject", methods=["POST"])
def reject(case_file_id):
    user = get_current_user()
    if not user:
        return jsonify({"error": "No autenticado"}), 401

    data = request.get_json() or {}
    try:
        case_file = reject_case_file(case_file_id, user.id)
        log_event(case_file_id, user.id, "CASE_REJECTED", {"reason": data.get("reason")})
        return jsonify(case_file.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@case_files_bp.route("/api/case-files/<int:case_file_id>/unblock", methods=["POST"])
def unblock(case_file_id):
    user = get_current_user()
    if not user:
        return jsonify({"error": "No autenticado"}), 401

    data = request.get_json() or {}
    justification = data.get("justification", "")

    try:
        case_file = unblock_case_file(case_file_id, user.id, justification)
        log_event(case_file_id, user.id, "CASE_UNLOCKED_FALSE_POSITIVE", {
            "justification": justification
        })
        return jsonify(case_file.to_dict()), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@case_files_bp.route("/api/case-files/<int:case_file_id>/audit-logs", methods=["GET"])
def audit_logs(case_file_id):
    case_file = get_case_file(case_file_id)
    if not case_file:
        return jsonify({"error": "Expediente no encontrado"}), 404

    logs = case_file.audit_logs
    return jsonify([log.to_dict() for log in logs]), 200


@case_files_bp.route("/api/case-files/<int:case_file_id>/alerts", methods=["GET"])
def alerts(case_file_id):
    case_file = get_case_file(case_file_id)
    if not case_file:
        return jsonify({"error": "Expediente no encontrado"}), 404

    alerts_list = case_file.alerts
    return jsonify([a.to_dict() for a in alerts_list]), 200