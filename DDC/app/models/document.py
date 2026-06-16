from datetime import datetime
from app.extensions import db


class Document(db.Model):
    __tablename__ = "documents"

    id = db.Column(db.Integer, primary_key=True)
    case_file_id = db.Column(db.Integer, db.ForeignKey("case_files.id"), nullable=False)
    document_type = db.Column(db.String(100), nullable=False)  # IDENTIFICACION, COMPROBANTE_DOMICILIO, etc
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    mime_type = db.Column(db.String(100), nullable=True)
    size = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    case_file = db.relationship("CaseFile", back_populates="documents")

    def to_dict(self):
        return {
            "id": self.id,
            "case_file_id": self.case_file_id,
            "document_type": self.document_type,
            "filename": self.filename,
            "file_path": self.file_path,
            "mime_type": self.mime_type,
            "size": self.size,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }