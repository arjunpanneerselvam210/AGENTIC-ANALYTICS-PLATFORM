import React, { useState, useEffect, useMemo } from 'react';
import {
  Users,
  UserPlus,
  Shield,
  Search,
  CheckCircle2,
  AlertCircle,
  Edit2,
  Eye,
  EyeOff,
  Filter,
  Check,
  RefreshCw,
  Building,
  KeyRound,
  ShieldAlert,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { adminApi, type EmployeeDirectoryItem, type RoleResponse } from '../services/adminApi';

export const UserManagement: React.FC = () => {
  const { user: currentUser, refreshProfile } = useAuth();
  const [employees, setEmployees] = useState<EmployeeDirectoryItem[]>([]);
  const [roles, setRoles] = useState<RoleResponse[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Active Main Subtab: 'workforce' | 'roles'
  const [activeAdminTab, setActiveAdminTab] = useState<'workforce' | 'roles'>('workforce');

  // Filters
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [accountFilter, setAccountFilter] = useState<'all' | 'has_account' | 'no_account'>('all');
  const [selectedDept, setSelectedDept] = useState<string>('all');
  const [selectedRoleFilter, setSelectedRoleFilter] = useState<string>('all');

  // Provisioning Modal State
  const [provisionModalOpen, setProvisionModalOpen] = useState<boolean>(false);
  const [targetEmployee, setTargetEmployee] = useState<EmployeeDirectoryItem | null>(null);
  const [provisionUsername, setProvisionUsername] = useState<string>('');
  const [provisionPassword, setProvisionPassword] = useState<string>('');
  const [showPassword, setShowPassword] = useState<boolean>(false);
  const [provisionRole, setProvisionRole] = useState<string>('SALES_MANAGER');
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [modalError, setModalError] = useState<string | null>(null);

  // Edit Role Modal State
  const [editRoleModalOpen, setEditRoleModalOpen] = useState<boolean>(false);
  const [targetUser, setTargetUser] = useState<EmployeeDirectoryItem | null>(null);
  const [newRole, setNewRole] = useState<string>('');

  // Fetch Directory & Roles
  const loadData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [dirData, rolesData] = await Promise.all([
        adminApi.getDirectory(),
        adminApi.getRoles(),
      ]);
      setEmployees(dirData);
      setRoles(rolesData);
    } catch (err: any) {
      console.error('Failed to load employee directory:', err);
      setError(err.response?.data?.detail || 'Failed to load employee directory from server.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // Unique departments for filter
  const departments = useMemo(() => {
    const set = new Set(employees.map((e) => e.department));
    return Array.from(set).sort();
  }, [employees]);

  // Filtered employees list
  const filteredEmployees = useMemo(() => {
    return employees.filter((emp) => {
      // Account filter
      if (accountFilter === 'has_account' && !emp.has_account) return false;
      if (accountFilter === 'no_account' && emp.has_account) return false;

      // Department filter
      if (selectedDept !== 'all' && emp.department !== selectedDept) return false;

      // Role filter
      if (selectedRoleFilter !== 'all' && emp.role_name !== selectedRoleFilter) return false;

      // Search query
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const matchesName = emp.full_name.toLowerCase().includes(q);
        const matchesId = emp.employee_id.toLowerCase().includes(q);
        const matchesEmail = emp.email.toLowerCase().includes(q);
        const matchesUsername = emp.username?.toLowerCase().includes(q);
        const matchesTitle = emp.job_title.toLowerCase().includes(q);
        return matchesName || matchesId || matchesEmail || matchesUsername || matchesTitle;
      }

      return true;
    });
  }, [employees, accountFilter, selectedDept, selectedRoleFilter, searchQuery]);

  // Counts
  const totalEmployees = employees.length;
  const withAccounts = employees.filter((e) => e.has_account).length;
  const withoutAccounts = totalEmployees - withAccounts;

  // Helper to generate cryptographically random temporary password
  const generateSecureTempPassword = (): string => {
    const uppercase = 'ABCDEFGHJKLMNPQRSTUVWXYZ';
    const lowercase = 'abcdefghijkmnpqrstuvwxyz';
    const numbers = '23456789';
    const symbols = '!@#$%&*';
    const all = uppercase + lowercase + numbers + symbols;
    let pwd = 'FM-';
    for (let i = 0; i < 8; i++) {
      pwd += all.charAt(Math.floor(Math.random() * all.length));
    }
    return pwd + '!';
  };

  // Open Provisioning Modal
  const handleOpenProvision = (emp: EmployeeDirectoryItem) => {
    setTargetEmployee(emp);
    const suggestedUsername = `${emp.first_name.toLowerCase()}.${emp.last_name.toLowerCase()}`.replace(/\s+/g, '');
    setProvisionUsername(suggestedUsername);
    setProvisionPassword(generateSecureTempPassword());
    setProvisionRole('SALES_MANAGER');
    setModalError(null);
    setProvisionModalOpen(true);
  };

  // Submit Provisioning
  const handleProvisionSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!targetEmployee) return;

    setIsSubmitting(true);
    setModalError(null);

    try {
      await adminApi.provisionAccount({
        employee_id: targetEmployee.employee_id,
        username: provisionUsername.trim(),
        password: provisionPassword,
        role_name: provisionRole,
      });

      setProvisionModalOpen(false);
      setSuccessMessage(
        `Successfully provisioned application account '${provisionUsername}' for ${targetEmployee.full_name} (${provisionRole})!`
      );
      setTimeout(() => setSuccessMessage(null), 5000);
      await loadData();
    } catch (err: any) {
      console.error('Provisioning failed:', err);
      setModalError(err.response?.data?.detail || 'Failed to provision application account.');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Open Edit Role Modal
  const handleOpenEditRole = (emp: EmployeeDirectoryItem) => {
    if (emp.user_id === currentUser?.user_id) {
      alert('Security Protection: You cannot modify your own application role.');
      return;
    }
    setTargetUser(emp);
    setNewRole(emp.role_name || 'SALES_MANAGER');
    setModalError(null);
    setEditRoleModalOpen(true);
  };

  // Submit Role Change
  const handleEditRoleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!targetUser || !targetUser.user_id) return;

    setIsSubmitting(true);
    setModalError(null);

    try {
      await adminApi.updateRole(targetUser.user_id, newRole);
      setEditRoleModalOpen(false);
      setSuccessMessage(
        `Successfully updated ${targetUser.full_name}'s role to ${newRole} (synchronized across PostgreSQL RBAC and MySQL Workforce)!`
      );
      setTimeout(() => setSuccessMessage(null), 5000);
      await loadData();
      if (refreshProfile) {
        await refreshProfile();
      }
    } catch (err: any) {
      console.error('Role update failed:', err);
      setModalError(err.response?.data?.detail || 'Failed to update user role.');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Toggle Account Status (Disable / Enable)
  const handleToggleStatus = async (emp: EmployeeDirectoryItem) => {
    if (!emp.user_id) return;
    if (emp.user_id === currentUser?.user_id) {
      alert('Security Protection: You cannot disable your own application account.');
      return;
    }

    const action = emp.is_active ? 'disable' : 'reactivate';
    if (!window.confirm(`Are you sure you want to ${action} application access for ${emp.full_name}?`)) {
      return;
    }

    try {
      await adminApi.toggleStatus(emp.user_id, !emp.is_active);
      setSuccessMessage(
        `Application account for ${emp.full_name} has been ${emp.is_active ? 'disabled' : 'reactivated'} successfully.`
      );
      setTimeout(() => setSuccessMessage(null), 5000);
      await loadData();
    } catch (err: any) {
      console.error('Status toggle failed:', err);
      alert(err.response?.data?.detail || 'Failed to change account status.');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/60 p-5 rounded-xl border border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
              <Shield className="w-4 h-4" />
            </div>
            <h1 className="text-xl font-bold text-white tracking-tight">User & Role Management</h1>
            <Badge variant="success" className="ml-2 text-[10px] uppercase font-bold tracking-wider">
              CEO Administration
            </Badge>
          </div>
          <p className="text-slate-400 text-xs mt-1">
            Provision and manage PostgreSQL application login accounts for existing MySQL FreshMart workforce employees.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="secondary"
            size="sm"
            onClick={loadData}
            disabled={isLoading}
            className="text-xs gap-1.5"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </Button>
        </div>
      </div>

      {/* Global Success / Error Alerts */}
      {successMessage && (
        <div className="p-4 rounded-lg bg-emerald-950/40 border border-emerald-500/30 flex items-center gap-3 text-emerald-300 text-xs animate-in fade-in duration-200">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>{successMessage}</span>
        </div>
      )}
      {error && (
        <div className="p-4 rounded-lg bg-rose-950/40 border border-rose-500/30 flex items-center gap-3 text-rose-300 text-xs">
          <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Sub-Tabs: Workforce Accounts vs Roles & RBAC Catalog */}
      <div className="flex items-center gap-2 border-b border-slate-800 pb-2">
        <button
          onClick={() => setActiveAdminTab('workforce')}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
            activeAdminTab === 'workforce'
              ? 'bg-emerald-600/20 text-emerald-400 border border-emerald-500/30 shadow-sm'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40 border border-transparent'
          }`}
        >
          <Users className="w-3.5 h-3.5" />
          <span>Workforce Accounts Directory</span>
          <span className="text-[10px] bg-slate-800 text-slate-300 font-mono px-1.5 py-0.5 rounded-full">
            {totalEmployees}
          </span>
        </button>

        <button
          onClick={() => setActiveAdminTab('roles')}
          className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
            activeAdminTab === 'roles'
              ? 'bg-emerald-600/20 text-emerald-400 border border-emerald-500/30 shadow-sm'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40 border border-transparent'
          }`}
        >
          <Shield className="w-3.5 h-3.5" />
          <span>Roles & RBAC Permissions Catalog</span>
          <span className="text-[10px] bg-emerald-500/20 text-emerald-300 font-mono px-1.5 py-0.5 rounded-full font-bold">
            {roles.length || 7} Roles
          </span>
        </button>
      </div>

      {activeAdminTab === 'workforce' ? (
        <>
          {/* Metric Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <Card className="p-4 flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-slate-800 flex items-center justify-center text-slate-300">
                <Building className="w-5 h-5" />
              </div>
              <div>
                <span className="text-[11px] text-slate-400 font-medium uppercase tracking-wider block">Total MySQL Employees</span>
                <span className="text-xl font-bold text-white">{totalEmployees}</span>
              </div>
            </Card>

            <Card className="p-4 flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
                <Users className="w-5 h-5" />
              </div>
              <div>
                <span className="text-[11px] text-slate-400 font-medium uppercase tracking-wider block">Provisioned Logins</span>
                <span className="text-xl font-bold text-emerald-400">{withAccounts}</span>
              </div>
            </Card>

            <Card className="p-4 flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
                <KeyRound className="w-5 h-5" />
              </div>
              <div>
                <span className="text-[11px] text-slate-400 font-medium uppercase tracking-wider block">Unprovisioned Employees</span>
                <span className="text-xl font-bold text-amber-400">{withoutAccounts}</span>
              </div>
            </Card>
          </div>

          {/* Filter and Search Bar */}
          <Card className="p-4 space-y-3">
            <div className="flex flex-col md:flex-row gap-3 items-stretch md:items-center justify-between">
              {/* Search Input */}
              <div className="relative flex-1">
                <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
                <input
                  type="text"
                  placeholder="Search by employee name, ID (e.g. E008), email, or username..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700/80 rounded-lg pl-9 pr-4 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-emerald-500"
                />
              </div>

              {/* Department & Role Filters */}
              <div className="flex items-center gap-2 flex-wrap">
                <div className="flex items-center gap-1.5 bg-slate-900 border border-slate-700/80 rounded-lg px-2.5 py-1">
                  <Filter className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                  <select
                    value={selectedDept}
                    onChange={(e) => setSelectedDept(e.target.value)}
                    className="bg-transparent text-xs text-slate-300 focus:outline-none cursor-pointer"
                  >
                    <option value="all" className="bg-slate-900">All Depts ({departments.length})</option>
                    {departments.map((d) => (
                      <option key={d} value={d} className="bg-slate-900">
                        {d}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="flex items-center gap-1.5 bg-slate-900 border border-slate-700/80 rounded-lg px-2.5 py-1">
                  <Shield className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                  <select
                    value={selectedRoleFilter}
                    onChange={(e) => setSelectedRoleFilter(e.target.value)}
                    className="bg-transparent text-xs text-slate-300 focus:outline-none cursor-pointer"
                  >
                    <option value="all" className="bg-slate-900">All Roles</option>
                    <option value="CEO" className="bg-slate-900">CEO</option>
                    <option value="SALES_MANAGER" className="bg-slate-900">SALES_MANAGER</option>
                    <option value="FINANCE_MANAGER" className="bg-slate-900">FINANCE_MANAGER</option>
                    <option value="HR_MANAGER" className="bg-slate-900">HR_MANAGER</option>
                    <option value="INVENTORY_MANAGER" className="bg-slate-900">INVENTORY_MANAGER</option>
                    <option value="ERP_MANAGER" className="bg-slate-900">ERP_MANAGER</option>
                    <option value="ADMIN" className="bg-slate-900">ADMIN</option>
                  </select>
                </div>
              </div>
            </div>

        {/* Account Status Filter Tabs */}
        <div className="flex items-center gap-2 border-t border-slate-800/80 pt-3">
          <span className="text-[11px] text-slate-400 font-medium mr-2">Show:</span>
          <button
            onClick={() => setAccountFilter('all')}
            className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
              accountFilter === 'all'
                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            All Employees ({totalEmployees})
          </button>
          <button
            onClick={() => setAccountFilter('has_account')}
            className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
              accountFilter === 'has_account'
                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            Provisioned Logins ({withAccounts})
          </button>
          <button
            onClick={() => setAccountFilter('no_account')}
            className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
              accountFilter === 'no_account'
                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            No Login Account ({withoutAccounts})
          </button>
        </div>
      </Card>

      {/* Employees Directory Table */}
      <Card className="overflow-hidden border border-slate-800">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/90 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
              <tr>
                <th className="py-3 px-4">Employee</th>
                <th className="py-3 px-4">Department & Role</th>
                <th className="py-3 px-4">Application Login</th>
                <th className="py-3 px-4">Application Role</th>
                <th className="py-3 px-4">Account Status</th>
                <th className="py-3 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {isLoading ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-slate-500">
                    <div className="flex flex-col items-center gap-2">
                      <RefreshCw className="w-5 h-5 animate-spin text-emerald-500" />
                      <span>Loading workforce directory from MySQL and PostgreSQL...</span>
                    </div>
                  </td>
                </tr>
              ) : filteredEmployees.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-slate-500">
                    No workforce records found matching your filters.
                  </td>
                </tr>
              ) : (
                filteredEmployees.map((emp) => {
                  const isCurrent = emp.user_id === currentUser?.user_id;

                  return (
                    <tr key={emp.employee_id} className="hover:bg-slate-800/30 transition-colors">
                      {/* Employee Info */}
                      <td className="py-3 px-4">
                        <div className="flex items-center gap-2.5">
                          <div className="w-7 h-7 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300 font-bold text-[11px] shrink-0">
                            {emp.first_name[0]}
                            {emp.last_name[0]}
                          </div>
                          <div>
                            <div className="font-semibold text-white flex items-center gap-1.5">
                              <span>{emp.full_name}</span>
                              <span className="text-[10px] font-mono text-slate-400 bg-slate-900 px-1 py-0.5 rounded border border-slate-800">
                                {emp.employee_id}
                              </span>
                            </div>
                            <span className="text-[11px] text-slate-400 block">{emp.email}</span>
                          </div>
                        </div>
                      </td>

                      {/* Department & Job Title */}
                      <td className="py-3 px-4">
                        <span className="text-slate-200 font-medium block">{emp.department}</span>
                        <span className="text-[11px] text-slate-400">{emp.job_title}</span>
                      </td>

                      {/* Application Login Username */}
                      <td className="py-3 px-4">
                        {emp.has_account ? (
                          <div className="flex items-center gap-1.5">
                            <span className="text-emerald-400 font-mono font-medium bg-emerald-950/40 border border-emerald-500/20 px-2 py-0.5 rounded text-[11px]">
                              @{emp.username}
                            </span>
                            {isCurrent && (
                              <span className="text-[9px] bg-slate-800 text-slate-400 px-1 rounded">You</span>
                            )}
                          </div>
                        ) : (
                          <span className="text-slate-500 italic text-[11px]">No application account</span>
                        )}
                      </td>

                      {/* Assigned Application Role */}
                      <td className="py-3 px-4">
                        {emp.has_account && emp.role_name ? (
                          <Badge
                            variant={
                              emp.role_name === 'CEO'
                                ? 'purple'
                                : emp.role_name === 'FINANCE_MANAGER'
                                ? 'warning'
                                : emp.role_name === 'HR_MANAGER'
                                ? 'info'
                                : 'success'
                            }
                            className="font-mono text-[10px]"
                          >
                            {emp.role_name}
                          </Badge>
                        ) : (
                          <span className="text-slate-600">—</span>
                        )}
                      </td>

                      {/* Status */}
                      <td className="py-3 px-4">
                        {emp.has_account ? (
                          emp.is_active ? (
                            <span className="inline-flex items-center gap-1.5 text-emerald-400 text-[11px] font-medium">
                              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                              Active
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1.5 text-rose-400 text-[11px] font-medium">
                              <span className="w-1.5 h-1.5 rounded-full bg-rose-400"></span>
                              Disabled
                            </span>
                          )
                        ) : (
                          <span className="text-slate-600 text-[11px]">Unprovisioned</span>
                        )}
                      </td>

                      {/* Actions */}
                      <td className="py-3 px-4 text-right">
                        {emp.has_account ? (
                          <div className="flex items-center justify-end gap-1.5">
                            <Button
                              variant="secondary"
                              size="sm"
                              disabled={isCurrent}
                              onClick={() => handleOpenEditRole(emp)}
                              className="text-[11px] py-1 px-2.5 gap-1"
                              title={isCurrent ? 'Cannot modify your own role' : 'Change application role'}
                            >
                              <Edit2 className="w-3 h-3" />
                              <span>Edit Role</span>
                            </Button>
                            <Button
                              variant={emp.is_active ? 'secondary' : 'primary'}
                              size="sm"
                              disabled={isCurrent}
                              onClick={() => handleToggleStatus(emp)}
                              className={`text-[11px] py-1 px-2.5 ${
                                emp.is_active
                                  ? 'text-rose-400 hover:text-rose-300 hover:bg-rose-950/30'
                                  : 'text-emerald-400'
                              }`}
                              title={isCurrent ? 'Cannot disable your own account' : 'Toggle account active status'}
                            >
                              {emp.is_active ? 'Disable' : 'Enable'}
                            </Button>
                          </div>
                        ) : (
                          <Button
                            variant="primary"
                            size="sm"
                            onClick={() => handleOpenProvision(emp)}
                            className="text-[11px] py-1 px-3 gap-1.5"
                          >
                            <UserPlus className="w-3 h-3" />
                            <span>Create Login Account</span>
                          </Button>
                        )}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </Card>
      </>
      ) : (
        /* ROLES & RBAC PERMISSIONS CATALOG TAB */
        <div className="space-y-6">
          {/* Roles Overview Header */}
          <div className="p-4 bg-slate-900/60 rounded-xl border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <Shield className="w-4 h-4 text-emerald-400" />
                <span>Enterprise RBAC Security Roles & Granted Permissions</span>
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                PostgreSQL authoritative security matrix governing data domain boundaries and AI query generation scopes.
              </p>
            </div>
            <span className="text-xs font-mono text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-lg border border-emerald-500/20 self-start sm:self-auto">
              {roles.length} Configured Application Roles
            </span>
          </div>

          {/* Role Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {roles.map((r) => {
              const assignedCount = employees.filter((e) => e.role_name === r.role_name).length;
              const isCeo = r.role_name === 'CEO';
              const isManager = r.role_name.includes('MANAGER');

              return (
                <Card
                  key={r.role_id}
                  className="p-5 flex flex-col justify-between border-slate-800 hover:border-slate-700 transition-all bg-gradient-to-b from-slate-900/80 to-[#0A0E1A]"
                >
                  <div className="space-y-3">
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <div className="flex items-center gap-2">
                          <h3 className="font-bold text-white text-sm tracking-tight">{r.role_name}</h3>
                        </div>
                        <span className="text-[11px] text-slate-400 font-medium block mt-0.5">
                          {isCeo
                            ? 'Enterprise-wide Executive'
                            : isManager
                            ? 'Domain Operations Lead'
                            : 'System Administration'}
                        </span>
                      </div>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700 font-semibold shrink-0">
                        {assignedCount} {assignedCount === 1 ? 'User' : 'Users'}
                      </span>
                    </div>

                    <p className="text-xs text-slate-300 leading-relaxed bg-slate-950/40 p-2.5 rounded-lg border border-slate-800/60">
                      {r.description || 'Application access role with domain-scoped query permissions.'}
                    </p>

                    <div>
                      <span className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold block mb-1.5">
                        Granted Permissions ({r.permissions.length}):
                      </span>
                      <div className="flex flex-wrap gap-1 max-h-28 overflow-y-auto pr-1">
                        {r.permissions.map((perm) => (
                          <span
                            key={perm}
                            className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950/40 text-emerald-300 border border-emerald-500/20"
                          >
                            {perm}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>

                  <div className="pt-4 mt-4 border-t border-slate-800/80 flex items-center justify-between gap-2">
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={() => {
                        setSelectedRoleFilter(r.role_name);
                        setActiveAdminTab('workforce');
                      }}
                      className="text-xs w-full justify-center gap-1.5"
                    >
                      <Users className="w-3 h-3 text-slate-400" />
                      <span>View Users ({assignedCount})</span>
                    </Button>
                  </div>
                </Card>
              );
            })}
          </div>

          {/* Interactive RBAC Permission Matrix Table */}
          <Card className="overflow-hidden border border-slate-800">
            <div className="p-4 border-b border-slate-800 flex items-center justify-between">
              <div>
                <h3 className="font-bold text-white text-sm flex items-center gap-2">
                  <KeyRound className="w-4 h-4 text-emerald-400" />
                  <span>Granular Role-to-Permission Access Control Matrix</span>
                </h3>
                <p className="text-xs text-slate-400">
                  Comprehensive audit view of all 11 security permission codes enforced by PostgreSQL and MCP guardrails
                </p>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-900/90 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
                  <tr>
                    <th className="py-3 px-4">Role Name</th>
                    <th className="py-3 px-3 text-center">VIEW_SALES</th>
                    <th className="py-3 px-3 text-center">VIEW_FINANCE</th>
                    <th className="py-3 px-3 text-center">VIEW_HR</th>
                    <th className="py-3 px-3 text-center">VIEW_SALARY</th>
                    <th className="py-3 px-3 text-center">VIEW_STOCK</th>
                    <th className="py-3 px-3 text-center">VIEW_PURCHASES</th>
                    <th className="py-3 px-3 text-center">VIEW_EXPENSES</th>
                    <th className="py-3 px-3 text-center">VIEW_PROFIT</th>
                    <th className="py-3 px-3 text-center">VIEW_CRM</th>
                    <th className="py-3 px-3 text-center">ADMIN</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 font-mono">
                  {roles.map((r) => {
                    const pSet = new Set(r.permissions);
                    return (
                      <tr key={r.role_id} className="hover:bg-slate-800/30 transition-colors">
                        <td className="py-3 px-4 font-sans font-bold text-white flex items-center gap-2">
                          <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                          <span>{r.role_name}</span>
                        </td>
                        <td className="py-3 px-3 text-center">
                          {pSet.has('VIEW_SALES') ? (
                            <Check className="w-4 h-4 text-emerald-400 mx-auto" />
                          ) : (
                            <span className="text-slate-600">-</span>
                          )}
                        </td>
                        <td className="py-3 px-3 text-center">
                          {pSet.has('VIEW_FINANCE') ? (
                            <Check className="w-4 h-4 text-emerald-400 mx-auto" />
                          ) : (
                            <span className="text-slate-600">-</span>
                          )}
                        </td>
                        <td className="py-3 px-3 text-center">
                          {pSet.has('VIEW_HR') ? (
                            <Check className="w-4 h-4 text-emerald-400 mx-auto" />
                          ) : (
                            <span className="text-slate-600">-</span>
                          )}
                        </td>
                        <td className="py-3 px-3 text-center">
                          {pSet.has('VIEW_EMPLOYEE_SALARY') ? (
                            <Check className="w-4 h-4 text-emerald-400 mx-auto" />
                          ) : (
                            <span className="text-slate-600">-</span>
                          )}
                        </td>
                        <td className="py-3 px-3 text-center">
                          {pSet.has('VIEW_INVENTORY') ? (
                            <Check className="w-4 h-4 text-emerald-400 mx-auto" />
                          ) : (
                            <span className="text-slate-600">-</span>
                          )}
                        </td>
                        <td className="py-3 px-3 text-center">
                          {pSet.has('VIEW_PURCHASES') ? (
                            <Check className="w-4 h-4 text-emerald-400 mx-auto" />
                          ) : (
                            <span className="text-slate-600">-</span>
                          )}
                        </td>
                        <td className="py-3 px-3 text-center">
                          {pSet.has('VIEW_EXPENSES') ? (
                            <Check className="w-4 h-4 text-emerald-400 mx-auto" />
                          ) : (
                            <span className="text-slate-600">-</span>
                          )}
                        </td>
                        <td className="py-3 px-3 text-center">
                          {pSet.has('VIEW_PROFIT') ? (
                            <Check className="w-4 h-4 text-emerald-400 mx-auto" />
                          ) : (
                            <span className="text-slate-600">-</span>
                          )}
                        </td>
                        <td className="py-3 px-3 text-center">
                          {pSet.has('VIEW_CRM') ? (
                            <Check className="w-4 h-4 text-emerald-400 mx-auto" />
                          ) : (
                            <span className="text-slate-600">-</span>
                          )}
                        </td>
                        <td className="py-3 px-3 text-center">
                          {pSet.has('MANAGE_USERS') ? (
                            <Check className="w-4 h-4 text-cyan-400 mx-auto" />
                          ) : (
                            <span className="text-slate-600">-</span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      )}

      {/* MODAL 1: Create Login Account */}
      {provisionModalOpen && targetEmployee && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <Card className="w-full max-w-md p-6 bg-slate-900 border-slate-700 shadow-2xl animate-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
                  <UserPlus className="w-4 h-4" />
                </div>
                <h3 className="font-bold text-white text-sm">Provision Application Login</h3>
              </div>
              <button
                onClick={() => setProvisionModalOpen(false)}
                className="text-slate-400 hover:text-white"
              >
                ✕
              </button>
            </div>

            {/* Read-Only Employee Context */}
            <div className="my-4 p-3 bg-slate-800/60 rounded-lg border border-slate-700/60 text-xs">
              <span className="text-[10px] text-slate-400 uppercase tracking-wider block font-semibold">
                Existing MySQL Employee
              </span>
              <div className="font-bold text-white text-sm mt-0.5">{targetEmployee.full_name}</div>
              <div className="text-slate-400 mt-0.5">
                {targetEmployee.job_title} • {targetEmployee.department} ({targetEmployee.employee_id})
              </div>
              <div className="text-[11px] text-slate-400 font-mono mt-1">{targetEmployee.email}</div>
            </div>

            {modalError && (
              <div className="mb-4 p-3 rounded bg-rose-950/50 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{modalError}</span>
              </div>
            )}

            <form onSubmit={handleProvisionSubmit} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-300 font-medium mb-1">
                  Application Username <span className="text-emerald-400">*</span>
                </label>
                <input
                  type="text"
                  required
                  value={provisionUsername}
                  onChange={(e) => setProvisionUsername(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-white font-mono focus:outline-none focus:border-emerald-500"
                  placeholder="e.g. rohan.mehta"
                />
              </div>

              <div>
                <div className="flex items-center justify-between mb-1">
                  <label className="text-slate-300 font-medium">
                    Temporary Password <span className="text-emerald-400">*</span>
                  </label>
                  <button
                    type="button"
                    onClick={() => setProvisionPassword(generateSecureTempPassword())}
                    className="text-[11px] text-emerald-400 hover:text-emerald-300 underline font-sans"
                  >
                    🎲 Regenerate
                  </button>
                </div>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    required
                    value={provisionPassword}
                    onChange={(e) => setProvisionPassword(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg pl-3 pr-9 py-2 text-white font-mono focus:outline-none focus:border-emerald-500"
                    placeholder="Min 6 characters"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-2.5 top-2.5 text-slate-400 hover:text-white"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
                <span className="text-[10px] text-slate-500 mt-1 block">
                  Password will be hashed using Bcrypt before storage in PostgreSQL.
                </span>
              </div>

              <div>
                <label className="block text-slate-300 font-medium mb-1">
                  Application Role <span className="text-emerald-400">*</span>
                </label>
                <select
                  value={provisionRole}
                  onChange={(e) => setProvisionRole(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-emerald-500"
                >
                  {roles.length > 0
                    ? roles
                        .filter((r) => r.role_name !== 'ADMIN')
                        .map((r) => (
                          <option key={r.role_id} value={r.role_name}>
                            {r.role_name} {r.description ? `(${r.description.split('.')[0]})` : ''}
                          </option>
                        ))
                    : (
                      <>
                        <option value="SALES_MANAGER">SALES_MANAGER (Sales & CRM Analytics)</option>
                        <option value="FINANCE_MANAGER">FINANCE_MANAGER (P&L & Expense Analytics)</option>
                        <option value="HR_MANAGER">HR_MANAGER (Workforce & Salary Analytics)</option>
                        <option value="INVENTORY_MANAGER">INVENTORY_MANAGER (Stock & Warehouses)</option>
                        <option value="ERP_MANAGER">ERP_MANAGER (Procurement & Operations)</option>
                        <option value="CEO">CEO (Enterprise-wide Executive Access)</option>
                      </>
                    )}
                </select>
              </div>

              <div className="p-2.5 rounded bg-emerald-950/20 border border-emerald-500/20 text-[11px] text-emerald-300 flex items-start gap-2">
                <ShieldAlert className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                <span>
                  Provisions a login in PostgreSQL for this employee. The employee record in MySQL is never duplicated or modified.
                </span>
              </div>

              <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-800">
                <Button
                  type="button"
                  variant="secondary"
                  size="sm"
                  onClick={() => setProvisionModalOpen(false)}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  variant="primary"
                  size="sm"
                  disabled={isSubmitting}
                  className="gap-1.5"
                >
                  {isSubmitting ? (
                    <>
                      <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                      <span>Provisioning...</span>
                    </>
                  ) : (
                    <>
                      <Check className="w-3.5 h-3.5" />
                      <span>Create Account</span>
                    </>
                  )}
                </Button>
              </div>
            </form>
          </Card>
        </div>
      )}

      {/* MODAL 2: Edit Application Role */}
      {editRoleModalOpen && targetUser && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <Card className="w-full max-w-sm p-6 bg-slate-900 border-slate-700 shadow-2xl animate-in zoom-in-95 duration-150">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
                  <Edit2 className="w-4 h-4" />
                </div>
                <h3 className="font-bold text-white text-sm">Change Application Role</h3>
              </div>
              <button
                onClick={() => setEditRoleModalOpen(false)}
                className="text-slate-400 hover:text-white"
              >
                ✕
              </button>
            </div>

            <div className="my-4 p-3 bg-slate-800/60 rounded-lg border border-slate-700/60 text-xs">
              <div className="font-bold text-white">{targetUser.full_name}</div>
              <div className="text-slate-400 mt-0.5">
                Username: <span className="text-emerald-400 font-mono">@{targetUser.username}</span>
              </div>
              <div className="text-slate-400 mt-0.5">
                Current Role: <span className="font-mono text-white">{targetUser.role_name}</span>
              </div>
            </div>

            {modalError && (
              <div className="mb-4 p-3 rounded bg-rose-950/50 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{modalError}</span>
              </div>
            )}

            <form onSubmit={handleEditRoleSubmit} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-300 font-medium mb-1">Select New Role</label>
                <select
                  value={newRole}
                  onChange={(e) => setNewRole(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-emerald-500"
                >
                  {roles.length > 0
                    ? roles
                        .filter((r) => r.role_name !== 'ADMIN')
                        .map((r) => (
                          <option key={r.role_id} value={r.role_name}>
                            {r.role_name}
                          </option>
                        ))
                    : (
                      <>
                        <option value="SALES_MANAGER">SALES_MANAGER</option>
                        <option value="FINANCE_MANAGER">FINANCE_MANAGER</option>
                        <option value="HR_MANAGER">HR_MANAGER</option>
                        <option value="INVENTORY_MANAGER">INVENTORY_MANAGER</option>
                        <option value="ERP_MANAGER">ERP_MANAGER</option>
                        <option value="CEO">CEO</option>
                      </>
                    )}
                </select>
              </div>

              <span className="text-[11px] text-slate-400 block">
                Updates PostgreSQL RBAC role mapping immediately. The user will receive updated permissions upon their next authentication or session refresh.
              </span>

              <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-800">
                <Button
                  type="button"
                  variant="secondary"
                  size="sm"
                  onClick={() => setEditRoleModalOpen(false)}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  variant="primary"
                  size="sm"
                  disabled={isSubmitting}
                  className="gap-1.5"
                >
                  {isSubmitting ? 'Saving...' : 'Save Role'}
                </Button>
              </div>
            </form>
          </Card>
        </div>
      )}
    </div>
  );
};
