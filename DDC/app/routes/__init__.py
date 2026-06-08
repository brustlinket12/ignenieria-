from app.routes.health import health_bp
from app.routes.auth import auth_bp
from app.routes.clients import clients_bp
from app.routes.case_files import case_files_bp
from app.routes.alerts import alerts_bp

__all__ = ["health_bp", "auth_bp", "clients_bp", "case_files_bp", "alerts_bp"]