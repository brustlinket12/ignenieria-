from app.extensions import db

# Importar todos los modelos para que SQLAlchemy resuelva las relaciones
from app.models.user import User
from app.models.client import Client
from app.models.case_file import CaseFile
from app.models.risk_assessment import RiskAssessment
from app.models.sanctions_screening import SanctionsScreening
from app.models.alert import Alert
from app.models.audit_log import AuditLog
from app.models.document import Document

__all__ = [
    "db",
    "User",
    "Client",
    "CaseFile",
    "RiskAssessment",
    "SanctionsScreening",
    "Alert",
    "AuditLog",
    "Document",
]