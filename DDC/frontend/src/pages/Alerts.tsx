import { useEffect, useState } from 'react';
import api from '../services/api';
import { useAuthStore } from '../stores/authStore';
import type { Alert } from '../types/api';

export default function Alerts() {
  const { user } = useAuthStore();
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const isAuditoria = user?.role === 'OFICIAL_AUDITORIA';

  useEffect(() => {
    if (user && !isAuditoria) {
      loadAlerts();
    }
  }, [user?.role, isAuditoria]);

  if (isAuditoria) {
    return (
      <div className="p-6 text-center">
        <p className="text-gray-500">No tienes acceso a alertas.</p>
      </div>
    );
  }

  const loadAlerts = async () => {
    try {
      const response = await api.get('/alerts');
      setAlerts(response.data);
    } catch (error) {
      console.error('Error cargando alertas:', error);
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (alertId: number) => {
    try {
      await api.patch(`/alerts/${alertId}/read`);
      setAlerts(alerts.map(a => a.id === alertId ? { ...a, read: true } : a));
    } catch (error) {
      console.error('Error marcando alerta:', error);
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Alertas</h1>

      <div className="bg-white rounded-lg shadow">
        {loading ? (
          <p className="p-6 text-center text-gray-500">Cargando...</p>
        ) : alerts.length === 0 ? (
          <div className="p-6 text-center">
            <span className="text-4xl mb-4 block">✓</span>
            <p className="text-gray-500">No hay alertas pendientes</p>
          </div>
        ) : (
          <ul className="divide-y">
            {alerts.map((alert) => (
              <li key={alert.id} className="p-4 flex items-start gap-4 hover:bg-gray-50">
                <span className="text-yellow-500 text-xl">⚠️</span>
                <div className="flex-1">
                  <p className="font-medium">{alert.message}</p>
                  <p className="text-sm text-gray-500">
                    Expediente #{alert.case_file_id} - {new Date(alert.created_at).toLocaleString()}
                  </p>
                </div>
                {!alert.read && (
                  <button
                    onClick={() => markAsRead(alert.id)}
                    className="text-blue-600 hover:underline text-sm"
                  >
                    Marcar leida
                  </button>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
