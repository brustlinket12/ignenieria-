export type Role = 'ANALISTA' | 'OFICIAL_CUMPLIMIENTO' | 'ADMIN';

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
  ADMIN: {
    primary: 'bg-slate-700',
    primaryHover: 'hover:bg-slate-800',
    accent: 'text-slate-700',
    headerBg: 'bg-slate-800',
    headerText: 'text-white',
    badge: 'bg-slate-100',
    badgeText: 'text-slate-700',
    cardBorder: 'border-l-slate-500',
    kpiBorder: 'border-slate-500',
    roleLabel: 'ADMIN',
    roleDescription: 'Administración total',
  },
};

export function getRoleTheme(role: Role | undefined): RoleTheme {
  if (!role) return themes.ADMIN;
  return themes[role] || themes.ADMIN;
}

export function getRoleAccentColor(role: Role | undefined): string {
  if (!role) return 'text-slate-600';
  return themes[role]?.accent || 'text-slate-600';
}
