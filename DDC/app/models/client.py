from datetime import datetime
from app.extensions import db


class Client(db.Model):
    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    id_type = db.Column(db.String(50), nullable=False)  # DNI, PASAPORTE, CEDULA
    id_number = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    case_files = db.relationship("CaseFile", back_populates="client")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "id_type": self.id_type,
            "id_number": self.id_number,
            "country": self.country,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }