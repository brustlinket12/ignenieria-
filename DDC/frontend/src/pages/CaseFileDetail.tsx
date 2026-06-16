import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import { useAuthStore } from '../stores/authStore';
import type { CaseFile, AuditLog } from '../types/api';
import CaseFileStatusBadge from '../components/CaseFileStatusBadge';
import RiskLevelBadge from '../components/RiskLevelBadge';
import { getRoleTheme } from '../theme/roleTheme';

export default function CaseFileDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const [caseFile, setCaseFile] = useState<CaseFile | null>(null);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);
  const [rejectReason, setRejectReason] = useState('');
  const [showRejectForm, setShowRejectForm] = useState(false);
  const [correctionNote, setCorrectionNote] = useState('');
  const [showCorrectionForm, setShowCorrectionForm] = useState(false);
  const [unblockJustification, setUnblockJustification] = useState('');
  const [showUnblockForm, setShowUnblockForm] = useState(false);

  const roleTheme = getRoleTheme(user?.role);

  useEffect(() => {
    if (id) {
      loadCaseFile();
    }
  }, [id]);

  const loadCaseFile = async () => {
    try {
      setLoading(true);
      const [cfRes, logsRes] = await Promise.all([
        api.get(`/case-files/${id}`),
        api.get(`/case-files/${id}/audit-logs`),
      ]);
      setCaseFile(cfRes.data);
      setAuditLogs(logsRes.data);
    } catch (error) {
      console.error('Error cargando expediente:', error);
      alert('Error al cargar el expediente');
      navigate('/case-files');
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async () => {
    if (!caseFile) return;
    try {
      setActionLoading(true);
      await api.post(`/case-files/${caseFile.id}/approve`);
      loadCaseFile();
    } catch (error: any) {
      alert(error.response?.data?.error || 'Error al aprobar');
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async () => {
    if (!caseFile || !rejectReason.trim()) {
      alert('Debe ingresar el motivo del rechazo');
      return;
    }
    try {
      setActionLoading(true);
      await api.post(`/case-files/${caseFile.id}/reject`, { reason: rejectReason });
      setShowRejectForm(false);
      setRejectReason('');
      loadCaseFile();
    } catch (error: any) {
      alert(error.response?.data?.error || 'Error al rechazar');
    } finally {
      setActionLoading(false);
    }
  };

  const handleRequestCorrection = async () => {
    if (!caseFile || !correctionNote.trim()) {
      alert('Debe ingresar la nota de correccion');
      return;
    }
    try {
      setActionLoading(true);
      await api.post(`/case-files/${caseFile.id}/request-correction`, { correction_note: correctionNote });
      setShowCorrectionForm(false);
      setCorrectionNote('');
      loadCaseFile();
    } catch (error: any) {
      alert(error.response?.data?.error || 'Error al solicitar correccion');
    } finally {
      setActionLoading(false);
    }
  };

  const handleUnblock = async () => {
    if (!caseFile || !unblockJustification.trim()) {
      alert('La justificacion es requerida');
      return;
    }
    try {
      setActionLoading(true);
      await api.post(`/case-files/${caseFile.id}/unblock`, {
        justification: unblockJustification,
      });
      setShowUnblockForm(false);
      setUnblockJustification('');
      loadCaseFile();
    } catch (error: any) {
      alert(error.response?.data?.error || 'Error al desbloquear');
    } finally {
      setActionLoading(false);
    }
  };

  if (loading) {
    return <div className="p-6">Cargando...</div>;
  }

  if (!caseFile) {
    return <div className="p-6">Expediente no encontrado</div>;
  }

  const isOfficial = user?.role === 'OFICIAL_CUMPLIMIENTO';

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="flex items-center gap-4 mb-6">
        <button onClick={() => navigate('/case-files')} className="text-gray-500 hover:text-gray-700">
          ← Volver
        </button>
        <h1 className="text-2xl font-bold">Expediente #{caseFile.id}</h1>
        <CaseFileStatusBadge status={caseFile.status} />
      </div>

      {/* Info del Cliente */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4">Informacion del Cliente</h2>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-gray-500 text-sm">Nombre</p>
            <p className="font-medium">{caseFile.client?.name}</p>
          </div>
          <div>
            <p className="text-gray-500 text-sm">Tipo Documento</p>
            <p className="font-medium">{caseFile.client?.id_type}</p>
          </div>
          <div>
            <p className="text-gray-500 text-sm">Numero Documento</p>
            <p className="font-medium">{caseFile.client?.id_number}</p>
          </div>
          <div>
            <p className="text-gray-500 text-sm">Pais</p>
            <p className="font-medium">{caseFile.client?.country}</p>
          </div>
        </div>
      </div>

      {/* Evaluacion de Riesgo */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4">Evaluacion de Riesgo</h2>
        {caseFile.risk_assessment ? (
          caseFile.risk_assessment.calculation_aborted ? (
            <div className="bg-red-50 border border-red-200 p-4 rounded">
              <p className="text-red-700 font-medium">⚠️ CALCULO ABORTADO - BLOQUEADO POR SANCIONES</p>
              <p className="text-red-600 text-sm mt-1">
                Se detecto coincidencia en listas de sanciones. El expediente no puede continuar
                hasta ser desbloqueado por un Oficial de Cumplimiento.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center p-4 bg-gray-50 rounded">
                <p className="text-3xl font-bold">{caseFile.risk_assessment.total_score}</p>
                <p className="text-gray-500 text-sm">Puntaje Total</p>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded">
                <RiskLevelBadge level={caseFile.risk_assessment.risk_level || null} />
                <p className="text-gray-500 text-sm mt-2">Nivel de Riesgo</p>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded">
                <p className="text-gray-500 text-sm">Sector</p>
                <p className="font-medium">{caseFile.risk_assessment.sector_score}/30</p>
                <p className="text-gray-500 text-sm">Jurisdiccion</p>
                <p className="font-medium">{caseFile.risk_assessment.jurisdiction_score}/20</p>
                <p className="text-gray-500 text-sm">PEP</p>
                <p className="font-medium">{caseFile.risk_assessment.pep_score}/20</p>
                <p className="text-gray-500 text-sm">Volumen</p>
                <p className="font-medium">{caseFile.risk_assessment.volume_score}/20</p>
                <p className="text-gray-500 text-sm">Origen Fondos</p>
                <p className="font-medium">{caseFile.risk_assessment.funds_origin_score}/10</p>
              </div>
            </div>
          )
        ) : (
          <p className="text-gray-500">Sin evaluacion de riesgo</p>
        )}
      </div>

      {/* Screening de Sanciones */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4">Screening de Sanciones</h2>
        {caseFile.sanctions_screening?.length > 0 ? (
          <div className="space-y-3">
            {caseFile.sanctions_screening.map((screening) => (
              <div key={screening.id} className="flex items-center gap-4 p-3 bg-gray-50 rounded">
                <span className={`text-2xl ${
                  screening.result === 'COINCIDENCIA_CONFIRMADA' ? 'text-red-600' :
                  screening.result === 'COINCIDENCIA_PARCIAL' ? 'text-yellow-600' :
                  'text-green-600'
                }`}>
                  {screening.result === 'COINCIDENCIA_CONFIRMADA' ? '🚫' :
                   screening.result === 'COINCIDENCIA_PARCIAL' ? '⚠️' : '✓'}
                </span>
                <div>
                  <p className="font-medium">{screening.result}</p>
                  {screening.matched_name && (
                    <p className="text-sm text-gray-500">
                      Coincidencia: {screening.matched_name} ({screening.matched_list})
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500">Sin screening realizado</p>
        )}
      </div>

      {/* Acciones de Oficial de Cumplimiento */}
      {caseFile.status === 'EN_REVISION' && isOfficial && (
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4 text-violet-700">Acciones de Revision</h2>

          {!showRejectForm && !showCorrectionForm && (
            <div className="flex gap-4">
              <button
                onClick={handleApprove}
                disabled={actionLoading}
                className={`flex-1 ${roleTheme.primary} text-white py-3 rounded ${roleTheme.primaryHover} disabled:opacity-50`}
              >
                {actionLoading ? 'Procesando...' : 'Aprobar Expediente'}
              </button>
              <button
                onClick={() => setShowCorrectionForm(true)}
                disabled={actionLoading}
                className="flex-1 bg-amber-500 text-white py-3 rounded hover:bg-amber-600 disabled:opacity-50"
              >
                Solicitar Correccion
              </button>
              <button
                onClick={() => setShowRejectForm(true)}
                disabled={actionLoading}
                className="flex-1 bg-red-600 text-white py-3 rounded hover:bg-red-700 disabled:opacity-50"
              >
                Rechazar Expediente
              </button>
            </div>
          )}

          {showRejectForm && (
            <div className="border border-red-200 rounded-lg p-4 bg-red-50">
              <h3 className="font-medium text-red-700 mb-2">Rechazar Expediente</h3>
              <p className="text-sm text-red-600 mb-3">Ingrese el motivo del rechazo:</p>
              <textarea
                value={rejectReason}
                onChange={(e) => setRejectReason(e.target.value)}
                className="w-full px-3 py-2 border border-red-300 rounded-md mb-3 focus:outline-none focus:ring-2 focus:ring-red-500"
                rows={3}
                placeholder="Motivo del rechazo..."
                autoFocus
              />
              <div className="flex gap-2">
                <button
                  onClick={() => { setShowRejectForm(false); setRejectReason(''); }}
                  className="flex-1 bg-gray-200 text-gray-700 py-2 rounded hover:bg-gray-300"
                >
                  Cancelar
                </button>
                <button
                  onClick={handleReject}
                  disabled={actionLoading || !rejectReason.trim()}
                  className="flex-1 bg-red-600 text-white py-2 rounded hover:bg-red-700 disabled:opacity-50"
                >
                  {actionLoading ? 'Procesando...' : 'Confirmar Rechazo'}
                </button>
              </div>
            </div>
          )}

          {showCorrectionForm && (
            <div className="border border-amber-200 rounded-lg p-4 bg-amber-50">
              <h3 className="font-medium text-amber-700 mb-2">Solicitar Correccion</h3>
              <p className="text-sm text-amber-600 mb-3">Ingrese las correcciones requeridas:</p>
              <textarea
                value={correctionNote}
                onChange={(e) => setCorrectionNote(e.target.value)}
                className="w-full px-3 py-2 border border-amber-300 rounded-md mb-3 focus:outline-none focus:ring-2 focus:ring-amber-500"
                rows={3}
                placeholder="Correcciones requeridas..."
                autoFocus
              />
              <div className="flex gap-2">
                <button
                  onClick={() => { setShowCorrectionForm(false); setCorrectionNote(''); }}
                  className="flex-1 bg-gray-200 text-gray-700 py-2 rounded hover:bg-gray-300"
                >
                  Cancelar
                </button>
                <button
                  onClick={handleRequestCorrection}
                  disabled={actionLoading || !correctionNote.trim()}
                  className="flex-1 bg-amber-500 text-white py-2 rounded hover:bg-amber-600 disabled:opacity-50"
                >
                  {actionLoading ? 'Procesando...' : 'Confirmar Correccion'}
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {caseFile.status === 'BLOQUEADO_POR_SANCIONES' && isOfficial && (
        <div className="bg-white rounded-lg shadow p-6 mb-6 border-l-4 border-red-500">
          <h2 className="text-lg font-semibold mb-4 text-red-600">Expediente Bloqueado</h2>
          <p className="text-gray-600 mb-4">
            Este expediente fue bloqueado debido a coincidencia con lista de sanciones.
            Solo un Oficial de Cumplimiento puede desbloquearlo marcando como falso positivo.
          </p>

          {!showUnblockForm && (
            <button
              onClick={() => setShowUnblockForm(true)}
              className={`${roleTheme.primary} text-white px-6 py-3 rounded ${roleTheme.primaryHover}`}
            >
              Desbloquear como Falso Positivo
            </button>
          )}

          {showUnblockForm && (
            <div className="border border-gray-300 rounded-lg p-4 bg-gray-50">
              <h3 className="font-medium text-gray-700 mb-2">Desbloquear como Falso Positivo</h3>
              <p className="text-sm text-gray-600 mb-3">Debe justificar por que este expediente no representa un riesgo real:</p>
              <textarea
                value={unblockJustification}
                onChange={(e) => setUnblockJustification(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md mb-3 focus:outline-none focus:ring-2 focus:ring-violet-500"
                rows={3}
                placeholder="Justificacion requerida..."
                autoFocus
              />
              <div className="flex gap-2">
                <button
                  onClick={() => { setShowUnblockForm(false); setUnblockJustification(''); }}
                  className="flex-1 bg-gray-200 text-gray-700 py-2 rounded hover:bg-gray-300"
                >
                  Cancelar
                </button>
                <button
                  onClick={handleUnblock}
                  disabled={actionLoading || !unblockJustification.trim()}
                  className={`flex-1 ${roleTheme.primary} text-white py-2 rounded ${roleTheme.primaryHover} disabled:opacity-50`}
                >
                  {actionLoading ? 'Procesando...' : 'Confirmar Desbloqueo'}
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Historial de Auditoria */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Historial de Auditoria</h2>
        {auditLogs.length === 0 ? (
          <p className="text-gray-500">Sin eventos de auditoria</p>
        ) : (
          <ul className="space-y-3">
            {auditLogs.map((log) => (
              <li key={log.id} className="flex items-start gap-3 p-3 bg-gray-50 rounded">
                <span className="text-gray-400 text-sm">#{log.id}</span>
                <div>
                  <p className="font-medium">{log.event_type}</p>
                  {log.payload && (
                    <pre className="text-xs text-gray-500 mt-1 bg-white p-2 rounded overflow-x-auto">
                      {JSON.stringify(JSON.parse(log.payload), null, 2)}
                    </pre>
                  )}
                  <p className="text-xs text-gray-400 mt-1">
                    {log.user?.name || 'Sistema'} - {new Date(log.created_at).toLocaleString()}
                  </p>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}