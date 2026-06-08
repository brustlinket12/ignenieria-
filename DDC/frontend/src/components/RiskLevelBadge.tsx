interface RiskLevelBadgeProps {
  level: string | null;
}

export default function RiskLevelBadge({ level }: RiskLevelBadgeProps) {
  if (!level) {
    return (
      <span className="px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-500">
        Sin evaluar
      </span>
    );
  }

  const config: Record<string, { bg: string; text: string }> = {
    BAJO: { bg: 'bg-green-100', text: 'text-green-700' },
    MEDIO: { bg: 'bg-yellow-100', text: 'text-yellow-700' },
    ALTO: { bg: 'bg-orange-100', text: 'text-orange-700' },
    MUY_ALTO: { bg: 'bg-red-100', text: 'text-red-700' },
  };

  const { bg, text } = config[level] || { bg: 'bg-gray-100', text: 'text-gray-700' };

  return (
    <span className={`px-2 py-1 rounded text-xs font-medium ${bg} ${text}`}>
      {level}
    </span>
  );
}