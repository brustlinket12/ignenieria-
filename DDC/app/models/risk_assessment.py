from datetime import datetime
from app.extensions import db


class RiskAssessment(db.Model):
    __tablename__ = "risk_assessments"

    id = db.Column(db.Integer, primary_key=True)
    case_file_id = db.Column(db.Integer, db.ForeignKey("case_files.id"), nullable=False, unique=True)

    # Campos semanticos guardados para auditoria y referencia
    sector_economico = db.Column(db.String(100), nullable=True)
    jurisdiccion = db.Column(db.String(100), nullable=True)
    pep_status = db.Column(db.String(100), nullable=True)
    volumen_transacciones = db.Column(db.String(100), nullable=True)
    origen_fondos = db.Column(db.String(100), nullable=True)

    # Scores calculados por el backend
    sector_score = db.Column(db.Integer, default=0)
    jurisdiction_score = db.Column(db.Integer, default=0)
    pep_score = db.Column(db.Integer, default=0)
    volume_score = db.Column(db.Integer, default=0)
    funds_origin_score = db.Column(db.Integer, default=0)
    sanctions_score = db.Column(db.Integer, default=0)

    total_score = db.Column(db.Integer, nullable=True)
    risk_level = db.Column(db.String(50), nullable=True)  # BAJO, MEDIO, ALTO, MUY_ALTO
    calculation_aborted = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    case_file = db.relationship("CaseFile", back_populates="risk_assessment")

    def calculate_risk_level(self, total_score):
        if total_score is None:
            return None
        if total_score <= 30:
            return "BAJO"
        elif total_score <= 60:
            return "MEDIO"
        elif total_score <= 90:
            return "ALTO"
        else:
            return "MUY_ALTO"

    def to_dict(self):
        return {
            "id": self.id,
            "case_file_id": self.case_file_id,
            "sector_economico": self.sector_economico,
            "jurisdiccion": self.jurisdiccion,
            "pep_status": self.pep_status,
            "volumen_transacciones": self.volumen_transacciones,
            "origen_fondos": self.origen_fondos,
            "sector_score": self.sector_score,
            "jurisdiction_score": self.jurisdiction_score,
            "pep_score": self.pep_score,
            "volume_score": self.volume_score,
            "funds_origin_score": self.funds_origin_score,
            "sanctions_score": self.sanctions_score,
            "total_score": self.total_score,
            "risk_level": self.risk_level,
            "calculation_aborted": self.calculation_aborted,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }