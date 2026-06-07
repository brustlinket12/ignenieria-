import hashlib
import random
import string
from datetime import datetime, timedelta, timezone

def random_hash():
    return hashlib.sha256(str(random.random()).encode()).hexdigest()

def random_id(prefix, length=4):
    return f"{prefix}-{''.join(random.choices(string.digits, k=length))}"

NOW = datetime.now(timezone.utc)

USUARIOS = {
    "OFICIAL_KYC": {"nombre": "Ana Martínez", "email": "ana.kyc@ddc.co", "rol": "OFICIAL_KYC"},
    "OFICIAL_CUMPLIMIENTO": {"nombre": "Carlos Vargas", "email": "carlos.cumplimiento@ddc.co", "rol": "OFICIAL_CUMPLIMIENTO"},
    "AUDITOR_INTERNO": {"nombre": "Sofía Reyes", "email": "sofia.auditor@ddc.co", "rol": "AUDITOR_INTERNO"},
}

CLIENTES = [
    {"id": "c-001", "nombre": "Inversiones Marítimas del Pacífico, S.A.", "ruc": "RUC-655-814-102839-2023", "tipo": "JURIDICA", "riesgo": "MEDIO_ALTO", "ultimaRevision": "2024-04-10", "proximaRevision": "2025-04-10", "estado": "DDC_VENCIDA", "esPEP": False, "uuid": "3fa85f64-5717-4562-b3fc-1a2b3c4d5e6f", "fechaVinculacion": "2020-03-15", "sancionado": False},
    {"id": "c-002", "nombre": "Carlos Méndez Herrera", "cedula": "8-234-5678", "tipo": "NATURAL", "riesgo": "BAJO", "ultimaRevision": "2024-11-15", "proximaRevision": "2026-11-15", "estado": "VIGENTE", "esPEP": False, "uuid": "4fa85f64-5717-4562-b3fc-2b3c4d5e6f7a", "fechaVinculacion": "2019-06-01", "sancionado": False},
    {"id": "c-003", "nombre": "Ricardo Fernández Aguirre", "cedula": "3-118-2045", "tipo": "PEP", "riesgo": "MUY_ALTO", "ultimaRevision": "2024-01-20", "proximaRevision": "2025-01-20", "estado": "DDC_VENCIDA", "esPEP": True, "uuid": "5fa85f64-5717-4562-b3fc-3c4d5e6f7a8b", "fechaVinculacion": "2018-11-20", "sancionado": False},
    {"id": "c-004", "nombre": "Logística Global Panama Corp.", "ruc": "RUC-123-456-789012-2021", "tipo": "JURIDICA", "riesgo": "ALTO", "ultimaRevision": "2025-03-01", "proximaRevision": "2026-03-01", "estado": "PROXIMA_A_VENCER", "esPEP": False, "uuid": "6fa85f64-5717-4562-b3fc-4d5e6f7a8b9c", "fechaVinculacion": "2021-01-10", "sancionado": False},
    {"id": "c-005", "nombre": "Ana Torres Villarreal", "cedula": "4-201-3311", "tipo": "NATURAL", "riesgo": "BAJO", "ultimaRevision": "2023-06-10", "proximaRevision": "2026-06-10", "estado": "VIGENTE", "esPEP": False, "uuid": "7fa85f64-5717-4562-b3fc-5e6f7a8b9c0d", "fechaVinculacion": "2022-05-30", "sancionado": False},
    {"id": "c-006", "nombre": "Cripto Assets International Inc.", "ruc": "RUC-890-123-456789-2022", "tipo": "JURIDICA", "riesgo": "MUY_ALTO", "ultimaRevision": "2025-02-14", "proximaRevision": "2026-02-14", "estado": "PENDIENTE_APROBACION", "esPEP": False, "uuid": "8fa85f64-5717-4562-b3fc-6f7a8b9c0d1e", "fechaVinculacion": "2022-08-12", "sancionado": False},
    {"id": "c-007", "nombre": "Mossack & Asociados, S.A.", "ruc": "RUC-001-002-000001-2010", "tipo": "JURIDICA", "riesgo": "MUY_ALTO", "ultimaRevision": None, "proximaRevision": None, "estado": "BLOQUEADO_SANCIONES", "esPEP": False, "uuid": "9fa85f64-5717-4562-b3fc-7a8b9c0d1e2f", "fechaVinculacion": "2010-04-05", "sancionado": True},
    {"id": "c-008", "nombre": "Transportes del Caribe, S.A.", "ruc": "RUC-321-654-987654-2019", "tipo": "JURIDICA", "riesgo": "MEDIO", "ultimaRevision": "2024-12-01", "proximaRevision": "2026-12-01", "estado": "VIGENTE", "esPEP": False, "uuid": "0fa85f64-5717-4562-b3fc-8b9c0d1e2f3a", "fechaVinculacion": "2019-09-22", "sancionado": False},
]

