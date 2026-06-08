import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../services/api';
import { useAuthStore } from '../stores/authStore';
import { getRoleTheme } from '../theme/roleTheme';
import type { CaseFile } from '../types/api';
import CaseFileStatusBadge from '../components/CaseFileStatusBadge';
import RiskLevelBadge from '../components/RiskLevelBadge';

export default function CaseFileList() {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const [caseFiles, setCaseFiles] = useState<CaseFile[]>([]);
  const [filter, setFilter] = useState<string>('');
  const [loading, setLoading] = useState(true);

  const theme = getRoleTheme(user?.role as any);

  useEffect(() => {
    loadCaseFiles();
  }, [filter]);

  const loadCaseFiles = async () => {
    try {
      setLoading(true);
      const url = filter ? `/case-files?status=${filter}` : '/case-files';
      const response = await api.get(url);
      setCaseFiles(response.data);
    } catch (error) {
      console.error('Error cargando expedientes:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800">Expedientes</h1>
        <button
          onClick={() => navigate('/case-files/new')}
          className={`px-5 py-2.5 rounded-lg font-medium text-white transition-colors ${theme.primary} ${theme.primaryHover}`}
        >
          + Nuevo Expediente
        </button>
      </div>

      {/* Filtros */}
      <div className="flex gap-2 mb-6">
        <button
          onClick={() => setFilter('')}
          className={`px-4 py-2 rounded text-sm font-medium transition-colors ${
            filter === '' ? `${theme.primary} text-white` : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
        >
          Todos
        </button>
        <button
          onClick={() => setFilter('BORRADOR')}
          className={`px-4 py-2 rounded text-sm font-medium transition-colors ${
            filter === 'BORRADOR' ? `${theme.primary} text-white` : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
        >
          Borrador
        </button>
        <button
          onClick={() => setFilter('EN_REVISION')}
          className={`px-4 py-2 rounded text-sm font-medium transition-colors ${
            filter === 'EN_REVISION' ? `${theme.primary} text-white` : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
        >
          En Revision
        </button>
        <button
          onClick={() => setFilter('BLOQUEADO_POR_SANCIONES')}
          className={`px-4 py-2 rounded text-sm font-medium transition-colors ${
            filter === 'BLOQUEADO_POR_SANCIONES' ? 'bg-red-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
          }`}
        >
          Bloqueados
        </button>
      </div>

      {/* Tabla */}
      <div className="bg-white rounded-lg shadow-sm overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50 border-b">
            <tr className="text-left text-gray-500 text-sm">
              <th className="p-4 font-medium">ID</th>
              <th className="p-4 font-medium">Cliente</th>
              <th className="p-4 font-medium">Pais</th>
              <th className="p-4 font-medium">Estado</th>
              <th className="p-4 font-medium">Nivel Riesgo</th>
              <th className="p-4 font-medium">Fecha Creacion</th>
              <th className="p-4 font-medium">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={7} className="p-4 text-center text-gray-500">
                  Cargando...
                </td>
              </tr>
            ) : caseFiles.length === 0 ? (
              <tr>
                <td colSpan={7} className="p-4 text-center text-gray-400 py-8">
                  No hay expedientes. Crea el primero con el boton azul de arriba.
                </td>
              </tr>
            ) : (
              caseFiles.map((cf) => (
                <tr key={cf.id} className="border-t border-gray-100 hover:bg-gray-50 transition-colors">
                  <td className="p-4 font-medium text-gray-800">#{cf.id}</td>
                  <td className="p-4 text-gray-700">{cf.client?.name || '-'}</td>
                  <td className="p-4 text-gray-500 text-sm">{cf.client?.country || '-'}</td>
                  <td className="p-4">
                    <CaseFileStatusBadge status={cf.status} />
                  </td>
                  <td className="p-4">
                    <RiskLevelBadge level={cf.risk_assessment?.risk_level || null} />
                  </td>
                  <td className="p-4 text-gray-500 text-sm">
                    {new Date(cf.created_at).toLocaleDateString()}
                  </td>
                  <td className="p-4">
                    <Link
                      to={`/case-files/${cf.id}`}
                      className={`text-sm font-medium ${theme.accent} hover:underline`}
                    >
                      Ver Detalle
                    </Link>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}