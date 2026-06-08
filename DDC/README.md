# DDC — Debida Diligencia Continua

> Sistema de gesti\u00f3n de expedientes para cumplimiento normativo AML/KYC bajo la Ley 23/2015 de Panam\u00e1.

---

## Stack Tecnol\u00f3gico

| Capa | Tecnolog\u00eda |
|------|----------------|
| **Backend** | Flask 3.0 + SQLAlchemy + SQLite |
| **Frontend** | React 19 + TypeScript + Vite |
| **Estilos** | Tailwind CSS v4 |
| **Formularios** | React Hook Form + Zod |
| **Routing** | React Router v7 |
| **HTTP** | Axios |
| **Serializaci\u00f3n** | Marshmallow |
| **Testing** | pytest |

---

## Arquitectura

```
React SPA (Puerto 5173)
 \u2192 HTTP/JSON \u2192
 Flask API (Puerto 5001)
                          \u2192
                    SQLAlchemy \u2192 SQLite
```

**Regla fundamental**: el frontend solo muestra lo que el backend responde. El c\u00e1lculo de riesgo, bloqueo por sanciones y auditor\u00eda se ejecutan siempre en Flask.

---

## Roles Del Sistema

| Rol | Descripci\u00f3n | Permisos |
|-----|-----------------|----------|
| `ANALISTA` | Carga y preparaci\u00f3n de expedientes | Crear, editar, enviar a revisi\u00f3n |
| `OFICIAL_CUMPLIMIENTO` | Control y decisi\u00f3n | Aprobar, rechazar, desbloquear falso positivo |
| `ADMIN` | Administraci\u00f3n total | Todas las funcionalidades |

---

## Modelo De Riesgo

**F\u00f3rmula:**

```
R = S + J + P + V + O + L
```

| Variable | Factor |
|----------|--------|
| `S` | Sector econ\u00f3mico (0-30) |
| `J` | Jurisdicci\u00f3n (0-20) |
| `P` | PEP - Persona Expuesta Pol\u00edticamente (0-20) |
| `V` | Volumen transaccional (0-20) |
| `O` | Origen de fondos (0-10) |
| `L` | Listas de sanciones (0 \u00f3 3) |

**Rangos de riesgo:**

| Puntaje | Nivel |
|---------|-------|
| 0-30 | `BAJO` |
| 31-60 | `MEDIO` |
| 61-90 | `ALTO` |
| 91+ | `MUY_ALTO` |

**Regla cr\u00edtica — Bypass de Bloqueo Inmediato:**

> Si `L = COINCIDENCIA_CONFIRMADA` (score = 3), el c\u00e1lculo se aborta, `total_score = null`, `risk_level = null`, y el expediente se bloquea autom\u00e1ticamente. Solo el Oficial de Cumplimiento puede desbloquearlo con justificaci\u00f3n.

---

## Estados Del Expediente

```
BORRADOR \u2192 EN_REVISION \u2192 APROBADO
                          \u2192 RECHAZADO
                          \u2192 BLOQUEADO_POR_SANCIONES \u2192 DESBLOQUEADO_FALSO_POSITIVO
```

---

## Getting Started

### Requisitos Previos

- Python 3.10+
- Node.js 18+

### 1. Backend

```bash
cd DDC

# Crear entorno virtual
python -m venv venv
.\venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Poblar datos demo
flask seed-demo

# Ejecutar servidor
python run.py
```

Backend disponible en: **http://localhost:5001**

### 2. Frontend

```bash
cd DDC/frontend

# Instalar dependencias
npm install

# Ejecutar en desarrollo
npm run dev
```

Frontend disponible en: **http://localhost:5173**

### 3. Tests

```bash
cd DDC
.\venv\Scripts\activate
pytest app/tests/ -v
```

---

## Datos Demo

| Email | Password | Rol |
|-------|----------|-----|
| `analista@demo.com` | `password123` | ANALISTA |
| `oficial@demo.com` | `password123` | OFICIAL_CUMPLIMIENTO |
| `admin@demo.com` | `password123` | ADMIN |

---

## Endpoints API

