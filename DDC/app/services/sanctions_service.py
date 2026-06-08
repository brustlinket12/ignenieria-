from app.models.sanctions_screening import SanctionsScreening
from app.models.case_file import CaseFile
from app.extensions import db
import json


def screen_name(case_file_id, name):
    """
    Mock de verificacion de sanciones.

    Reglas:
    - "SANCIONADO" en nombre -> COINCIDENCIA_CONFIRMADA (3)
    - "SIMILAR" en nombre -> COINCIDENCIA_PARCIAL (2)
    - otro -> SIN_COINCIDENCIA (1)

    Retorna el resultado y lo guarda en la BD.
    """
    name_upper = name.upper()

    if "SANCIONADO" in name_upper:
        result = "COINCIDENCIA_CONFIRMADA"
        matched_name = name
        matched_list = "LISTA_BLOQUEO_DEMO"
        raw_response = json.dumps({
            "match": True,
            "list": "LISTA_BLOQUEO_DEMO",
            "score": 100,
            "entity": name
        })
    elif "SIMILAR" in name_upper:
        result = "COINCIDENCIA_PARCIAL"
        matched_name = name
        matched_list = "LISTA_BLOQUEO_DEMO"
        raw_response = json.dumps({
            "match": True,
            "list": "LISTA_BLOQUEO_DEMO",
            "score": 75,
            "entity": name
        })
    else:
        result = "SIN_COINCIDENCIA"
        matched_name = None
        matched_list = None
        raw_response = json.dumps({
            "match": False,
            "lists_checked": ["LISTA_BLOQUEO_DEMO", "OFAC", "UN"],
            "entity": name
        })

    screening = SanctionsScreening(
        case_file_id=case_file_id,
        provider="MOCK_PROVIDER",
        result=result,
        matched_name=matched_name,
        matched_list=matched_list,
        raw_response=raw_response,
    )
    db.session.add(screening)
    db.session.commit()

    return screening