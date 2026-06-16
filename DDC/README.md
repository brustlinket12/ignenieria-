# DDC — Debida Diligencia Continua

> Sistema de gestión de expedientes para cumplimiento normativo AML/KYC bajo la Ley 23/2015 de Panamá.

---

## Stack Tecnológico

| Capa | Tecnología |
|------|----------------|
| **Backend** | Flask 3.0 + SQLAlchemy + SQLite |
| **Frontend** | React 19 + TypeScript + Vite |
| **Estilos** | Tailwind CSS v4 |
| **Formularios** | React Hook Form + Zod |
| **Routing** | React Router v7 |
| **HTTP** | Axios |
| **Serialización** | Marshmallow |
| **Testing** | pytest |

---

## Arquitectura

```
React SPA (Puerto 5173)
 → HTTP/JSON →
 Flask API (Puerto 5001)
                          →
                    SQLAlchemy → SQLite
```

**Regla fundamental**: el frontend solo muestra lo que el backend responde. El cálculo de riesgo, la derivación por sanciones y auditoría se ejecutan siempre en Flask.

---

## Roles Del Sistema

| Rol | Función |
|-----|---------|
| `ANALISTA` | Crea expedientes, calcula riesgo, sube documentos, finaliza |
| `OFICIAL_CUMPLIMIENTO` | Revisa expedientes `EN_REVISION`, aprueba, rechaza, pide corrección |
| `OFICIAL_AUDITORIA` | Solo lectura, no modifica, no ve borradores ni alertas |

**Filtros y visibilidad por rol:**

| Rol | Estados visibles |
|-----|------------------|
| `ANALISTA` | `BORRADOR`, `EN_REVISION`, `APROBADO`, `RECHAZADO` |
| `OFICIAL_CUMPLIMIENTO` | `EN_REVISION`, `REQUIERE_CORRECCION`, `APROBADO`, `RECHAZADO` |
| `OFICIAL_AUDITORIA` | `EN_REVISION`, `APROBADO`, `RECHAZADO` |

`OFICIAL_CUMPLIMIENTO` no ve `BORRADOR`. `OFICIAL_AUDITORIA` no ve `BORRADOR`, no ve `REQUIERE_CORRECCION` y no tiene sección de alertas.

---

## Modelo De Riesgo

**Fórmula:**

```
R = S + J + P + V + O + L
```

| Variable | Factor |
|----------|--------|
| `S` | Sector económico (0-30) |
| `J` | Jurisdicción (0-20) |
| `P` | PEP - Persona Expuesta Políticamente (0-20) |
| `V` | Volumen transaccional (0-20) |
| `O` | Origen de fondos (0-10) |
| `L` | Listas de sanciones (0 ó 3) |

**Rangos de riesgo:**

| Puntaje | Nivel |
|---------|-------|
| 0-30 | `BAJO` |
| 31-60 | `MEDIO` |
| 61-90 | `ALTO` |
| 91+ | `MUY_ALTO` |

**Flujo de aprobación según riesgo:**

| Nivel | Puntaje | Resultado al finalizar |
|-------|---------|------------------------|
| `BAJO` | 0-30 | Auto-aprobado, sin revisión |
| `MEDIO` | 31-60 | Pasa a `EN_REVISION` |
| `ALTO` | 61-90 | Pasa a `EN_REVISION` con alerta a `OFICIAL_CUMPLIMIENTO` |
| `MUY_ALTO` | 91+ | Pasa a `EN_REVISION` con alerta a `OFICIAL_CUMPLIMIENTO` |

**Regla crítica — Sanciones Confirmadas:**

> Si `L = COINCIDENCIA_CONFIRMADA` (score = 3), el expediente pasa a `EN_REVISION` con `blocked_by_sanctions = true` y alerta a `OFICIAL_CUMPLIMIENTO`.

**Alertas:** `OFICIAL_CUMPLIMIENTO` recibe alertas solo para riesgo `ALTO`, `MUY_ALTO` o sanciones confirmadas. `OFICIAL_AUDITORIA` no tiene sección de alertas. `ANALISTA` recibe notificación cuando su expediente cambia de estado.

---

## Estados Del Expediente

