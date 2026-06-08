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
# Evolución de Arquitectura: Del Informe de DDC a Producción (Motor de Riesgos)

Este documento detalla la transición, las nuevas reglas de negocio y las optimizaciones aplicadas al sistema de **Debida Diligencia Continua (DDC)**. Su objetivo es servir de puente entre el planteamiento conceptual del informe y la especificación técnica de producción necesaria para el desarrollo de la API y el backend.

---

## 1. Componentes 100% Nuevos (Lo que se AGREGÓ)

Estos elementos **no existían en absoluto** en el informe original y se introdujeron en esta etapa técnica para poder estructurar la base de datos y las condicionales del código:

* **La Ecuación Matemática del Riesgo ($R = S + J + P + V + O + L$):** El informe mencionaba que el sistema evaluaba el riesgo de manera automática, pero no incluía ninguna fórmula. En producción se definieron tablas de datos indexadas con asignaciones de peso exactas (puntos del 5 al 25) para automatizar el cálculo en el backend.
* **Umbrales Numéricos de Corte (Rangos de Riesgo):** Se crearon límites matemáticos cerrados para categorizar automáticamente el score resultante de la fórmula en variables limpias para el código, evitando caídas o excepciones:
    * **Bajo:** 0 - 30 puntos
    * **Medio:** 31 - 60 puntos
    * **Alto:** 61 - 90 puntos
    * **Muy Alto:** 91+ puntos
      
* **El Rol de "Auditor Interno":** El informe original solo contemplaba operativamente al Oficial KYC y al Oficial de Cumplimiento. Se agregó este tercer rol técnico con permisos exclusivos de solo lectura (`Read-Only`) orientado al control inmutable de trazas y logs de auditoría.

---

## 2. Optimizaciones de Arquitectura (Lo que se MEJORÓ)

Estos componentes **ya estaban presentes o descritos en el informe**, pero su lógica presentaba conflictos regulatorios o vacíos operativos que fueron subsanados para su implementación real:

* **Sincronización del Cortocircuito de Bloqueo (Caso de Uso CU-03):** * *En el Informe:* El CU-03 ya establecía correctamente que una coincidencia en listas de sanciones bloqueaba el Paso 1 del formulario.
    * *Modificaciones:* Se resolvió un conflicto con la nueva fórmula matemática. Si el backend detecta un positivo confirmado (`L = COINCIDENCIA_CONFIRMADA`), se dispara un *short-circuit* (bypass) que deniega el negocio de inmediato, aborta el flujo y pasa el expediente a `RECHAZADO`, impidiendo que la fórmula sume puntos en un proceso que ya está legalmente muerto.
* **Estructuración de la Matriz de Permisos (RBAC):**
    * *En el Informe:* Los roles de Oficial KYC y Cumplimiento ya operaban en las pantallas y flujos descritos.
    * *Modificaciones:* Se eliminaron las ambigüedades donde las funciones se mezclaban (como que el KYC aprobara casos de riesgo medio). Se estructuraron formalmente en una **Matriz de Control de Acceso Basado en Roles (RBAC)** en formato de tabla para validar tokens de usuario, dejando claro que KYC *crea/edita* y Cumplimiento es el único que *aprueba/rechaza*.
* **Ciclo de Vida del Expediente (Máquina de Estados Finita):**
    * *En el Informe:* Se usaban términos sueltos y desconectados como *"Verificación pendiente"* o *"Completado"*.
    * *Modificaciones:* Se estandarizó el pipeline del backend en una máquina de estados limpia y rígida para controlar los flujos de las peticiones HTTP de la API:
        $$\text{BORRADOR} \longrightarrow \text{EN\_REVISION} \longrightarrow \text{PENDIENTE\_APROBACION} \longrightarrow \begin{cases} \text{APROBADO} \\ \text{RECHAZADO} \end{cases}$$
* **Estandarización de Clasificaciones (Eliminación de Estados Huérfanos):**
    * *En el Informe:* El JSON de ejemplo provisto para el cliente real arrojaba un nivel de riesgo `"MEDIO_ALTO"`.
    * *Modificaciones:* Se eliminó este término por completo, ya que no existe en la matriz regulatoria de Panamá ni en los condicionales (`if/else`) del backend. Todo se mapea estrictamente a los 4 niveles oficiales basados en los umbrales de la fórmula.

---

## 3. Resumen de Enfoque Final

| Documento | Propósito en el Proyecto | Implementación Técnica |
| :--- | :--- | :--- |
| **Informe de DDC (PDF)** | Sustento Legal (Ley 23 de 2015), Diseño UX/UI (Campos y Layout) y Requerimientos Funcionales. | Guía para el Frontend, Validaciones de campos e interfaz de usuario. |
| **Especificación del Motor (Word / MD)** | Reglas de Negocio Matemáticas, Control de Acceso (RBAC) y Estados del Servidor. | Planos de Arquitectura para el Backend, API Endpoints y Base de Datos (MongoDB). |
