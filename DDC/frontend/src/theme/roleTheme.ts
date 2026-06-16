export type Role = 'ANALISTA' | 'OFICIAL_CUMPLIMIENTO' | 'OFICIAL_AUDITORIA';

export interface RoleTheme {
  primary: string;
  primaryHover: string;
  accent: string;
  headerBg: string;
  headerText: string;
  badge: string;
  badgeText: string;
  cardBorder: string;
  kpiBorder: string;
  roleLabel: string;
  roleDescription: string;
}

const themes: Record<Role, RoleTheme> = {
  ANALISTA: {
    primary: 'bg-blue-600',
    primaryHover: 'hover:bg-blue-700',
    accent: 'text-blue-600',
    headerBg: 'bg-blue-600',
    headerText: 'text-white',
    badge: 'bg-blue-100',
    badgeText: 'text-blue-700',
    cardBorder: 'border-l-blue-500',
    kpiBorder: 'border-blue-500',
    roleLabel: 'ANALISTA',
    roleDescription: 'Carga y preparación de expedientes',
  },
  OFICIAL_CUMPLIMIENTO: {
    primary: 'bg-violet-600',
    primaryHover: 'hover:bg-violet-700',
    accent: 'text-violet-600',
    headerBg: 'bg-violet-700',
    headerText: 'text-white',
    badge: 'bg-violet-100',
    badgeText: 'text-violet-700',
    cardBorder: 'border-l-violet-500',
    kpiBorder: 'border-violet-500',
    roleLabel: 'OFICIAL DE CUMPLIMIENTO',
    roleDescription: 'Revisión, control y decisión',
  },
  OFICIAL_AUDITORIA: {
    primary: 'bg-teal-700',
    primaryHover: 'hover:bg-teal-800',
    accent: 'text-teal-700',
    headerBg: 'bg-teal-800',
    headerText: 'text-white',
    badge: 'bg-teal-100',
    badgeText: 'text-teal-700',
    cardBorder: 'border-l-teal-500',
    kpiBorder: 'border-teal-500',
    roleLabel: 'OFICIAL DE AUDITORIA',
    roleDescription: 'Supervisión y auditoría',
  },
};

export function getRoleTheme(role: Role | undefined): RoleTheme {
  if (!role) return themes.OFICIAL_AUDITORIA;
  return themes[role] || themes.OFICIAL_AUDITORIA;
}

export function getRoleAccentColor(role: Role | undefined): string {
  if (!role) return 'text-slate-600';
  return themes[role]?.accent || 'text-slate-600';
}
