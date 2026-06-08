interface StatusBadgeProps {
  status: string;
}

export default function CaseFileStatusBadge({ status }: StatusBadgeProps) {
  const config: Record<string, { bg: string; text: string; label: string }> = {
    BORRADOR: { bg: 'bg-gray-100', text: 'text-gray-700', label: 'Borrador' },
    EN_REVISION: { bg: 'bg-blue-100', text: 'text-blue-700', label: 'En Revision' },
    APROBADO: { bg: 'bg-green-100', text: 'text-green-700', label: 'Aprobado' },
    RECHAZADO: { bg: 'bg-red-100', text: 'text-red-700', label: 'Rechazado' },
    BLOQUEADO_POR_SANCIONES: { bg: 'bg-red-100', text: 'text-red-700', label: 'Bloqueado' },
    DESBLOQUEADO_FALSO_POSITIVO: { bg: 'bg-yellow-100', text: 'text-yellow-700', label: 'Desbloqueado' },
  };

  const { bg, text, label } = config[status] || { bg: 'bg-gray-100', text: 'text-gray-700', label: status };

  return (
    <span className={`px-2 py-1 rounded text-xs font-medium ${bg} ${text}`}>
      {label}
    </span>
  );
}