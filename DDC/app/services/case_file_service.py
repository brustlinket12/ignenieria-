from datetime import datetime
from app.models.case_file import CaseFile
from app.models.client import Client
from app.models.user import User
from app.extensions import db


# Estados validos del expediente
VALID_STATUSES = [
    "BORRADOR",
    "EN_REVISION",
    "APROBADO",
    "RECHAZADO",
    "REQUIERE_CORRECCION",
]


def create_case_file(client_data, user_id):
    """Crea un nuevo expediente con datos del cliente."""
    client = Client(
        name=client_data["client_name"],
        id_type=client_data["client_id_type"],
        id_number=client_data["client_id_number"],
        country=client_data["client_country"],
    )
    db.session.add(client)
    db.session.flush()

    case_file = CaseFile(
        client_id=client.id,
        status="BORRADOR",
        current_step=1,
        blocked_by_sanctions=False,
        created_by=user_id,
    )
    db.session.add(case_file)
    db.session.commit()

    return case_file


def update_case_file(case_file_id, data):
    """Actualiza datos del expediente."""
    case_file = CaseFile.query.get(case_file_id)
    if not case_file:
        raise ValueError(f"Expediente {case_file_id} no encontrado")

    if "current_step" in data:
        case_file.current_step = data["current_step"]
    if "status" in data:
        case_file.status = data["status"]

    case_file.updated_at = datetime.utcnow()
    db.session.commit()

    return case_file


def submit_case_file(case_file_id):
    """Envia el expediente para revision."""
    case_file = CaseFile.query.get(case_file_id)
    if not case_file:
        raise ValueError(f"Expediente {case_file_id} no encontrado")

    if case_file.status not in ["BORRADOR", "REQUIERE_CORRECCION"]:
        raise ValueError("Solo expedientes en BORRADOR o REQUIERE_CORRECCION pueden ser enviados")

    risk_level = case_file.risk_assessment.risk_level if case_file.risk_assessment else None
    if case_file.blocked_by_sanctions:
        case_file.status = "EN_REVISION"
    elif risk_level == "BAJO":
        case_file.status = "APROBADO"
    else:
        case_file.status = "EN_REVISION"

    case_file.submitted_at = datetime.utcnow()
    case_file.updated_at = datetime.utcnow()
    db.session.commit()

    return case_file


def approve_case_file(case_file_id, user_id):
    """Aprueba el expediente. Solo OFICIAL_CUMPLIMIENTO."""
    user = User.query.get(user_id)
    if not user:
        raise PermissionError("Usuario no encontrado")

    if not user.is_oficial_cumplimiento():
        raise PermissionError("Solo el Oficial de Cumplimiento puede aprobar expedientes")

    case_file = CaseFile.query.get(case_file_id)
    if not case_file:
        raise ValueError(f"Expediente {case_file_id} no encontrado")

    if case_file.status != "EN_REVISION":
        raise ValueError("Solo expedientes EN_REVISION pueden ser aprobados")

    case_file.status = "APROBADO"
    case_file.reviewed_by = user_id
    case_file.approved_at = datetime.utcnow()
    case_file.updated_at = datetime.utcnow()
    db.session.commit()

    return case_file


def reject_case_file(case_file_id, user_id, reason=None):
    """Rechaza el expediente. Solo OFICIAL_CUMPLIMIENTO."""
    user = User.query.get(user_id)
    if not user:
        raise PermissionError("Usuario no encontrado")

    if not user.is_oficial_cumplimiento():
        raise PermissionError("Solo el Oficial de Cumplimiento puede rechazar expedientes")

    case_file = CaseFile.query.get(case_file_id)
    if not case_file:
        raise ValueError(f"Expediente {case_file_id} no encontrado")

    if case_file.status not in ["EN_REVISION", "REQUIERE_CORRECCION"]:
        raise ValueError("Estado no valido para rechazar")

    case_file.status = "RECHAZADO"
    case_file.reviewed_by = user_id
    case_file.rejected_at = datetime.utcnow()
    case_file.updated_at = datetime.utcnow()
    if reason:
        case_file.rejection_reason = reason

    db.session.commit()

    return case_file


def request_correction_case_file(case_file_id, user_id, correction_note):
    """
    Marca el expediente como REQUIERE_CORRECCION.
    El analista debe corregir y reenviar.
    Solo OFICIAL_CUMPLIMIENTO.
    """
    user = User.query.get(user_id)
    if not user:
        raise PermissionError("Usuario no encontrado")

    if not user.is_oficial_cumplimiento():
        raise PermissionError("Solo el Oficial de Cumplimiento puede solicitar correcciones")

    case_file = CaseFile.query.get(case_file_id)
    if not case_file:
        raise ValueError(f"Expediente {case_file_id} no encontrado")

    if case_file.status != "EN_REVISION":
        raise ValueError("Solo expedientes EN_REVISION pueden requerir correccion")

    case_file.status = "REQUIERE_CORRECCION"
    case_file.reviewed_by = user_id
    case_file.updated_at = datetime.utcnow()
    if correction_note:
        case_file.rejection_reason = correction_note

    db.session.commit()

    return case_file


def get_case_file(case_file_id):
    """Obtiene un expediente por ID."""
    return CaseFile.query.get(case_file_id)


def list_case_files(filters=None, user=None):
    """Lista expedientes con filtros opcionales."""
    query = CaseFile.query

    if user:
        if user.is_analista():
            query = query.filter(CaseFile.created_by == user.id)
        elif user.is_oficial_cumplimiento() or user.is_oficial_auditoria():
            query = query.filter(CaseFile.status != "BORRADOR")

    if filters:
        if "status" in filters:
            query = query.filter(CaseFile.status == filters["status"])
        if "created_by" in filters:
            query = query.filter(CaseFile.created_by == filters["created_by"])

    return query.order_by(CaseFile.created_at.desc()).all()


def block_case_file_if_sanctions(case_file_id, user_id, sanctions_result):
    """
    Marca un expediente con coincidencia en sanciones si el screening devolvio COINCIDENCIA_CONFIRMADA.
    El envio del expediente decide el enrutamiento segun blocked_by_sanctions.
    """
    from app.services.audit_service import log_event
    from app.services.alert_service import create_alert, create_alert_for_role

    case_file = CaseFile.query.get(case_file_id)
    if not case_file:
        raise ValueError(f"Expediente {case_file_id} no encontrado")

    if sanctions_result.result == "COINCIDENCIA_CONFIRMADA":
        case_file.blocked_by_sanctions = True
        case_file.updated_at = datetime.utcnow()
        db.session.commit()

        log_event(case_file_id, user_id, "CASE_BLOCKED_BY_SANCTIONS", {
            "matched_name": sanctions_result.matched_name,
            "matched_list": sanctions_result.matched_list,
        })

        # Alerta al oficial de cumplimiento
        create_alert_for_role(
            case_file_id,
            "BLOQUEO_SANCIONES",
            f"Expediente #{case_file_id} con coincidencia en sanciones confirmada",
            "OFICIAL_CUMPLIMIENTO"
        )

        # Alerta al analista creador
        create_alert(
            case_file_id,
            "BLOQUEO_SANCIONES",
            f"Tu expediente #{case_file_id} tiene coincidencia en sanciones",
            recipient_user_id=case_file.created_by,
        )

    return case_file
