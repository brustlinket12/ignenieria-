import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import { useAuthStore } from '../stores/authStore';
import { getRoleTheme } from '../theme/roleTheme';
import type { CaseFile, Alert } from '../types/api';
import CaseFileStatusBadge from '../components/CaseFileStatusBadge';
import RiskLevelBadge from '../components/RiskLevelBadge';

export default function Dashboard() {
  const { user } = useAuthStore();
  const [caseFiles, setCaseFiles] = useState<CaseFile[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [stats, setStats] = useState({
    total: 0,
    borrador: 0,
    enRevision: 0,
    aprobado: 0,
    rechazado: 0,
    requiereCorreccion: 0,
  });

  const theme = getRoleTheme(user?.role);
  const isAnalista = user?.role === 'ANALISTA';
  const isOficial = user?.role === 'OFICIAL_CUMPLIMIENTO';
  const isAuditoria = user?.role === 'OFICIAL_AUDITORIA';

  const loadData = async () => {
    try {
      const [cfRes, alertRes] = await Promise.all([
        api.get('/case-files'),
        isAuditoria ? Promise.resolve({ data: [] }) : api.get('/alerts'),
      ]);
      setCaseFiles(cfRes.data);
      setAlerts(alertRes.data);

      const data = cfRes.data;
      setStats({
        total: data.length,
        borrador: data.filter((c: CaseFile) => c.status === 'BORRADOR').length,
        enRevision: data.filter((c: CaseFile) => c.status === 'EN_REVISION').length,
        aprobado: data.filter((c: CaseFile) => c.status === 'APROBADO').length,
        rechazado: data.filter((c: CaseFile) => c.status === 'RECHAZADO').length,
        requiereCorreccion: data.filter((c: CaseFile) => c.status === 'REQUIERE_CORRECCION').length,
      });
    } catch (error) {
      console.error('Error cargando datos:', error);
    }
  };

  useEffect(() => {
    if (user) {
      loadData();
    }
  }, [user?.role]);

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Titulo con accion principal segun rol */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">
            {isAnalista && 'Panel de Operacion'}
            {isOficial && 'Panel de Control y Cumplimiento'}
            {!isAnalista && !isOficial && 'Panel de Auditoria'}
          </h1>
          <p className="text-gray-500 text-sm mt-1">{theme.roleDescription}</p>
        </div>
        {isAnalista && (
          <Link
            to="/case-files/new"
            className={`px-5 py-2.5 rounded-lg font-medium text-white transition-colors ${theme.primary} ${theme.primaryHover}`}
          >
            + Nuevo Expediente
          </Link>
        )}
      </div>

      {/* KPIs - differ segun rol */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {/* Total - siempre visible */}
        <div className="bg-white p-6 rounded-lg shadow-sm border-l-4 border-gray-400">
          <p className="text-gray-500 text-sm">Total Expedientes</p>
          <p className="text-3xl font-bold text-gray-800">{stats.total}</p>
        </div>

        {/* En Revision - visible para oficial y auditoria */}
        {(isOficial || !isAnalista) && (
          <div className={`bg-white p-6 rounded-lg shadow-sm border-l-4 ${theme.kpiBorder}`}>
            <p className="text-gray-500 text-sm">En Revision</p>
            <p className={`text-3xl font-bold ${theme.accent}`}>{stats.enRevision}</p>
          </div>
        )}

        {/* Aprobados - para todos */}
        <div className="bg-white p-6 rounded-lg shadow-sm border-l-4 border-green-500">
          <p className="text-gray-500 text-sm">Aprobados</p>
          <p className="text-3xl font-bold text-green-600">{stats.aprobado}</p>
        </div>

        {/* Borrador - solo para analista */}
        {isAnalista && (
          <div className="bg-white p-6 rounded-lg shadow-sm border-l-4 border-blue-400">
            <p className="text-gray-500 text-sm">En Borrador</p>
            <p className="text-3xl font-bold text-blue-500">{stats.borrador}</p>
          </div>
        )}

        {/* Rechazados - para oficial y auditoria */}
        {!isAnalista && (
          <div className="bg-white p-6 rounded-lg shadow-sm border-l-4 border-red-400">
            <p className="text-gray-500 text-sm">Rechazados</p>
            <p className="text-3xl font-bold text-red-500">{stats.rechazado}</p>
          </div>
        )}

        {isOficial && (
          <div className="bg-white p-6 rounded-lg shadow-sm border-l-4 border-amber-400">
            <p className="text-gray-500 text-sm">Requieren Correccion</p>
            <p className="text-3xl font-bold text-amber-500">{stats.requiereCorreccion}</p>
          </div>
        )}
      </div>

      {/* Expedientes recientes */}
      <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold text-gray-800">Expedientes Recientes</h2>
          <Link to="/case-files" className={`text-sm font-medium ${theme.accent} hover:underline`}>
            Ver todos
          </Link>
        </div>
        {caseFiles.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-gray-400 mb-4">No hay expedientes creados</p>
            {isAnalista && (
              <Link
                to="/case-files/new"
                className={`inline-block px-4 py-2 rounded-lg text-white text-sm font-medium ${theme.primary} ${theme.primaryHover}`}
              >
                Crear primer expediente
              </Link>
            )}
          </div>
        ) : (
          <table className="w-full">
            <thead>
              <tr className="text-left text-gray-500 border-b">
                <th className="pb-3 text-sm">ID</th>
                <th className="pb-3 text-sm">Cliente</th>
                <th className="pb-3 text-sm">Estado</th>
                <th className="pb-3 text-sm">Nivel Riesgo</th>
                <th className="pb-3 text-sm">Fecha</th>
              </tr>
            </thead>
            <tbody>
              {(isOficial || isAuditoria ? caseFiles.filter((cf) => cf.status !== 'BORRADOR') : caseFiles.slice(0, 5)).map((cf) => (
                <tr key={cf.id} className="border-b border-gray-50 hover:bg-gray-50 transition-colors">
                  <td className="py-3">
                    <Link to={`/case-files/${cf.id}`} className={`font-medium ${theme.accent} hover:underline`}>
                      #{cf.id}
                    </Link>
                  </td>
                  <td className="py-3 text-gray-700">{cf.client?.name || '-'}</td>
                  <td className="py-3">
                    <CaseFileStatusBadge status={cf.status} />
                  </td>
                  <td className="py-3">
                    <RiskLevelBadge level={cf.risk_assessment?.risk_level || null} />
                  </td>
                  <td className="py-3 text-gray-500 text-sm">
                    {new Date(cf.created_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {!isAuditoria && (
        <div className={`rounded-lg shadow-sm p-6 ${isOficial ? 'bg-red-50 border border-red-200' : 'bg-white'}`}>
          <div className="flex justify-between items-center mb-4">
            <h2 className={`text-lg font-semibold ${isOficial ? 'text-red-800' : 'text-gray-800'}`}>
              {isOficial ? 'Alertas Criticas' : 'Alertas Pendientes'}
            </h2>
            <Link to="/alerts" className={`text-sm font-medium ${theme.accent} hover:underline`}>
              Ver todas
            </Link>
          </div>
          {alerts.length === 0 ? (
            <p className="text-gray-500">No hay alertas pendientes</p>
          ) : (
            <ul className="space-y-3">
              {alerts.slice(0, 5).map((alert) => (
                <li key={alert.id} className={`flex items-start gap-3 p-3 rounded ${isOficial ? 'bg-white border border-red-100' : 'bg-yellow-50'}`}>
                  <span className={`text-lg ${isOficial ? 'text-red-500' : 'text-yellow-600'}`}>⚠️</span>
                  <div>
                    <p className={`font-medium ${isOficial ? 'text-red-800' : 'text-gray-800'}`}>{alert.message}</p>
                    <p className="text-sm text-gray-500">
                      {new Date(alert.created_at).toLocaleString()}
                    </p>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
