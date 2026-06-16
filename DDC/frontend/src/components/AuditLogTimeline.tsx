import type { AuditLog } from '../types/api';
import { useAuthStore } from '../stores/authStore';
import { getRoleTheme } from '../theme/roleTheme';

type AuditPayload = Record<string, unknown>;

type DetailRow = {
  label: string;
  value: unknown;
};

type ActionConfig = {
  label: string;
  dot: string;
  border: string;
  badge: string;
};

const ACTION_LABELS: Record<string, string> = {
  CASE_CREATED: 'Expediente creado',
  RISK_CALCULATED: 'Riesgo calculado',
  CASE_SUBMITTED: 'Expediente finalizado',
  CASE_APPROVED: 'Expediente aprobado',
  CASE_REJECTED: 'Expediente rechazado',
  CASE_REQUIRES_CORRECTION: 'Correccion solicitada',
  DOCUMENT_UPLOADED: 'Documento adjuntado',
  DOCUMENT_DELETED: 'Documento eliminado',
  CASE_UPDATED: 'Expediente actualizado',
  CASE_BLOCKED_BY_SANCTIONS: 'Bloqueo por sanciones',
  CASE_UNLOCKED_FALSE_POSITIVE: 'Desbloqueado como falso positivo',
  ALERT_CREATED: 'Alerta generada',
};

const KNOWN_ACTIONS = new Set(Object.keys(ACTION_LABELS));

const EVENT_STYLES: Record<string, Omit<ActionConfig, 'label'>> = {
  CASE_CREATED: { dot: 'bg-blue-500', border: 'border-l-blue-500', badge: 'bg-blue-50 text-blue-700 ring-blue-200' },
  CASE_UPDATED: { dot: 'bg-blue-500', border: 'border-l-blue-500', badge: 'bg-blue-50 text-blue-700 ring-blue-200' },
  DOCUMENT_UPLOADED: { dot: 'bg-blue-500', border: 'border-l-blue-500', badge: 'bg-blue-50 text-blue-700 ring-blue-200' },
  DOCUMENT_DELETED: { dot: 'bg-blue-500', border: 'border-l-blue-500', badge: 'bg-blue-50 text-blue-700 ring-blue-200' },
  CASE_SUBMITTED: { dot: 'bg-violet-500', border: 'border-l-violet-500', badge: 'bg-violet-50 text-violet-700 ring-violet-200' },
  CASE_APPROVED: { dot: 'bg-green-500', border: 'border-l-green-500', badge: 'bg-green-50 text-green-700 ring-green-200' },
  CASE_REJECTED: { dot: 'bg-red-500', border: 'border-l-red-500', badge: 'bg-red-50 text-red-700 ring-red-200' },
  CASE_BLOCKED_BY_SANCTIONS: { dot: 'bg-red-500', border: 'border-l-red-500', badge: 'bg-red-50 text-red-700 ring-red-200' },
  CASE_REQUIRES_CORRECTION: { dot: 'bg-amber-500', border: 'border-l-amber-500', badge: 'bg-amber-50 text-amber-700 ring-amber-200' },
};

const DEFAULT_STYLE = {
  dot: 'bg-gray-400',
  border: 'border-l-gray-400',
  badge: 'bg-gray-50 text-gray-700 ring-gray-200',
};

interface AuditLogTimelineProps {
  logs: AuditLog[];
}

