from datetime import datetime
from app.models.case_file import CaseFile
from app.models.client import Client
from app.extensions import db


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
    """Envía el expediente para revisión."""
    case_file = CaseFile.query.get(case_file_id)
    if not case_file:
        raise ValueError(f"Expediente {case_file_id} no encontrado")

    if case_file.status != "BORRADOR":
        raise ValueError("Solo expedientes en BORRADOR pueden ser enviados")

    if case_file.blocked_by_sanctions:
        raise ValueError("No se puede enviar un expediente bloqueado por sanciones")

    case_file.status = "EN_REVISION"
    case_file.submitted_at = datetime.utcnow()
    case_file.updated_at = datetime.utcnow()
    db.session.commit()

    return case_file


def approve_case_file(case_file_id, user_id):
    """Aprueba el expediente."""
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


def reject_case_file(case_file_id, user_id):
    """Rechaza el expediente."""
    case_file = CaseFile.query.get(case_file_id)
    if not case_file:
        raise ValueError(f"Expediente {case_file_id} no encontrado")

    if case_file.status not in ["EN_REVISION", "BLOQUEADO_POR_SANCIONES"]:
        raise ValueError("Estado no valido para rechazar")

    case_file.status = "RECHAZADO"
    case_file.reviewed_by = user_id
    case_file.rejected_at = datetime.utcnow()
    case_file.updated_at = datetime.utcnow()
    db.session.commit()

    return case_file


def unblock_case_file(case_file_id, user_id, justification):
    """
    Desbloquea un expediente marcado como falso positivo.
    Solo usuarios con rol OFICIAL_CUMPLIMIENTO pueden ejecutar esta accion.
    """
    from app.models.user import User

    user = User.query.get(user_id)
    if not user or not user.is_oficial_cumplimiento():
        raise PermissionError("Solo oficiales de cumplimiento pueden desbloquear expedientes")

    case_file = CaseFile.query.get(case_file_id)
    if not case_file:
        raise ValueError(f"Expediente {case_file_id} no encontrado")

    if case_file.status != "BLOQUEADO_POR_SANCIONES":
        raise ValueError("Solo expedientes BLOQUEADOS_POR_SANCIONES pueden ser desbloqueados")

    case_file.status = "DESBLOQUEADO_FALSO_POSITIVO"
    case_file.blocked_by_sanctions = False
    case_file.reviewed_by = user_id
    case_file.updated_at = datetime.utcnow()
    db.session.commit()

    return case_file


def get_case_file(case_file_id):
    """Obtiene un expediente por ID."""
    return CaseFile.query.get(case_file_id)


def block_case_file_if_sanctions(case_file_id, user_id, sanctions_result):
    """
    Bloquea un expediente si el screening de sanciones devolvio COINCIDENCIA_CONFIRMADA.
    Este es el unico punto donde se aplica el bloqueo por sanciones.
    """
    from app.services.audit_service import log_event
    from app.services.alert_service import create_alert

    case_file = CaseFile.query.get(case_file_id)
    if not case_file:
        raise ValueError(f"Expediente {case_file_id} no encontrado")

    if sanctions_result.result == "COINCIDENCIA_CONFIRMADA":
        case_file.status = "BLOQUEADO_POR_SANCIONES"
        case_file.blocked_by_sanctions = True
        case_file.updated_at = datetime.utcnow()
        db.session.commit()

        log_event(case_file_id, user_id, "CASE_BLOCKED_BY_SANCTIONS", {
            "matched_name": sanctions_result.matched_name,
            "matched_list": sanctions_result.matched_list,
        })
        create_alert(
            case_file_id,
            "BLOQUEO_SANCIONES",
            f"Expediente bloqueado: coincidencia confirmada en lista de sanciones"
        )

    return case_file


def list_case_files(filters=None):
    """Lista expedientes con filtros opcionales."""
    query = CaseFile.query

    if filters:
        if "status" in filters:
            query = query.filter(CaseFile.status == filters["status"])
        if "created_by" in filters:
            query = query.filter(CaseFile.created_by == filters["created_by"])

    return query.order_by(CaseFile.created_at.desc()).all()