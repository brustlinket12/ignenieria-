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
    request_correction_case_file,
    unblock_case_file,
    get_case_file,
    list_case_files,
    calculate_risk,
    screen_name,
    log_event,
    create_alert,
    create_alert_for_role,
    block_case_file_if_sanctions,
)
from app.services.document_service import (
    add_document_to_case_file,
    list_case_file_documents,
    delete_document,
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

    # Solo ANALISTA y ADMIN pueden crear expedientes
    if not (user.is_analista() or user.is_admin()):
        return jsonify({"error": "Solo analistas y admins pueden crear expedientes"}), 403

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
    if request.args.get("created_by"):
        filters["created_by"] = request.args.get("created_by")

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

    # Solo el creador puede actualizar si esta en BORRADOR o REQUIERE_CORRECCION
    case_file = get_case_file(case_file_id)
    if not case_file:
        return jsonify({"error": "Expediente no encontrado"}), 404

    if case_file.created_by != user.id and not user.is_admin():
        return jsonify({"error": "Solo el creador o admin pueden editar"}), 403

    if case_file.status not in ["BORRADOR", "REQUIERE_CORRECCION"]:
        return jsonify({"error": "No se puede editar un expediente en revision o ya procesado"}), 400

    data = request.get_json()
    try:
        case_file = update_case_file(case_file_id, data)
        log_event(case_file_id, user.id, "CASE_UPDATED", data)
        return jsonify(case_file.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ============================================================
# DOCUMENTOS
# ============================================================

@case_files_bp.route("/api/case-files/<int:case_file_id>/documents", methods=["GET"])
def get_documents(case_file_id):
    """Lista todos los documentos de un expediente."""
    case_file = get_case_file(case_file_id)
    if not case_file:
        return jsonify({"error": "Expediente no encontrado"}), 404

    documents = list_case_file_documents(case_file_id)
    return jsonify([doc.to_dict() for doc in documents]), 200


@case_files_bp.route("/api/case-files/<int:case_file_id>/documents", methods=["POST"])
def upload_document(case_file_id):
    """Sube un documento a un expediente (multipart/form-data)."""
    user = get_current_user()
    if not user:
        return jsonify({"error": "No autenticado"}), 401

    case_file = get_case_file(case_file_id)
    if not case_file:
        return jsonify({"error": "Expediente no encontrado"}), 404

    # Solo el creador puede subir documentos si esta en BORRADOR o REQUIERE_CORRECCION
    if case_file.created_by != user.id and not user.is_admin():
        return jsonify({"error": "Solo el creador o admin pueden subir documentos"}), 403

    if case_file.status not in ["BORRADOR", "REQUIERE_CORRECCION"]:
        return jsonify({"error": "No se pueden agregar documentos a un expediente en revision o ya procesado"}), 400

    if "file" not in request.files:
        return jsonify({"error": "No se encontro archivo en la peticion"}), 400

    file = request.files["file"]
    document_type = request.form.get("document_type", "OTRO")

    if file.filename == "":
        return jsonify({"error": "No se selecciono archivo"}), 400

    try:
        document = add_document_to_case_file(case_file_id, document_type, file, user.id)
        log_event(case_file_id, user.id, "DOCUMENT_UPLOADED", {
            "document_id": document.id,
            "document_type": document_type,
            "filename": document.filename,
        })
        return jsonify(document.to_dict()), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@case_files_bp.route("/api/case-files/<int:case_file_id>/documents/<int:document_id>", methods=["DELETE"])
def remove_document(case_file_id, document_id):
    """Elimina un documento de un expediente."""
    user = get_current_user()
    if not user:
        return jsonify({"error": "No autenticado"}), 401

    case_file = get_case_file(case_file_id)
    if not case_file:
        return jsonify({"error": "Expediente no encontrado"}), 404

    if case_file.created_by != user.id and not user.is_admin():
        return jsonify({"error": "Solo el creador o admin pueden eliminar documentos"}), 403

    try:
        document = delete_document(document_id, user.id)
        log_event(case_file_id, user.id, "DOCUMENT_DELETED", {
            "document_id": document_id,
            "filename": document.filename,
        })
        return jsonify({"message": "Documento eliminado"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


# ============================================================
# SUBMIT Y FLUJO DE APROBACION
# ============================================================

@case_files_bp.route("/api/case-files/<int:case_file_id>/submit", methods=["POST"])
def submit(case_file_id):
    user = get_current_user()
    if not user:
        return jsonify({"error": "No autenticado"}), 401

    try:
        case_file = submit_case_file(case_file_id)
        log_event(case_file_id, user.id, "CASE_SUBMITTED", {})

        # Alertar al oficial de cumplimiento
        create_alert_for_role(
            case_file_id,
            "NUEVO_EXPEDIENTE",
            f"Nuevo expediente #{case_file_id} enviado a revision por {user.name}",
            "OFICIAL_CUMPLIMIENTO"
        )

        return jsonify(case_file.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@case_files_bp.route("/api/case-files/<int:case_file_id>/risk-assessment", methods=["POST"])
def risk_assessment(case_file_id):
    user = get_current_user()
    if not user:
        return jsonify({"error": "No autenticado"}), 401

    # Solo el creador puede calcular riesgo
    case_file = get_case_file(case_file_id)
    if not case_file:
        return jsonify({"error": "Expediente no encontrado"}), 404

    if case_file.created_by != user.id and not user.is_admin():
        return jsonify({"error": "Solo el creador puede evaluar el riesgo"}), 403

    data = request.get_json()

    # Hacer screening de sanciones primero
    client = case_file.client
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

        # Alerta al analista creador
        create_alert(
            case_file_id,
            "EXPEDIENTE_APROBADO",
            f"Tu expediente #{case_file_id} fue APROBADO por {user.name}",
            recipient_user_id=case_file.created_by,
        )

        return jsonify(case_file.to_dict()), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@case_files_bp.route("/api/case-files/<int:case_file_id>/reject", methods=["POST"])
def reject(case_file_id):
    user = get_current_user()
    if not user:
        return jsonify({"error": "No autenticado"}), 401

    data = request.get_json() or {}
    reason = data.get("reason")

    try:
        case_file = reject_case_file(case_file_id, user.id, reason)
        log_event(case_file_id, user.id, "CASE_REJECTED", {"reason": reason})

        # Alerta al analista creador
        create_alert(
            case_file_id,
            "EXPEDIENTE_RECHAZADO",
            f"Tu expediente #{case_file_id} fue RECHAZADO por {user.name}: {reason or 'Sin motivo especificado'}",
            recipient_user_id=case_file.created_by,
        )

        return jsonify(case_file.to_dict()), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@case_files_bp.route("/api/case-files/<int:case_file_id>/request-correction", methods=["POST"])
def request_correction(case_file_id):
    user = get_current_user()
    if not user:
        return jsonify({"error": "No autenticado"}), 401

    data = request.get_json() or {}
    correction_note = data.get("correction_note")

    try:
        case_file = request_correction_case_file(case_file_id, user.id, correction_note)
        log_event(case_file_id, user.id, "CASE_REQUIRES_CORRECTION", {"note": correction_note})

        # Alerta al analista creador
        create_alert(
            case_file_id,
            "REQUIERE_CORRECCION",
            f"Tu expediente #{case_file_id} requiere correccion: {correction_note or 'Sin especificacion'}",
            recipient_user_id=case_file.created_by,
        )

        return jsonify(case_file.to_dict()), 200
    except PermissionError as e:
        return jsonify({"error": str(e)}), 403
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

        # Alerta al analista creador
        create_alert(
            case_file_id,
            "DESBLOQUEADO_FALSO_POSITIVO",
            f"Tu expediente #{case_file_id} fue desbloqueado como falso positivo por {user.name}",
            recipient_user_id=case_file.created_by,
        )

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
