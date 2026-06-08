from datetime import datetime
from app.extensions import db


class Alert(db.Model):
    __tablename__ = "alerts"

    id = db.Column(db.Integer, primary_key=True)
    case_file_id = db.Column(db.Integer, db.ForeignKey("case_files.id"), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    case_file = db.relationship("CaseFile", back_populates="alerts")

    def to_dict(self):
        return {
            "id": self.id,
            "case_file_id": self.case_file_id,
            "type": self.type,
            "message": self.message,
            "read": self.read,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }