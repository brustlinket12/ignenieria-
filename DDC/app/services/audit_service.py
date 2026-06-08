import json
from datetime import datetime
from app.models.audit_log import AuditLog
from app.extensions import db


def log_event(case_file_id, user_id, event_type, payload=None):
    """Registra un evento de auditoría."""
    log = AuditLog(
        case_file_id=case_file_id,
        user_id=user_id,
        event_type=event_type,
        payload=json.dumps(payload) if payload else None,
    )
    db.session.add(log)
    db.session.commit()
    return log