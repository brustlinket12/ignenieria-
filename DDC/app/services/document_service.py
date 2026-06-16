import os
import uuid
from werkzeug.utils import secure_filename
from app.models.document import Document
from app.extensions import db


ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "doc", "docx", "xls", "xlsx"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def get_upload_folder(case_file_id):
    """Retorna la ruta absoluta a la carpeta de uploads del case file."""
    from app.config import config_by_name
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    upload_dir = os.path.join(base_dir, "uploads", "case-files", str(case_file_id))
    os.makedirs(upload_dir, exist_ok=True)
    return upload_dir


def add_document_to_case_file(case_file_id, document_type, file, user_id):
    """Agrega un documento a un expediente."""
    from app.models.case_file import CaseFile

    case_file = CaseFile.query.get(case_file_id)
    if not case_file:
        raise ValueError(f"Expediente {case_file_id} no encontrado")

    if not allowed_file(file.filename):
        raise ValueError(f"Tipo de archivo no permitido. Permitidos: {', '.join(ALLOWED_EXTENSIONS)}")

    if file.content_length and file.content_length > MAX_FILE_SIZE:
        raise ValueError(f"El archivo excede el tamano maximo de {MAX_FILE_SIZE // 1024 // 1024}MB")

    # Generar nombre seguro unico
    original_filename = secure_filename(file.filename)
    ext = original_filename.rsplit(".", 1)[1].lower() if "." in original_filename else ""
    unique_filename = f"{uuid.uuid4().hex}.{ext}" if ext else uuid.uuid4().hex

    upload_dir = get_upload_folder(case_file_id)
    file_path = os.path.join(upload_dir, unique_filename)
    file.save(file_path)

    file_size = os.path.getsize(file_path)

    document = Document(
        case_file_id=case_file_id,
        document_type=document_type,
        filename=original_filename,
        file_path=file_path,
        mime_type=file.content_type or "application/octet-stream",
        size=file_size,
    )
    db.session.add(document)
    db.session.commit()

    return document


def list_case_file_documents(case_file_id):
    """Lista todos los documentos de un expediente."""
    documents = Document.query.filter_by(case_file_id=case_file_id).all()
    return documents


def delete_document(document_id, user_id):
    """Elimina un documento (solo el owner o admin)."""
    document = Document.query.get(document_id)
    if not document:
        raise ValueError(f"Documento {document_id} no encontrado")

    # Eliminar archivo fisico
    if os.path.exists(document.file_path):
        os.remove(document.file_path)

    db.session.delete(document)
    db.session.commit()

    return document
