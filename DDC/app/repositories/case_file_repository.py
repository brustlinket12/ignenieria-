from app.models.case_file import CaseFile
from app.models.client import Client
from app.extensions import db


def create(case_file_data):
    """Crea un nuevo expediente."""
    client = Client(
        name=case_file_data.get("client_name"),
        id_type=case_file_data.get("client_id_type"),
        id_number=case_file_data.get("client_id_number"),
        country=case_file_data.get("client_country"),
    )
    db.session.add(client)
    db.session.flush()

    case_file = CaseFile(
        client_id=client.id,
        status="BORRADOR",
        current_step=1,
        blocked_by_sanctions=False,
        created_by=case_file_data.get("user_id"),
    )
    db.session.add(case_file)
    db.session.commit()
    return case_file


def get_by_id(case_file_id):
    """Obtiene un expediente por ID."""
    return CaseFile.query.get(case_file_id)


def get_all(filters=None):
    """Lista todos los expedientes con filtros opcionales."""
    query = CaseFile.query
    if filters:
        if "status" in filters:
            query = query.filter(CaseFile.status == filters["status"])
        if "blocked" in filters:
            query = query.filter(CaseFile.blocked_by_sanctions == filters["blocked"])
    return query.order_by(CaseFile.created_at.desc()).all()


def update(case_file_id, data):
    """Actualiza un expediente."""
    case_file = CaseFile.query.get(case_file_id)
    if not case_file:
        return None

    for key, value in data.items():
        if hasattr(case_file, key):
            setattr(case_file, key, value)

    db.session.commit()
    return case_file


def delete(case_file_id):
    """Elimina un expediente."""
    case_file = CaseFile.query.get(case_file_id)
    if case_file:
        db.session.delete(case_file)
        db.session.commit()
        return True
    return False