export default function AuditLogTimeline({ logs }: AuditLogTimelineProps) {
  const { user } = useAuthStore();
  const roleTheme = getRoleTheme(user?.role);

  if (logs.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className={`text-lg font-semibold mb-4 ${roleTheme.accent}`}>Historial de Auditoria</h2>
        <p className="text-gray-500">Sin eventos de auditoria</p>
      </div>
    );
  }

  return (
    <section className="bg-white rounded-lg shadow p-4 sm:p-6">
      <div className="flex items-center justify-between gap-3 mb-5">
        <h2 className={`text-lg font-semibold ${roleTheme.accent}`}>Historial de Auditoria</h2>
        <span className={`${roleTheme.badge} ${roleTheme.badgeText} px-2.5 py-1 rounded-full text-xs font-medium`}>
          {logs.length} eventos
        </span>
      </div>

      <ol className="relative border-l border-gray-200 pl-5 sm:pl-7 space-y-4">
        {logs.map((log) => {
          const payload = parsePayload(log.payload);
          const config = getActionConfig(log.event_type);
          const isKnown = KNOWN_ACTIONS.has(log.event_type);
          const details = isKnown ? getDetails(log.event_type, payload, log) : [];

          return (
            <li key={log.id} className="relative">
              <span className={`absolute -left-[29px] sm:-left-[37px] top-4 h-4 w-4 rounded-full ring-4 ring-white ${config.dot}`} />

              <article className={`rounded-lg border border-gray-100 border-l-4 ${config.border} bg-white p-4 shadow-sm`}>
                <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ${config.badge}`}>
                      {config.label}
                    </span>
                    <p className="mt-2 text-xs text-gray-500 sm:text-sm">
                      {log.user?.name || 'Sistema'} · {formatDate(log.created_at)}
                    </p>
                  </div>
                  <span className="text-xs font-medium text-gray-400">#{log.id}</span>
                </div>

                {details.length > 0 && (
                  <dl className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2">
                    {details.map((detail) => (
                      <div key={detail.label} className="rounded-md bg-gray-50 px-3 py-2">
                        <dt className="text-[11px] font-medium uppercase tracking-wide text-gray-500 sm:text-xs">
                          {detail.label}
                        </dt>
                        <dd className="mt-1 text-sm font-medium text-gray-800 break-words">
                          {formatValue(detail.value)}
                        </dd>
                      </div>
                    ))}
                  </dl>
                )}

                {!isKnown && (
                  <details className="mt-4 rounded-md border border-gray-200 bg-gray-50 p-3">
                    <summary className="cursor-pointer text-sm font-medium text-gray-700">Ver datos tecnicos</summary>
                    <pre className="mt-3 overflow-x-auto rounded bg-white p-3 text-xs text-gray-600">
                      {JSON.stringify(payload ?? log.payload ?? {}, null, 2)}
                    </pre>
                  </details>
                )}
              </article>
            </li>
          );
        })}
      </ol>
    </section>
  );
}

function getActionConfig(eventType: string): ActionConfig {
  const style = EVENT_STYLES[eventType] || DEFAULT_STYLE;
  return {
    label: ACTION_LABELS[eventType] || eventType || 'Evento desconocido',
    ...style,
  };
}

function parsePayload(payload: string | null): AuditPayload {
  if (!payload) return {};

  try {
    const parsed = JSON.parse(payload);
    return isRecord(parsed) ? parsed : { valor: parsed };
  } catch {
    return { payload };
  }
}

function getDetails(eventType: string, data: AuditPayload, log: AuditLog): DetailRow[] {
  switch (eventType) {
    case 'CASE_CREATED': {
      const client = getRecord(data.client);
      return compactRows([
        { label: 'Cliente', value: client.name },
        { label: 'Tipo documento', value: client.id_type },
        { label: 'Numero documento', value: client.id_number },
        { label: 'Pais', value: client.country },
      ]);
    }
    case 'RISK_CALCULATED':
      return compactRows([
        { label: 'Nivel de riesgo', value: data.risk_level },
        { label: 'Puntaje total', value: data.total_score },
        { label: 'Sector', value: data.sector_score },
        { label: 'Jurisdiccion', value: data.jurisdiction_score },
        { label: 'PEP', value: data.pep_score },
        { label: 'Volumen', value: data.volume_score },
        { label: 'Origen fondos', value: data.funds_origin_score },
        { label: 'Sanciones score', value: data.sanctions_score },
      ]);
    case 'DOCUMENT_UPLOADED':
      return compactRows([
        { label: 'Tipo de documento', value: data.document_type || data.type },
        { label: 'Nombre del archivo', value: data.filename || data.file_name || data.name },
      ]);
    case 'DOCUMENT_DELETED':
      return compactRows([{ label: 'Nombre del archivo', value: data.filename || data.file_name || data.name }]);
    case 'CASE_SUBMITTED':
      return compactRows([
        { label: 'Estado destino', value: data.status || data.to_status || data.target_status },
        { label: 'Auto-aprobacion', value: data.auto_approved || data.auto_approval_message || data.message },
      ]);
    case 'CASE_APPROVED':
      return compactRows([{ label: 'Aprobado por', value: data.approved_by || data.reviewer || log.user?.name }]);
    case 'CASE_REJECTED':
      return compactRows([{ label: 'Motivo', value: data.rejection_reason || data.reason }]);
    case 'CASE_REQUIRES_CORRECTION':
      return compactRows([{ label: 'Nota de correccion', value: data.correction_note || data.note }]);
    case 'CASE_UPDATED':
      return compactRows([{ label: 'Campos modificados', value: data.changed_fields || data.fields || data.changes }]);
    case 'CASE_BLOCKED_BY_SANCTIONS':
      return compactRows([
        { label: 'Nombre coincidente', value: data.matched_name },
        { label: 'Lista coincidente', value: data.matched_list },
      ]);
    case 'CASE_UNLOCKED_FALSE_POSITIVE':
      return compactRows([{ label: 'Justificacion', value: data.justification || data.reason }]);
    default:
      return [];
  }
}

function compactRows(rows: DetailRow[]): DetailRow[] {
  return rows.filter((row) => row.value !== undefined && row.value !== null && row.value !== '');
}

function formatDate(value: string | null): string {
  if (!value) return 'Fecha no disponible';

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return 'Fecha no disponible';

  return date.toLocaleString('es-UY', {
    dateStyle: 'short',
    timeStyle: 'short',
  });
}

function formatValue(value: unknown): string {
  if (value === undefined || value === null || value === '') return 'No informado';
  if (typeof value === 'boolean') return value ? 'Si' : 'No';
  if (Array.isArray(value)) return value.map(formatValue).join(', ');
  if (isRecord(value)) return JSON.stringify(value);
  return String(value);
}

function getRecord(value: unknown): AuditPayload {
  return isRecord(value) ? value : {};
}

function isRecord(value: unknown): value is AuditPayload {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}
