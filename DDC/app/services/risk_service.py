from app.models.risk_assessment import RiskAssessment
from app.models.case_file import CaseFile
from app.extensions import db


# =============================================================================
# MAPEOS OFICIALES SEGUN PRD - Ley 23/2015 Panama
# =============================================================================

# Sector Economico (S)
SECTOR_SCORES = {
    "BANCO_FINANCIERA_REGULADA": 5,
    "FIDUCIARIA_CASA_VALORES": 10,
    "COMERCIO_GENERAL": 10,
    "CONSTRUCCION": 15,
    "BIENES_RAICES_VEHICULOS_EMPENO_METALES": 20,
    "CASINOS_JUEGOS_AZAR": 25,
    "OTRO_SECTOR": 10,
}

# Jurisdiccion / Pais (J)
JURISDICTION_SCORES = {
    # Nivel Bajo
    "PANAMA": 5,
    "COSTA_RICA": 5,
    "EEUU": 5,
    "CANADA": 5,
    "ESPANA": 5,
    # Nivel Medio
    "COLOMBIA": 10,
    "MEXICO": 10,
    "BRASIL": 10,
    "ARGENTINA": 10,
    "PERU": 10,
    # Nivel Alto
    "VENEZUELA": 15,
    "HAITI": 15,
    # Nivel Muy Alto
    "IRAN": 20,
    "COREA_DEL_NORTE": 20,
    # Cualquier otro pais
    "OTRO_PAIS": 5,
}

# PEP - Persona Expuesta Politicamente (P)
PEP_SCORES = {
    "NO_PEP": 0,
    "PEP_NACIONAL": 10,
    "PEP_EXTRANJERO": 20,
    "RELACIONADO_PEP": 15,
}

# Volumen Transacciones (V)
VOLUME_SCORES = {
    "BAJO": 5,
    "MEDIO": 10,
    "ALTO": 20,
}

# Origen de Fondos (O)
FUNDS_ORIGIN_SCORES = {
    "SALARIO_RELACION_LABORAL": 0,
    "ACTIVIDAD_COMERCIAL_DECLARADA": 5,
    "INVERSIONES_PATRIMONIO": 5,
    "TERCEROS": 10,
    "NO_JUSTIFICADO": 10,
}

# =============================================================================
# FUNCIONES DE CALCULO
# =============================================================================

def get_score(value, score_map, default=0):
    """Obtiene el score de un mapa, devuelve default si no existe."""
    return score_map.get(value, default)


def calculate_risk_from_selections(selections):
    """
    Convierte selecciones semanticas del formulario a scores.
    selections = {
        "sector_economico": "CASINOS_JUEGOS_AZAR",
        "jurisdiccion": "PANAMA",
        "pep_status": "NO_PEP",
        "volumen_transacciones": "ALTO",
        "origen_fondos": "ACTIVIDAD_COMERCIAL_DECLARADA",
    }
    """
    s = get_score(selections.get("sector_economico"), SECTOR_SCORES)
    j = get_score(selections.get("jurisdiccion"), JURISDICTION_SCORES)
    p = get_score(selections.get("pep_status"), PEP_SCORES)
    v = get_score(selections.get("volumen_transacciones"), VOLUME_SCORES)
    o = get_score(selections.get("origen_fondos"), FUNDS_ORIGIN_SCORES)

    return {
        "sector_score": s,
        "jurisdiction_score": j,
        "pep_score": p,
        "volume_score": v,
        "funds_origin_score": o,
    }


def calculate_risk(case_file_id, risk_data):
    """
    Calcula el nivel de riesgo para un expediente.

    Recibe datos semanticos del formulario y calcula scores automaticamente.

    Formula: R = S + J + P + V + O + L

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

    # Guardar selecciones semanticas
    assessment.sector_economico = risk_data.get("sector_economico")
    assessment.jurisdiccion = risk_data.get("jurisdiccion")
    assessment.pep_status = risk_data.get("pep_status")
    assessment.volumen_transacciones = risk_data.get("volumen_transacciones")
    assessment.origen_fondos = risk_data.get("origen_fondos")

    # Si vienen scores directos (backward compatibility), usarlos
    # Si vienen selecciones semanticas, calcular scores
    if risk_data.get("sector_score") is not None:
        assessment.sector_score = risk_data.get("sector_score", 0)
        assessment.jurisdiction_score = risk_data.get("jurisdiction_score", 0)
        assessment.pep_score = risk_data.get("pep_score", 0)
        assessment.volume_score = risk_data.get("volume_score", 0)
        assessment.funds_origin_score = risk_data.get("funds_origin_score", 0)
    else:
        # Calcular desde selecciones semanticas
        scores = calculate_risk_from_selections({
            "sector_economico": assessment.sector_economico,
            "jurisdiccion": assessment.jurisdiccion,
            "pep_status": assessment.pep_status,
            "volumen_transacciones": assessment.volumen_transacciones,
            "origen_fondos": assessment.origen_fondos,
        })
        assessment.sector_score = scores["sector_score"]
        assessment.jurisdiction_score = scores["jurisdiction_score"]
        assessment.pep_score = scores["pep_score"]
        assessment.volume_score = scores["volume_score"]
        assessment.funds_origin_score = scores["funds_origin_score"]

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