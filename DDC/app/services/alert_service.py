from app.models.alert import Alert
from app.models.user import User
from app.extensions import db


def create_alert(case_file_id, alert_type, message):
    """Crea una alerta para un expediente."""
    alert = Alert(
        case_file_id=case_file_id,
        type=alert_type,
        message=message,
        read=False,
    )
    db.session.add(alert)
    db.session.commit()
    return alert


def get_unread_alerts(user_id=None):
    """Obtiene alertas no leídas, opcionalmente filtradas por usuario."""
    query = Alert.query.filter_by(read=False)
    return query.order_by(Alert.created_at.desc()).all()