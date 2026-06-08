from datetime import datetime
from app.extensions import db


class SanctionsScreening(db.Model):
    __tablename__ = "sanctions_screenings"

    id = db.Column(db.Integer, primary_key=True)
    case_file_id = db.Column(db.Integer, db.ForeignKey("case_files.id"), nullable=False)

    provider = db.Column(db.String(100), default="MOCK_PROVIDER")
    result = db.Column(db.String(50), nullable=False)
    matched_name = db.Column(db.String(255), nullable=True)
    matched_list = db.Column(db.String(255), nullable=True)
    raw_response = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Resultados: SIN_COINCIDENCIA, COINCIDENCIA_PARCIAL, COINCIDENCIA_CONFIRMADA, ERROR_CONSULTA

    # Relaciones
    case_file = db.relationship("CaseFile", back_populates="sanctions_screening")

    def to_dict(self):
        return {
            "id": self.id,
            "case_file_id": self.case_file_id,
            "provider": self.provider,
            "result": self.result,
            "matched_name": self.matched_name,
            "matched_list": self.matched_list,
            "raw_response": self.raw_response,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }