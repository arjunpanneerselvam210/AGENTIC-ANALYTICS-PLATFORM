import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth, getRoleSlug } from '../context/AuthContext';
import { Layout } from '../components/layout/Layout';
import { Login } from '../pages/Login';
import { RoleDashboard } from '../pages/RoleDashboard';
import { AnalyticsChat } from '../pages/AnalyticsChat';
import { DataSources } from '../pages/DataSources';
import { Reports } from '../pages/Reports';
import { Insights } from '../pages/Insights';
import { Settings } from '../pages/Settings';
import { UserManagement } from '../pages/UserManagement';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" />
          <span className="text-xs text-slate-400">Loading FreshMart Analytics...</span>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

interface RoleProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles: string[];
}

/**
 * Protects direct dashboard URLs based on authoritative user role.
 * Redirects unauthorized attempts to the user's authorized role dashboard.
 */
const RoleProtectedRoute: React.FC<RoleProtectedRouteProps> = ({ children, allowedRoles }) => {
  const { user, isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-12 min-h-[50vh]">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" />
          <span className="text-xs text-slate-400">Verifying security authorization...</span>
        </div>
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />;
  }

  const userRole = user.role;
  if (!allowedRoles.includes(userRole)) {
    const userRoleSlug = getRoleSlug(userRole);
    return <Navigate to={`/dashboard/${userRoleSlug}`} replace />;
  }

  return <>{children}</>;
};

const DashboardRedirect: React.FC = () => {
  const { user } = useAuth();
  const slug = getRoleSlug(user?.role);
  return <Navigate to={`/dashboard/${slug}`} replace />;
};

export const AppRouter: React.FC = () => {
  const { isAuthenticated } = useAuth();

  return (
    <Routes>
      {/* Public Login Route */}
      <Route
        path="/login"
        element={isAuthenticated ? <DashboardRedirect /> : <Login />}
      />

      {/* Protected Routes wrapped in Main Layout */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<DashboardRedirect />} />
        
        {/* Dynamic Role-Specific Dashboard Routes */}
        <Route path="dashboard" element={<DashboardRedirect />} />
        <Route
          path="dashboard/ceo"
          element={
            <RoleProtectedRoute allowedRoles={['CEO', 'ADMIN']}>
              <RoleDashboard roleSlug="ceo" />
            </RoleProtectedRoute>
          }
        />
        <Route
          path="dashboard/sales"
          element={
            <RoleProtectedRoute allowedRoles={['SALES_MANAGER', 'CEO', 'ERP_MANAGER']}>
              <RoleDashboard roleSlug="sales" />
            </RoleProtectedRoute>
          }
        />
        <Route
          path="dashboard/hr"
          element={
            <RoleProtectedRoute allowedRoles={['HR_MANAGER', 'CEO']}>
              <RoleDashboard roleSlug="hr" />
            </RoleProtectedRoute>
          }
        />
        <Route
          path="dashboard/finance"
          element={
            <RoleProtectedRoute allowedRoles={['FINANCE_MANAGER', 'CEO']}>
              <RoleDashboard roleSlug="finance" />
            </RoleProtectedRoute>
          }
        />
        <Route
          path="dashboard/inventory"
          element={
            <RoleProtectedRoute allowedRoles={['INVENTORY_MANAGER', 'CEO', 'SALES_MANAGER', 'ERP_MANAGER']}>
              <RoleDashboard roleSlug="inventory" />
            </RoleProtectedRoute>
          }
        />
        <Route
          path="dashboard/erp"
          element={
            <RoleProtectedRoute allowedRoles={['ERP_MANAGER', 'CEO']}>
              <RoleDashboard roleSlug="erp" />
            </RoleProtectedRoute>
          }
        />

        {/* Existing Analytics Workspace & Operational Pages */}
        <Route path="analytics" element={<AnalyticsChat />} />
        <Route path="data-sources" element={<DataSources />} />
        <Route path="reports" element={<Reports />} />
        <Route path="dashboards" element={<DashboardRedirect />} />
        <Route path="insights" element={<Insights />} />
        <Route path="settings" element={<Settings />} />

        {/* CEO-Only Administration: User & Role Management */}
        <Route
          path="admin/users"
          element={
            <RoleProtectedRoute allowedRoles={['CEO', 'ADMIN']}>
              <UserManagement />
            </RoleProtectedRoute>
          }
        />
      </Route>

      {/* Fallback */}
      <Route path="*" element={<DashboardRedirect />} />
    </Routes>
  );
};