```
BORRADOR → EN_REVISION → APROBADO
                         → RECHAZADO
                         → REQUIERE_CORRECCION
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
| `auditoria@demo.com` | `password123` | OFICIAL_AUDITORIA |

---

## Endpoints API

| Método | Endpoint | Descripción |
|-----------|----------|-----------------|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/auth/login` | Login de usuario |
| `POST` | `/api/auth/logout` | Cerrar sesión |
| `GET` | `/api/me` | Usuario autenticado |
| `GET` | `/api/case-files` | Listar expedientes |
| `POST` | `/api/case-files` | Crear expediente |
| `GET` | `/api/case-files/:id` | Ver expediente |
| `PATCH` | `/api/case-files/:id` | Actualizar expediente |
| `POST` | `/api/case-files/:id/submit` | Enviar a revisión |
| `POST` | `/api/case-files/:id/risk-assessment` | Calcular riesgo + screening |
| `GET` | `/api/case-files/:id/documents` | Listar documentos |
| `POST` | `/api/case-files/:id/documents` | Subir documento real con `multipart/form-data` |
| `DELETE` | `/api/case-files/:id/documents/:document_id` | Eliminar documento |
| `POST` | `/api/case-files/:id/approve` | Aprobar expediente |
| `POST` | `/api/case-files/:id/reject` | Rechazar expediente |
| `POST` | `/api/case-files/:id/request-correction` | Solicitar corrección |
| `GET` | `/api/case-files/:id/audit-logs` | Historial de auditoría |
| `GET` | `/api/case-files/:id/alerts` | Alertas del expediente |
| `GET` | `/api/alerts` | Alertas no leídas |
| `PATCH` | `/api/alerts/:id/read` | Marcar alerta como leída |

Los documentos se suben como archivo real en `POST /api/case-files/:id/documents` usando `multipart/form-data`. Se almacenan en `uploads/case-files/:id/` y soportan PDF, PNG, JPG, DOC y XLS hasta 10MB.

El historial de auditoría se muestra en la UI como una línea de tiempo profesional, con etiquetas de eventos legibles en español y el JSON técnico colapsado por defecto.

---

## Estructura Del Proyecto

```
DDC/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── config.py            # Configuración por entorno
│   ├── extensions.py        # SQLAlchemy, Migrate, CORS
│   ├── models/              # Modelos SQLAlchemy
│   ├── routes/              # Blueprints API
│   ├── services/            # Lógica de dominio
│   ├── schemas/             # Marshmallow schemas
│   ├── repositories/        # Acceso a datos
│   ├── seed/                # Datos demo
│   ├── tests/               # Tests backend
│   ├── frontend/            # React app
├── instance/              # SQLite DB (ignorado por git)
├── run.py                  # Entry point
├── requirements.txt
├── package.json
```

---

## Troubleshooting

### `unable to open database file`
La carpeta `instance/` debe existir. Si no existe, creala:

```bash
mkdir instance
```

### Error de CORS al login
Verificá que `supports_credentials: True` esté configurado en `app/__init__.py`:

```python
cors.init_app(app, resources={r"/api/*": {"origins": "*", "supports_credentials": True}})
```

### Tailwind v4 — error de clipboard
Si aparece `Cannot read "clipboard"`, instalá el plugin PostCSS correcto:

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
Verificá que el servidor esté corriendo. En Windows:

```bash
cd DDC
.\venv\Scripts\activate
python run.py
```

---

## Notas De Seguridad

- **No subir al repo**: archivos `.sqlite`, `.env`, `node_modules/`, `instance/`, `__pycache__/`
- **No usar datos reales** en seeds o pruebas
- **La sesión es server-side** con `Flask-Session`. Las credenciales no se almacenan en el frontend como fuente de verdad
- **El motor de riesgo con derivación por sanciones es la regla más crítica** del sistema. Si falla, el sistema pierde su propósito regulatorio

---

## Formulario DDC — Flujo De4 Pasos

```
Paso 1: Datos del Cliente
  → Nombre, tipo/número de identificación, país

Paso 2: Perfil de Riesgo
  → S, J, P, V, O (variables de riesgo)
  → Backend consulta screening de sanciones mock
  → Si L = COINCIDENCIA_CONFIRMADA → EN_REVISION con blocked_by_sanctions=true y alerta

Paso 3: Documentos
  → Upload real de documentos PDF, PNG, JPG, DOC o XLS hasta 10MB

Paso 4: Revisión y Envío
  → Resumen completo
  → Enviar a revisión o guardar como borrador
```

