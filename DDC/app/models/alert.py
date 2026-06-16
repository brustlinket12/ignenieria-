from datetime import datetime
from app.extensions import db


class Alert(db.Model):
    __tablename__ = "alerts"

    id = db.Column(db.Integer, primary_key=True)
    case_file_id = db.Column(db.Integer, db.ForeignKey("case_files.id"), nullable=False)
    recipient_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)  # null = todos los del rol
    recipient_role = db.Column(db.String(50), nullable=True)  # ANALISTA, OFICIAL_CUMPLIMIENTO, OFICIAL_AUDITORIA
    type = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    case_file = db.relationship("CaseFile", back_populates="alerts")
    recipient_user = db.relationship("User", foreign_keys=[recipient_user_id])

    def to_dict(self):
        return {
            "id": self.id,
            "case_file_id": self.case_file_id,
            "recipient_user_id": self.recipient_user_id,
            "recipient_role": self.recipient_role,
            "type": self.type,
            "message": self.message,
            "read": self.read,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