EXPEDIENTES_EN_COLA = [
    {
        "id": "exp-001",
        "clienteId": "c-006",
        "clienteNombre": "Cripto Assets International Inc.",
        "clienteRuc": "RUC-890-123-456789-2022",
        "nivelRiesgo": "MUY_ALTO",
        "esPEP": False,
        "oficialKYC": "Ana Martínez",
        "fechaEnvio": (NOW - timedelta(hours=36)).isoformat(),
        "comentarios": "",
    },
    {
        "id": "exp-002",
        "clienteId": "c-003",
        "clienteNombre": "Ricardo Fernández Aguirre",
        "clienteRuc": "3-118-2045",
        "nivelRiesgo": "MUY_ALTO",
        "esPEP": True,
        "oficialKYC": "Ana Martínez",
        "fechaEnvio": (NOW - timedelta(hours=80)).isoformat(),
        "comentarios": "",
    },
    {
        "id": "exp-003",
        "clienteId": "c-004",
        "clienteNombre": "Logística Global Panama Corp.",
        "clienteRuc": "RUC-123-456-789012-2021",
        "nivelRiesgo": "ALTO",
        "esPEP": False,
        "oficialKYC": "Ana Martínez",
        "fechaEnvio": (NOW - timedelta(hours=50)).isoformat(),
        "comentarios": "",
    },
]

AUDIT_LOG = []
for i in range(1, 21):
    acciones = ["CREATE", "UPDATE", "READ", "APPROVE", "REJECT", "EXPORT"]
    accion = random.choice(acciones)
    cliente = random.choice(CLIENTES)
    ts = (NOW - timedelta(hours=random.randint(1, 720), minutes=random.randint(0, 59))).isoformat()
    usuario = random.choice(list(USUARIOS.values()))
    ip = f"10.0.{random.randint(1, 254)}.{random.randint(1, 254)}"
    hash_val = random_hash()
    AUDIT_LOG.append({
        "id": i,
        "timestamp": ts,
        "usuarioId": f"usr-{random.randint(100, 999)}",
        "usuarioNombre": usuario["nombre"],
        "rol": usuario["rol"],
        "accion": accion,
        "entidad": f"Cliente {cliente['id']}",
        "clienteNombre": cliente["nombre"],
        "delta": f'{{"antes": null, "despues": "{accion.lower()}d"}}',
        "ip": ip,
        "hash": hash_val,
    })

