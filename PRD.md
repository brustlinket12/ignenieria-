# PRD: Formulario Web de Debida Diligencia Continua (DDC)

**Versión:** 1.1.0  
**Fecha:** 7 de junio de 2026  
**Estado:** Borrador Final  
**Área:** Ingeniería de Software - Cumplimiento Regulatorio  
**Norma base:** Ley 23 de 27 de abril de 2015 (Panamá) - Prevención de Blanqueo de Capitales  
**Integrantes:** Yireikis Abrego, Christian Dutary, Jose Avila  

## 1. Resumen Ejecutivo

El Formulario Web de Debida Diligencia Continua (DDC) es una solución digital para que los sujetos obligados en Panamá cumplan con la Ley 23/2015. Automatiza la identificación, evaluación de riesgo, documentación y aprobación de clientes, con validaciones en tiempo real, cifrado AES-256, auditoría inmutable y alertas automáticas.

**Objetivos clave:**
- Garantizar 100% cumplimiento y reducir riesgo de sanciones (hasta USD 1M).
- Reducir tiempo de actualización KYC en ≥70%.
- Proporcionar trazabilidad completa y retención de 5 años.

El sistema usa un flujo de 4 pasos con motor de riesgo basado en fórmula ponderada, incluyendo una regla crítica de bloqueo inmediato por sanciones.

## 2. Definición del Problema y Objetivos

(Se mantiene igual al PRD anterior)

## 3. Motor de Cálculo de Riesgo (Prioritario)

**Fórmula base:**  
**R = S + J + P + V + O + L**

### Tablas de Puntaje

**Sector Económico (S)**  
| Actividad económica                          | Puntaje |
|----------------------------------------------|---------|
| Banco / Empresa financiera regulada          | 5       |
| Fiduciaria / Casa de valores                 | 10      |
| Comercio general / Construcción              | 10 / 15 |
| Bienes raíces / Vehículos / Empeño / Metales / Piedras | 20 |
| Casinos y juegos de azar                     | 25      |
| **Cualquier otro sector no listado**         | **10**  |

**Jurisdicción (J)**  
| País / Categoría                             | Nivel     | Puntos |
|----------------------------------------------|-----------|--------|
| Panamá, Costa Rica, EE.UU., Canadá, España   | Bajo      | 5      |
| Colombia, México, Brasil, Argentina, Perú    | Medio     | 10     |
| Venezuela, Haití                             | Alto      | 15     |
| Irán, Corea del Norte                        | Muy Alto  | 20     |
| **Cualquier otro país**                      | -         | **5**  |
| **Cualquier otra jurisdicción de lista estándar** | -    | **5**  |

**PEP (P)**, **Volumen (V)**, **Origen de Fondos (O)** y **Listas de Sanciones (L)** se mantienen según la versión anterior.

**Rangos de Riesgo Final**  
| Puntaje Total | Nivel de Riesgo |
|---------------|-----------------|
| 0 - 30        | **Bajo**        |
| 31 - 60       | **Medio**       |
| 61 - 90       | **Alto**        |
| 91+           | **Muy Alto**    |

### Regla de Negocio Crítica: Bypass de Bloqueo Inmediato por Listas de Sanciones

> **Si `L = COINCIDENCIA_CONFIRMADA`, el sistema debe activar un flag de bloqueo inmediato (`bloqueoSanciones = true`), abortar el cálculo completo de la fórmula R y denegar la transacción / aprobación del expediente, sin importar el puntaje resultante de las otras variables (S + J + P + V + O).**

**Comportamiento esperado:**
- Se genera una alerta CRÍTICA inmediata.
- El formulario se bloquea en el Paso 1 o 2.
- El expediente pasa a estado `BLOQUEADO_POR_SANCIONES`.
- Solo el Oficial de Cumplimiento (o rol superior) puede revisar, justificar como falso positivo y desbloquear.
- Todo el evento queda registrado en el log de auditoría inmutable.

Esta regla tiene precedencia absoluta sobre el cálculo numérico y responde a las mejores prácticas regulatorias de la Intendencia de Supervisión y Regulación de Sujetos Obligados y Superintendencia de Bancos de Panamá.

## 4. Diseño del Producto

(Se mantiene igual, con referencia al motor actualizado)

## 5. Requisitos

### Requisitos Funcionales (destacados)
- **RF-03** Integración con API OFAC, ONU y UE → debe retornar estado `COINCIDENCIA_CONFIRMADA` cuando corresponda.
- **RF-NUEVO** Motor de riesgo debe implementar la regla de Bypass de Bloqueo Inmediato (precedencia máxima).

### Flujo de Estados del Expediente (actualizado)