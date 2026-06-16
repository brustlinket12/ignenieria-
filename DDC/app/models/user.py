from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # ANALISTA, OFICIAL_CUMPLIMIENTO, OFICIAL_AUDITORIA
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    case_files_created = db.relationship("CaseFile", foreign_keys="CaseFile.created_by", back_populates="creator")
    case_files_reviewed = db.relationship("CaseFile", foreign_keys="CaseFile.reviewed_by", back_populates="reviewer")
    audit_logs = db.relationship("AuditLog", back_populates="user")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_oficial_cumplimiento(self):
        return self.role == "OFICIAL_CUMPLIMIENTO"

    def is_oficial_auditoria(self):
        return self.role == "OFICIAL_AUDITORIA"

    def is_admin(self):
        return self.role == "ADMIN"

    def is_analista(self):
        return self.role == "ANALISTA"

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "role": self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
