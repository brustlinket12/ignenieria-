from datetime import datetime
from app.extensions import db


class CaseFile(db.Model):
    __tablename__ = "case_files"

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("clients.id"), nullable=False)
    status = db.Column(db.String(50), nullable=False, default="BORRADOR")
    current_step = db.Column(db.Integer, default=1)
    blocked_by_sanctions = db.Column(db.Boolean, default=False)

    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    reviewed_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    submitted_at = db.Column(db.DateTime, nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    rejected_at = db.Column(db.DateTime, nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)  # Razon de rechazo o correccion requerida

    # Estados: BORRADOR, EN_REVISION, APROBADO, RECHAZADO, BLOQUEADO_POR_SANCIONES, DESBLOQUEADO_FALSO_POSITIVO, REQUIERE_CORRECCION

    # Relaciones
    client = db.relationship("Client", back_populates="case_files")
    creator = db.relationship("User", foreign_keys=[created_by], back_populates="case_files_created")
    reviewer = db.relationship("User", foreign_keys=[reviewed_by], back_populates="case_files_reviewed")
    risk_assessment = db.relationship("RiskAssessment", back_populates="case_file", uselist=False)
    sanctions_screening = db.relationship("SanctionsScreening", back_populates="case_file")
    alerts = db.relationship("Alert", back_populates="case_file")
    audit_logs = db.relationship("AuditLog", back_populates="case_file")
    documents = db.relationship("Document", back_populates="case_file")

    def to_dict(self):
        return {
            "id": self.id,
            "client_id": self.client_id,
            "client": self.client.to_dict() if self.client else None,
            "status": self.status,
            "current_step": self.current_step,
            "blocked_by_sanctions": self.blocked_by_sanctions,
            "created_by": self.created_by,
            "reviewed_by": self.reviewed_by,
            "rejection_reason": self.rejection_reason,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "rejected_at": self.rejected_at.isoformat() if self.rejected_at else None,
            "risk_assessment": self.risk_assessment.to_dict() if self.risk_assessment else None,
            "sanctions_screening": [s.to_dict() for s in self.sanctions_screening] if self.sanctions_screening else [],
            "documents": [d.to_dict() for d in self.documents] if self.documents else [],
            "alerts": [a.to_dict() for a in self.alerts] if self.alerts else [],
        }