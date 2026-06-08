import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useEffect } from 'react';
import { useAuthStore } from './stores/authStore';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import CaseFileList from './pages/CaseFileList';
import CaseFileForm from './pages/CaseFileForm';
import CaseFileDetail from './pages/CaseFileDetail';
import Alerts from './pages/Alerts';
import Layout from './components/Layout';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading, checkAuth } = useAuthStore();

  useEffect(() => {
    checkAuth();
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p>Cargando...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <Layout>{children}</Layout>;
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/case-files"
          element={
            <ProtectedRoute>
              <CaseFileList />
            </ProtectedRoute>
          }
        />
        <Route
          path="/case-files/new"
          element={
            <ProtectedRoute>
              <CaseFileForm />
            </ProtectedRoute>
          }
        />
        <Route
          path="/case-files/:id"
          element={
            <ProtectedRoute>
              <CaseFileDetail />
            </ProtectedRoute>
          }
        />
        <Route
          path="/alerts"
          element={
            <ProtectedRoute>
              <Alerts />
            </ProtectedRoute>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;