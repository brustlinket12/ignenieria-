import { ReactNode } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { getRoleTheme } from '../theme/roleTheme';

interface LayoutProps {
  children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();

  const theme = getRoleTheme(user?.role as any);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header con color segun rol */}
      <header className={`${theme.headerBg} shadow-md`}>
        <div className="px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-8">
            <h1 className={`text-xl font-bold ${theme.headerText}`}>DDC</h1>
            <nav className="flex gap-6">
              <Link to="/" className={`${theme.headerText} opacity-90 hover:opacity-100 transition-opacity`}>
                Inicio
              </Link>
              <Link to="/case-files" className={`${theme.headerText} opacity-90 hover:opacity-100 transition-opacity`}>
                Expedientes
              </Link>
              {user?.role !== 'OFICIAL_AUDITORIA' && (
                <Link to="/alerts" className={`${theme.headerText} opacity-90 hover:opacity-100 transition-opacity`}>
                  Alertas
                </Link>
              )}
            </nav>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right">
              <p className={`text-sm font-medium ${theme.headerText}`}>{user?.name}</p>
              <p className={`text-xs ${theme.headerText} opacity-75`}>{theme.roleDescription}</p>
            </div>
            <span className={`text-xs px-3 py-1 rounded-full font-semibold ${theme.badge} ${theme.badgeText}`}>
              {theme.roleLabel}
            </span>
            <button
              onClick={handleLogout}
              className={`text-sm ${theme.headerText} opacity-75 hover:opacity-100 transition-opacity`}
            >
              Cerrar sesion
            </button>
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="p-6">
        {children}
      </main>
    </div>
  );
}
