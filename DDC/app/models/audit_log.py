from datetime import datetime
from app.extensions import db


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    case_file_id = db.Column(db.Integer, db.ForeignKey("case_files.id"), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    event_type = db.Column(db.String(100), nullable=False)
    payload = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Tipos: CASE_CREATED, CASE_UPDATED, RISK_CALCULATED, SANCTIONS_SCREENED,
    #        CASE_BLOCKED_BY_SANCIONES, CASE_SUBMITTED, CASE_APPROVED,
    #        CASE_REJECTED, CASE_UNLOCKED_FALSE_POSITIVE

    # Relaciones
    case_file = db.relationship("CaseFile", back_populates="audit_logs")
    user = db.relationship("User", back_populates="audit_logs")

    def to_dict(self):
        return {
            "id": self.id,
            "case_file_id": self.case_file_id,
            "user_id": self.user_id,
            "event_type": self.event_type,
            "payload": self.payload,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "user": self.user.to_dict() if self.user else None,
        }