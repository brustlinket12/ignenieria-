from app.models.risk_assessment import RiskAssessment
from app.models.case_file import CaseFile
from app.extensions import db


def calculate_risk(case_file_id, risk_data):
    """
    Calcula el nivel de riesgo para un expediente.

    Formula: R = S + J + P + V + O + L
    donde:
    - S = sector_score
    - J = jurisdiction_score
    - P = pep_score
    - V = volume_score
    - O = funds_origin_score
    - L = sanctions_score

    Rangos:
    - BAJO: 0-30
    - MEDIO: 31-60
    - ALTO: 61-90
    - MUY_ALTO: 91+

    CRITICO: Si L (sanctions_score) == COINCIDENCIA_CONFIRMADA (3):
    - calculation_aborted = True
    - total_score = None
    - risk_level = None
    - El expediente debe ser bloqueado por el caller
    """
    case_file = CaseFile.query.get(case_file_id)
    if not case_file:
        raise ValueError(f"Expediente {case_file_id} no encontrado")

    # Crear o actualizar assessment
    assessment = RiskAssessment.query.filter_by(case_file_id=case_file_id).first()
    if not assessment:
        assessment = RiskAssessment(case_file_id=case_file_id)
        db.session.add(assessment)

    assessment.sector_score = risk_data.get("sector_score", 0)
    assessment.jurisdiction_score = risk_data.get("jurisdiction_score", 0)
    assessment.pep_score = risk_data.get("pep_score", 0)
    assessment.volume_score = risk_data.get("volume_score", 0)
    assessment.funds_origin_score = risk_data.get("funds_origin_score", 0)
    assessment.sanctions_score = risk_data.get("sanctions_score", 0)

    # REGLA CRITICA: Si sanctions_score es COINCIDENCIA_CONFIRMADA (3), abortar
    if assessment.sanctions_score == 3:  # COINCIDENCIA_CONFIRMADA
        assessment.calculation_aborted = True
        assessment.total_score = None
        assessment.risk_level = None
        db.session.commit()
        return assessment

    # Calcular total
    total = (
        assessment.sector_score
        + assessment.jurisdiction_score
        + assessment.pep_score
        + assessment.volume_score
        + assessment.funds_origin_score
        + assessment.sanctions_score
    )

    assessment.total_score = total
    assessment.calculation_aborted = False
    assessment.risk_level = assessment.calculate_risk_level(total)
    db.session.commit()

    return assessment