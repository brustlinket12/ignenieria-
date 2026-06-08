# AGENTS.md - Sistema DDC

## Reglas de Implementation

1. **API Flask responde JSON, no HTML**
2. **Frontend NO calcula riesgo ni decide bloqueo** - solo muestra lo que backend responde
3. **El motor de riesgo con bypass por sanciones es la regla m\u00e1s cr\u00edtica** - debe estar cubierta por tests
4. **No commitees archivos**: .sqlite, .env, node_modules/, __pycache__/
5. **Mantener todo en espa\u00f1ol** los archivos del proyecto

## Reglas de Orchestration

- **NO hacer trabajo inline** - siempre delegar a sub-agentes
- **Preferir delegate sobre task** para trabajo async
- **El orquestador solo lee**: git status/log, engram results, todo state
- **"Es peque\u00f1o" no es raz\u00f3n para saltarse delegaci\u00f3n**

## SDD Phases

| Phase | Reads | Writes |
|-------|-------|--------|
| sdd-explore | Nothing | explore |
| sdd-propose | Exploration (optional) | proposal |
| sdd-spec | Proposal | spec |
| sdd-design | Proposal | design |
| sdd-tasks | Spec + Design | tasks |
| sdd-apply | Tasks + Spec + Design | apply-progress |
| sdd-verify | Spec + Tasks | verify-report |
| sdd-archive | All artifacts | archive-report |

## Skill Registry

Skills disponibles en: `~/.config/opencode/skills/` y `~/.claude/skills/`

- sdd-apply: Implementaci\u00f3n de tasks
- sdd-verify: Validaci\u00f3n de implementaci\u00f3n
- sdd-archive: Archivar cambio completado

## Contexto del Proyecto

Stack: Flask + SQLite + React + TypeScript + Tailwind + React Hook Form + Zod

Modelo de riesgo CR\u00cdTICO:
```
R = S + J + P + V + O + L
SI L == COINCIDENCIA_CONFIRMADA (3):
  - calculation_aborted = True
  - total_score = None
  - expediente se BLOQUEA
  - Solo OFICIAL_CUMPLIMIENTO puede desbloquear
```