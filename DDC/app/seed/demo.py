from datetime import datetime, timedelta
import click
from app.models.user import User
from app.models.client import Client
from app.models.case_file import CaseFile
from app.models.risk_assessment import RiskAssessment
from app.models.sanctions_screening import SanctionsScreening
from app.extensions import db


def seed_demo():
    """Pobla la base de datos con datos de demostración."""

    # Limpiar datos existentes
    User.query.delete()
    Client.query.delete()
    CaseFile.query.delete()
    RiskAssessment.query.delete()
    SanctionsScreening.query.delete()
    db.session.commit()

    # Usuarios demo
    users_data = [
        {"email": "analista@demo.com", "password": "password123", "name": "Analista Demo", "role": "ANALISTA"},
        {"email": "oficial@demo.com", "password": "password123", "name": "Oficial Cumplimiento Demo", "role": "OFICIAL_CUMPLIMIENTO"},
        {"email": "auditoria@demo.com", "password": "password123", "name": "Oficial Auditoria Demo", "role": "OFICIAL_AUDITORIA"},
    ]

    users = {}
    for u_data in users_data:
        user = User(
            email=u_data["email"],
            name=u_data["name"],
            role=u_data["role"],
        )
        user.set_password(u_data["password"])
        db.session.add(user)
        db.session.flush()
        users[u_data["role"]] = user

    db.session.commit()

    # Clientes demo
    clients_data = [
        {"name": "Cliente Normal Demo", "id_type": "DNI", "id_number": "12345678", "country": "Argentina"},
        {"name": "Cliente Similar Demo", "id_type": "PASAPORTE", "id_number": "AB123456", "country": "Uruguay"},
        {"name": "Cliente Sancionado Demo", "id_type": "CEDULA", "id_number": "87654321", "country": "Brasil"},
    ]

    clients = []
    for c_data in clients_data:
        client = Client(**c_data)
        db.session.add(client)
        db.session.flush()
        clients.append(client)

    db.session.commit()

    # Expedientes demo
    now = datetime.utcnow()

    # Expediente 1: Normal en BORRADOR
    case1 = CaseFile(
        client_id=clients[0].id,
        status="BORRADOR",
        current_step=1,
        blocked_by_sanctions=False,
        created_by=users["ANALISTA"].id,
        created_at=now - timedelta(days=5),
    )
    db.session.add(case1)

    # Expediente 2: Alto riesgo en EN_REVISION
    case2 = CaseFile(
        client_id=clients[1].id,
        status="EN_REVISION",
        current_step=4,
        blocked_by_sanctions=False,
        created_by=users["ANALISTA"].id,
        submitted_at=now - timedelta(days=2),
        created_at=now - timedelta(days=10),
    )
    db.session.add(case2)

    # Crear screening para case2
    screening2 = SanctionsScreening(
        case_file_id=2,  # Se asignará después
        provider="MOCK_PROVIDER",
        result="COINCIDENCIA_PARCIAL",
        matched_name=clients[1].name,
        matched_list="LISTA_BLOQUEO_DEMO",
    )

    # Expediente 3: Sancionado en EN_REVISION con flag de sanciones
    case3 = CaseFile(
        client_id=clients[2].id,
        status="EN_REVISION",
        current_step=2,
        blocked_by_sanctions=True,
        created_by=users["ANALISTA"].id,
        submitted_at=now - timedelta(days=1),
        created_at=now - timedelta(days=7),
    )
    db.session.add(case3)

    db.session.flush()

    # Ajustar screening con case_file_id real
    screening2.case_file_id = case2.id
    db.session.add(screening2)

    # Risk assessments
    risk1 = RiskAssessment(
        case_file_id=case1.id,
        sector_score=10,
        jurisdiction_score=5,
        pep_score=0,
        volume_score=15,
        funds_origin_score=5,
        sanctions_score=0,
        total_score=35,
        risk_level="MEDIO",
        calculation_aborted=False,
    )
    db.session.add(risk1)

    risk2 = RiskAssessment(
        case_file_id=case2.id,
        sector_score=20,
        jurisdiction_score=15,
        pep_score=20,
        volume_score=25,
        funds_origin_score=10,
        sanctions_score=1,
        total_score=91,
        risk_level="MUY_ALTO",
        calculation_aborted=False,
    )
    db.session.add(risk2)

    # Para case3, assessment abortado
    risk3 = RiskAssessment(
        case_file_id=case3.id,
        sector_score=20,
        jurisdiction_score=15,
        pep_score=20,
        volume_score=25,
        funds_origin_score=10,
        sanctions_score=3,
        total_score=None,
        risk_level=None,
        calculation_aborted=True,
    )
    db.session.add(risk3)

    db.session.commit()

    print("Datos demo creados exitosamente!")
    print("Usuarios:")
    print("  - analista@demo.com / password123 (ANALISTA)")
    print("  - oficial@demo.com / password123 (OFICIAL_CUMPLIMIENTO)")
    print("  - auditoria@demo.com / password123 (OFICIAL_AUDITORIA)")
    print("\nExpedientes:")
    print(f"  - Expediente ID 1: Normal, BORRADOR")
    print(f"  - Expediente ID 2: Alto riesgo (MUY_ALTO), EN_REVISION")
    print(f"  - Expediente ID 3: EN_REVISION con coincidencia en sanciones")


@click.command("seed-demo")
def seed_demo_command():
    """Comando Flask para ejecutar seed-demo."""
    seed_demo()