| M\u00e9todo | Endpoint | Descripci\u00f3n |
|-----------|----------|-----------------|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/auth/login` | Login de usuario |
| `POST` | `/api/auth/logout` | Cerrar sesi\u00f3n |
| `GET` | `/api/me` | Usuario autenticado |
| `GET` | `/api/case-files` | Listar expedientes |
| `POST` | `/api/case-files` | Crear expediente |
| `GET` | `/api/case-files/:id` | Ver expediente |
| `PATCH` | `/api/case-files/:id` | Actualizar expediente |
| `POST` | `/api/case-files/:id/submit` | Enviar a revisi\u00f3n |
| `POST` | `/api/case-files/:id/risk-assessment` | Calcular riesgo + screening |
| `POST` | `/api/case-files/:id/approve` | Aprobar expediente |
| `POST` | `/api/case-files/:id/reject` | Rechazar expediente |
| `POST` | `/api/case-files/:id/unblock` | Desbloquear falso positivo |
| `GET` | `/api/case-files/:id/audit-logs` | Historial de auditor\u00eda |
| `GET` | `/api/case-files/:id/alerts` | Alertas del expediente |
| `GET` | `/api/alerts` | Alertas no le\u00eddas |
| `PATCH` | `/api/alerts/:id/read` | Marcar alerta como le\u00edda |

---

## Estructura Del Proyecto

```
DDC/
\u251c\u2500\u2500 app/
\u2502   \u251c\u2500\u2500 __init__.py          # Flask app factory
\u2502   \u251c\u2500\u2500 config.py            # Configuraci\u00f3n por entorno
\u2502   \u251c\u2500\u2500 extensions.py        # SQLAlchemy, Migrate, CORS
\u2502   \u251c\u2500\u2500 models/              # Modelos SQLAlchemy
\u2502   \u251c\u2500\u2500 routes/              # Blueprints API
\u2502   \u251c\u2500\u2500 services/            # L\u00f3gica de dominio
\u2502   \u251c\u2500\u2500 schemas/             # Marshmallow schemas
\u2502   \u251c\u2500\u2500 repositories/        # Acceso a datos
\u2502   \u251c\u2500\u2500 seed/                # Datos demo
\u2502   \u251c\u2500\u2500 tests/               # Tests backend
\u2502   \u251c\u2500\u2500 frontend/            # React app
\u251c\u2500\u2500 instance/              # SQLite DB (ignorado por git)
\u251c\u2500\u2500 run.py                  # Entry point
\u251c\u2500\u2500 requirements.txt
\u251c\u2500\u2500 package.json
```

---

## Troubleshooting

### `unable to open database file`
La carpeta `instance/` debe existir. Si no existe, creala:

```bash
mkdir instance
```

### Error de CORS al login
Verific\u00e1 que `supports_credentials: True` est\u00e9 configurado en `app/__init__.py`:

```python
cors.init_app(app, resources={r"/api/*": {"origins": "*", "supports_credentials": True}})
```

### Tailwind v4 — error de clipboard
Si aparece `Cannot read "clipboard"`, instal\u00e1 el plugin PostCSS correcto:

```bash
cd DDC/frontend
npm install -D @tailwindcss/postcss
```

Y en `postcss.config.js`:

```js
export default {
  plugins: {
    "@tailwindcss/postcss": {},
  },
}
```

### Backend no responde en puerto 5001
Verific\u00e1 que el servidor est\u00e9 corriendo. En Windows:

```bash
cd DDC
.\venv\Scripts\activate
python run.py
```

---

## Notas De Seguridad

- **No subir al repo**: archivos `.sqlite`, `.env`, `node_modules/`, `instance/`, `__pycache__/`
- **No usar datos reales** en seeds o pruebas
- **La sesi\u00f3n es server-side** con `Flask-Session`. Las credenciales no se almacenan en el frontend como fuente de verdad
- **El motor de riesgo con bypass por sanciones es la regla m\u00e1s cr\u00edtica** del sistema. Si falla, el sistema pierde su prop\u00f3sito regulatorio

---

## Formulario DDC — Flujo De4 Pasos

```
Paso 1: Datos del Cliente
  \u2192 Nombre, tipo/n\u00famero de identificaci\u00f3n, pa\u00eds

Paso 2: Perfil de Riesgo
  \u2192 S, J, P, V, O (variables de riesgo)
  \u2192 Backend consulta screening de sanciones mock
  \u2192 Si L = COINCIDENCIA_CONFIRMADA \u2192 BLOQUEO INMEDIATO

Paso 3: Documentos
  \u2192 Declaraci\u00f3n de documentos (MVP - upload real en desarrollo)

Paso 4: Revisi\u00f3n y Env\u00edo
  \u2192 Resumen completo
  \u2192 Enviar a revisi\u00f3n o guardar como borrador
```

---

## Pruebas De La Regla Cr\u00edtica

Para verificar que el bypass por sanciones funciona:

1. Logueate como `analista@demo.com`
2. Cre\u00e1 un expediente con nombre **"Cliente Sancionado Demo"**
3. Complet\u00e1 el perfil de riesgo
4. Observ\u00e1 que el expediente queda **BLOQUEADO_POR_SANCIONES**
5. Logueate como `oficial@demo.com`
6. Revis\u00e1 el expediente bloqueado
7. Desbloquealo con justificaci\u00f3n de falso positivo
