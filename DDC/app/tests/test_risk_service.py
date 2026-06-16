import pytest
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.client import Client
from app.models.case_file import CaseFile
from app.models.risk_assessment import RiskAssessment
from app.services.risk_service import VOLUME_SCORES, calculate_risk, calculate_risk_from_selections


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client_data():
    return {
        "name": "Test Client",
        "id_type": "DNI",
        "id_number": "12345678",
        "country": "Argentina",
    }


@pytest.fixture
def setup_case_file(app, client_data):
    with app.app_context():
        # Crear usuario
        user = User(email="test@test.com", name="Test", role="ANALISTA")
        user.set_password("password")
        db.session.add(user)
        db.session.flush()

        # Crear cliente
        client = Client(**client_data)
        db.session.add(client)
        db.session.flush()

        # Crear expediente
        case_file = CaseFile(
            client_id=client.id,
            status="BORRADOR",
            created_by=user.id,
        )
        db.session.add(case_file)
        db.session.commit()

        return case_file.id


class TestRiskService:
    """Tests para el servicio de calculo de riesgo."""

    @pytest.mark.parametrize(
        ("volumen_transacciones", "expected_score"),
        [
            ("HASTA_10000", 0),
            ("10001_50000", 5),
            ("50001_100000", 10),
            ("100001_500000", 15),
            ("MAS_500000", 20),
        ],
    )
    def test_volumen_transacciones_nuevos_rangos(self, volumen_transacciones, expected_score):
        assert VOLUME_SCORES[volumen_transacciones] == expected_score

        scores = calculate_risk_from_selections({
            "sector_economico": "BANCO_FINANCIERA_REGULADA",
            "jurisdiccion": "PANAMA",
            "pep_status": "NO_PEP",
            "volumen_transacciones": volumen_transacciones,
            "origen_fondos": "SALARIO_RELACION_LABORAL",
        })

        assert scores["volume_score"] == expected_score

    def test_riesgo_bajo(self, app, setup_case_file):
        """R = 5+5+5+5+5+0 = 25 -> BAJO (0-30)"""
        with app.app_context():
            risk_data = {
                "sector_score": 5,
                "jurisdiction_score": 5,
                "pep_score": 5,
                "volume_score": 5,
                "funds_origin_score": 5,
                "sanctions_score": 0,
            }
            assessment = calculate_risk(setup_case_file, risk_data)

            assert assessment.total_score == 25
            assert assessment.risk_level == "BAJO"
            assert assessment.calculation_aborted is False

    def test_riesgo_medio(self, app, setup_case_file):
        """R = 10+10+10+10+5+0 = 45 -> MEDIO (31-60)"""
        with app.app_context():
            risk_data = {
                "sector_score": 10,
                "jurisdiction_score": 10,
                "pep_score": 10,
                "volume_score": 10,
                "funds_origin_score": 5,
                "sanctions_score": 0,
            }
            assessment = calculate_risk(setup_case_file, risk_data)

            assert assessment.total_score == 45
            assert assessment.risk_level == "MEDIO"
            assert assessment.calculation_aborted is False

    def test_riesgo_alto(self, app, setup_case_file):
        """R = 15+15+15+15+5+0 = 65 -> ALTO (61-90)"""
        with app.app_context():
            risk_data = {
                "sector_score": 15,
                "jurisdiction_score": 15,
                "pep_score": 15,
                "volume_score": 15,
                "funds_origin_score": 5,
                "sanctions_score": 0,
            }
            assessment = calculate_risk(setup_case_file, risk_data)

            assert assessment.total_score == 65
            assert assessment.risk_level == "ALTO"
            assert assessment.calculation_aborted is False

    def test_riesgo_muy_alto(self, app, setup_case_file):
        """R = 20+20+20+20+20+5 = 105 -> MUY_ALTO (91+)"""
        with app.app_context():
            risk_data = {
                "sector_score": 20,
                "jurisdiction_score": 20,
                "pep_score": 20,
                "volume_score": 20,
                "funds_origin_score": 20,
                "sanctions_score": 5,
            }
            assessment = calculate_risk(setup_case_file, risk_data)

            assert assessment.total_score == 105
            assert assessment.risk_level == "MUY_ALTO"
            assert assessment.calculation_aborted is False

    def test_coincidencia_confirmada_aborta_calculo(self, app, setup_case_file):
        """
        CRITICO: Cuando L (sanctions_score) = 3 (COINCIDENCIA_CONFIRMADA),
        el calculo debe abortarse inmediatamente.

        R = S + J + P + V + O + L
        Si L = 3, entonces:
        - calculation_aborted = True
        - total_score = None
        - risk_level = None
        """
        with app.app_context():
            risk_data = {
                "sector_score": 20,
                "jurisdiction_score": 20,
                "pep_score": 20,
                "volume_score": 20,
                "funds_origin_score": 20,
                "sanctions_score": 3,  # COINCIDENCIA_CONFIRMADA
            }
            assessment = calculate_risk(setup_case_file, risk_data)

            assert assessment.calculation_aborted is True
            assert assessment.total_score is None
            assert assessment.risk_level is None

    def test_coincidencia_confirmada_no_calcula_resto(self, app, setup_case_file):
        """
        Verifica que cuando hay COINCIDENCIA_CONFIRMADA,
        los otros scores no se suman (el calculo se aborta antes).
        """
        with app.app_context():
            risk_data = {
                "sector_score": 20,
                "jurisdiction_score": 20,
                "pep_score": 20,
                "volume_score": 20,
                "funds_origin_score": 20,
                "sanctions_score": 3,
            }
            assessment = calculate_risk(setup_case_file, risk_data)

            # Verificar que los scores quedaron guardados
            assert assessment.sector_score == 20
            assert assessment.jurisdiction_score == 20
            assert assessment.pep_score == 20
            assert assessment.volume_score == 20
            assert assessment.funds_origin_score == 20
            assert assessment.sanctions_score == 3

            # Pero el total y nivel son None porque se abortó
            assert assessment.total_score is None
            assert assessment.risk_level is None
            assert assessment.calculation_aborted is True