---

## Pruebas De La Regla Crítica

Para verificar que el bypass por sanciones funciona:

1. Logueate como `analista@demo.com`
2. Creá un expediente con nombre **"Cliente Sancionado Demo"**
3. Completá el perfil de riesgo
4. Observá que el expediente queda **EN_REVISION** con `blocked_by_sanctions = true`
5. Logueate como `oficial@demo.com`
6. Revisá el expediente con alerta por sanciones confirmadas
7. Aprobá, rechazá o solicitá corrección según corresponda
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
      
* **El Rol de `OFICIAL_AUDITORIA`:** El informe original solo contemplaba operativamente al Oficial KYC y al Oficial de Cumplimiento. Se agregó este tercer rol técnico con permisos exclusivos de solo lectura (`Read-Only`) orientado al control inmutable de trazas y logs de auditoría, sin acceso a borradores, correcciones ni alertas.

---

## 2. Optimizaciones de Arquitectura (Lo que se MEJORÓ)

Estos componentes **ya estaban presentes o descritos en el informe**, pero su lógica presentaba conflictos regulatorios o vacíos operativos que fueron subsanados para su implementación real:

* **Sincronización de la Derivación por Sanciones (Caso de Uso CU-03):** * *En el Informe:* El CU-03 ya establecía correctamente que una coincidencia en listas de sanciones requería tratamiento especial.
    * *Modificaciones:* Se resolvió un conflicto con la nueva fórmula matemática. Si el backend detecta un positivo confirmado (`L = COINCIDENCIA_CONFIRMADA`), el expediente pasa a `EN_REVISION` con `blocked_by_sanctions = true` y alerta a `OFICIAL_CUMPLIMIENTO` para decisión formal.
* **Estructuración de la Matriz de Permisos (RBAC):**
    * *En el Informe:* Los roles de Oficial KYC y Cumplimiento ya operaban en las pantallas y flujos descritos.
    * *Modificaciones:* Se eliminaron las ambigüedades donde las funciones se mezclaban (como que el KYC aprobara casos de riesgo medio). Se estructuraron formalmente en una **Matriz de Control de Acceso Basado en Roles (RBAC)** en formato de tabla para validar tokens de usuario, dejando claro que `ANALISTA` *crea/edita/finaliza*, `OFICIAL_CUMPLIMIENTO` *aprueba/rechaza/solicita corrección* y `OFICIAL_AUDITORIA` solo consulta.
* **Ciclo de Vida del Expediente (Máquina de Estados Finita):**
    * *En el Informe:* Se usaban términos sueltos y desconectados como *"Verificación pendiente"* o *"Completado"*.
    * *Modificaciones:* Se estandarizó el pipeline del backend en una máquina de estados limpia y rígida para controlar los flujos de las peticiones HTTP de la API:
        $$\text{BORRADOR} \longrightarrow \text{EN\_REVISION} \longrightarrow \begin{cases} \text{APROBADO} \\ \text{RECHAZADO} \\ \text{REQUIERE\_CORRECCION} \end{cases}$$
* **Estandarización de Clasificaciones (Eliminación de Estados Huérfanos):**
    * *En el Informe:* El JSON de ejemplo provisto para el cliente real arrojaba un nivel de riesgo `"MEDIO_ALTO"`.
    * *Modificaciones:* Se eliminó este término por completo, ya que no existe en la matriz regulatoria de Panamá ni en los condicionales (`if/else`) del backend. Todo se mapea estrictamente a los 4 niveles oficiales basados en los umbrales de la fórmula.

---

## 3. Resumen de Enfoque Final

| Documento | Propósito en el Proyecto | Implementación Técnica |
| :--- | :--- | :--- |
| **Informe de DDC (PDF)** | Sustento Legal (Ley 23 de 2015), Diseño UX/UI (Campos y Layout) y Requerimientos Funcionales. | Guía para el Frontend, Validaciones de campos e interfaz de usuario. |
| **Especificación del Motor (Word / MD)** | Reglas de Negocio Matemáticas, Control de Acceso (RBAC) y Estados del Servidor. | Planos de Arquitectura para el Backend, API Endpoints y Base de Datos (MongoDB). |
