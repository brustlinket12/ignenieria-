import pytest
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.client import Client
from app.models.case_file import CaseFile
from app.models.risk_assessment import RiskAssessment
from app.models.sanctions_screening import SanctionsScreening
from app.services.case_file_service import (
    create_case_file,
    submit_case_file,
    approve_case_file,
    reject_case_file,
    get_case_file,
)


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def user_analista(app):
    with app.app_context():
        user = User(email="analista@test.com", name="Analista", role="ANALISTA")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture
def user_oficial(app):
    with app.app_context():
        user = User(email="oficial@test.com", name="Oficial", role="OFICIAL_CUMPLIMIENTO")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture
def client(app):
    with app.app_context():
        client = Client(name="Test Client", id_type="DNI", id_number="12345678", country="Argentina")
        db.session.add(client)
        db.session.commit()
        return client.id


class TestCaseFileService:
    """Tests para el servicio de expedientes."""

    def test_crear_expediente(self, app, user_analista):
        """Verifica que se puede crear un expediente correctamente."""
        with app.app_context():
            client_data = {
                "client_name": "Nuevo Cliente",
                "client_id_type": "PASAPORTE",
                "client_id_number": "AB123456",
                "client_country": "Chile",
            }
            case_file = create_case_file(client_data, user_analista)

            assert case_file.id is not None
            assert case_file.status == "BORRADOR"
            assert case_file.client.name == "Nuevo Cliente"

    def test_submit_expediente(self, app, user_analista, client):
        """Verifica que un expediente puede ser enviado a revision."""
        with app.app_context():
            # Crear expediente
            case_file = CaseFile(client_id=client, status="BORRADOR", created_by=user_analista)
            db.session.add(case_file)
            db.session.commit()

            case_file = submit_case_file(case_file.id)

            assert case_file.status == "EN_REVISION"
            assert case_file.submitted_at is not None

    def test_bloqueo_por_sanciones(self, app, user_analista, client):
        """
        Verifica que cuando un expediente tiene screening con COINCIDENCIA_CONFIRMADA,
        queda marcado con coincidencia en sanciones sin cambiar su estado.
        """
        from app.services.case_file_service import block_case_file_if_sanctions

        with app.app_context():
            # Crear expediente
            case_file = CaseFile(client_id=client, status="EN_REVISION", created_by=user_analista)
            db.session.add(case_file)
            db.session.flush()

            # Crear screening con coincidencia confirmada
            screening = SanctionsScreening(
                case_file_id=case_file.id,
                provider="MOCK",
                result="COINCIDENCIA_CONFIRMADA",
                matched_name="SANCIONADO_TEST",
                matched_list="LISTA_TEST",
            )
            db.session.add(screening)
            db.session.flush()

            # Crear assessment abortado
            assessment = RiskAssessment(
                case_file_id=case_file.id,
                sanctions_score=3,
                calculation_aborted=True,
                total_score=None,
                risk_level=None,
            )
            db.session.add(assessment)
            db.session.commit()

            # Aplicar marca de coincidencia via servicio
            block_case_file_if_sanctions(case_file.id, user_analista, screening)

            # Verificar flag de sanciones sin estado de bloqueo dedicado
            case_file = get_case_file(case_file.id)
            assert case_file.status == "EN_REVISION"
            assert case_file.blocked_by_sanctions is True

    def test_submit_con_sanciones_va_a_revision(self, app, user_analista, client):
        """
        CRITICO: Un expediente con coincidencia en sanciones enviado queda EN_REVISION.
        """
        with app.app_context():
            case_file = CaseFile(
                client_id=client,
                status="BORRADOR",
                blocked_by_sanctions=True,
                created_by=user_analista,
            )
            db.session.add(case_file)
            db.session.commit()

            case_file = submit_case_file(case_file.id)
            assert case_file.status == "EN_REVISION"
            assert case_file.blocked_by_sanctions is True

    def test_aprobar_expediente(self, app, user_oficial, client):
        """Verifica que un expediente puede ser aprobado."""
        with app.app_context():
            case_file = CaseFile(
                client_id=client,
                status="EN_REVISION",
                created_by=1,  # user_analista
            )
            db.session.add(case_file)
            db.session.commit()

            case_file = approve_case_file(case_file.id, user_oficial)

            assert case_file.status == "APROBADO"
            assert case_file.reviewed_by == user_oficial
            assert case_file.approved_at is not None

    def test_rechazar_expediente(self, app, user_oficial, client):
        """Verifica que un expediente puede ser rechazado."""
        with app.app_context():
            case_file = CaseFile(
                client_id=client,
                status="EN_REVISION",
                created_by=1,
            )
            db.session.add(case_file)
            db.session.commit()

            case_file = reject_case_file(case_file.id, user_oficial)

            assert case_file.status == "RECHAZADO"
            assert case_file.reviewed_by == user_oficial
            assert case_file.rejected_at is not None


class TestAuth:
    """Tests para autenticacion y permisos."""

    def test_login_valido(self, app, user_analista):
        """Verifica login con credenciales validas."""
        with app.app_context():
            user = User.query.get(user_analista)
            assert user.check_password("password123") is True

    def test_login_invalido(self, app, user_analista):
        """Verifica login con credenciales invalidas."""
        with app.app_context():
            user = User.query.get(user_analista)
            assert user.check_password("wrong_password") is False

    def test_solo_oficial_cumplimiento_tiene_rol_de_revision(self, app, user_analista, user_oficial, client):
        """
        Verifica que la restriccion de rol de cumplimiento funciona.
        """
        with app.app_context():
            case_file = CaseFile(
                client_id=client,
                status="EN_REVISION",
                blocked_by_sanctions=True,
                created_by=user_analista,
            )
            db.session.add(case_file)
            db.session.commit()

            # Verificar que analista no tiene permiso
            user = User.query.get(user_analista)
            assert user.is_oficial_cumplimiento() is False

            # Verificar que oficial tiene permiso
            user_of = User.query.get(user_oficial)
            assert user_of.is_oficial_cumplimiento() is True