HISTORIAL_MONITOREO = {}
for cliente in CLIENTES:
    if cliente["riesgo"] in ("ALTO", "MUY_ALTO", "MEDIO_ALTO") or cliente["esPEP"]:
        riesgos_posibles = ["BAJO", "MEDIO", "ALTO", "MUY_ALTO"]
        entradas = []
        for j in range(2):
            riesgo_anterior = random.choice(riesgos_posibles)
            riesgo_nuevo = random.choice(riesgos_posibles)
            ts = (NOW - timedelta(days=random.randint(30, 400))).isoformat()
            hash_firma = random_hash()
            entradas.append({
                "id": f"rev-{cliente['id']}-{j+1}",
                "fecha": ts,
                "riesgoAnterior": riesgo_anterior,
                "riesgoNuevo": riesgo_nuevo,
                "cambioDetectado": riesgo_anterior != riesgo_nuevo,
                "motivoCambio": "Actualización de perfil transaccional" if riesgo_anterior != riesgo_nuevo else "Sin cambios significativos",
                "oficial": "Ana Martínez",
                "estado": random.choice(["APROBADO", "APROBADO", "APROBADO", "DEVUELTO"]),
                "hashFirma": hash_firma,
            })
        HISTORIAL_MONITOREO[cliente["id"]] = entradas

NOTIFICACIONES = [
    {"id": "notif-001", "tipo": "CRITICA", "mensaje": "Coincidencia en lista de sanciones (OFAC/ONU/UE) detectada.", "cliente": "Mossack & Asociados, S.A.", "timestamp": (NOW - timedelta(hours=2)).isoformat(), "leida": False},
    {"id": "notif-002", "tipo": "ALTA", "mensaje": "Cliente PEP pendiente de aprobación > 72h.", "cliente": "Ricardo Fernández Aguirre", "timestamp": (NOW - timedelta(hours=76)).isoformat(), "leida": False},
    {"id": "notif-003", "tipo": "MEDIA", "mensaje": "DDC próxima a vencer en 30 días.", "cliente": "Logística Global Panama Corp.", "timestamp": (NOW - timedelta(hours=12)).isoformat(), "leida": False},
    {"id": "notif-004", "tipo": "INFO", "mensaje": "Borrador guardado automáticamente.", "cliente": "Inversiones Marítimas del Pacífico, S.A.", "timestamp": (NOW - timedelta(minutes=30)).isoformat(), "leida": True},
    {"id": "notif-005", "tipo": "MEDIA", "mensaje": "Documentación pendiente de revisión.", "cliente": "Cripto Assets International Inc.", "timestamp": (NOW - timedelta(hours=48)).isoformat(), "leida": False},
]

SECTORES_ECONOMICOS = [
    ("H5012", "Transporte Marítimo"),
    ("K6419", "Banca"),
    ("J6110", "Telecomunicaciones"),
    ("G4711", "Comercio"),
    ("V6420", "Criptomonedas"),
    ("I5510", "Hotelería"),
]

JURISDICCIONES = [
    ("PA", "Panamá"),
    ("US", "Estados Unidos"),
    ("KY", "Islas Caimán"),
    ("VG", "Islas Vírgenes Británicas"),
    ("CH", "Suiza"),
    ("CN", "China"),
]

ORIGENES_FONDOS = [
    "Actividades Comerciales",
    "Herencia",
    "Inversiones",
    "Salario",
    "Otro",
]

def calcular_riesgo(sector, jurisdiccion, es_pep, volumen, sancionado):
    score = 0
    if sector in ("V6420", "KY"):
        score += 40
    if sector == "K6419":
        score += 15
    if jurisdiccion in ("KY", "VG"):
        score += 30
    if es_pep:
        score += 35
    if volumen > 500000:
        score += 20
    elif volumen > 100000:
        score += 10
    if sancionado:
        score = 100

    if score >= 75:
        nivel = "MUY_ALTO"
    elif score >= 50:
        nivel = "ALTO"
    elif score >= 20:
        nivel = "MEDIO"
    else:
        nivel = "BAJO"

    return nivel, score

def get_proxima_revision(nivel):
    if nivel in ("MUY_ALTO", "ALTO"):
        return (NOW + timedelta(days=365)).strftime("%Y-%m-%d")
    elif nivel == "MEDIO":
        return (NOW + timedelta(days=730)).strftime("%Y-%m-%d")
    else:
        return (NOW + timedelta(days=1095)).strftime("%Y-%m-%d")
