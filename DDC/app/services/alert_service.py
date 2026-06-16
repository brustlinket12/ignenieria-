from app.models.alert import Alert
from app.models.user import User
from app.extensions import db


def create_alert(case_file_id, alert_type, message, recipient_user_id=None, recipient_role=None):
    """
    Crea una alerta para un expediente.

    Args:
        case_file_id: ID del expediente
        alert_type: Tipo de alerta
        message: Mensaje de la alerta
        recipient_user_id: Si se especifica, solo ese usuario recibe la alerta
        recipient_role: Si se especifica, todos los usuarios con ese rol reciben la alerta
                        Puede ser: ANALISTA, OFICIAL_CUMPLIMIENTO, OFICIAL_AUDITORIA
    """
    alert = Alert(
        case_file_id=case_file_id,
        type=alert_type,
        message=message,
        read=False,
        recipient_user_id=recipient_user_id,
        recipient_role=recipient_role,
    )
    db.session.add(alert)
    db.session.commit()
    return alert


def create_alert_for_role(case_file_id, alert_type, message, role):
    """Crea una alerta dirigida a todos los usuarios de un rol."""
    return create_alert(
        case_file_id=case_file_id,
        alert_type=alert_type,
        message=message,
        recipient_role=role,
    )


def get_unread_alerts(user_id=None, user_role=None):
    """
    Obtiene alertas no leídas, filtradas por usuario o rol.

    Un usuario ve:
    - Sus alertas personales (recipient_user_id = user_id)
    - Las alertas dirigidas a su rol (recipient_role = user_role)
    - Las alertas sin destinatario especifico (para admin)
    """
    if user_id:
        query = Alert.query.filter(
            Alert.read == False,
            (
                (Alert.recipient_user_id == user_id) |
                (Alert.recipient_role == user_role) |
                (Alert.recipient_user_id.is_(None) & Alert.recipient_role.is_(None))
            )
        )
    else:
        query = Alert.query.filter_by(read=False)

    return query.order_by(Alert.created_at.desc()).all()


def mark_alert_read(alert_id, user_id):
    """Marca una alerta como leída."""
    alert = Alert.query.get(alert_id)
    if not alert:
        return None

    # Verificar que el usuario tiene permiso
    if (alert.recipient_user_id and alert.recipient_user_id != user_id):
        # Si es para otro usuario, no se puede marcar
        return None

    alert.read = True
    db.session.commit()
    return alert


def mark_case_file_alerts_read(case_file_id, user_id):
    """Marca todas las alertas de un expediente como leídas para un usuario."""
    Alert.query.filter(
        Alert.case_file_id == case_file_id,
        Alert.read == False,
        (
            (Alert.recipient_user_id == user_id) |
            (Alert.recipient_user_id.is_(None))
        )
    ).update({"read": True})
    db.session.commit()
