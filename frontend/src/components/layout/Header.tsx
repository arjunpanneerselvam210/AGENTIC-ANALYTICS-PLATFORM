import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Bell, LogOut, ShieldCheck, ChevronDown, User as UserIcon } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { Badge } from '../common/Badge';

const ROLE_TITLES: Record<string, string> = {
  CEO: 'Chief Executive Officer',
  SALES_MANAGER: 'Sales Manager',
  HR_MANAGER: 'HR Manager',
  FINANCE_MANAGER: 'Finance Manager',
  INVENTORY_MANAGER: 'Inventory Manager',
  ERP_MANAGER: 'ERP Operations Manager',
  ADMIN: 'System Administrator',
};

const ROLE_AREAS: Record<string, string[]> = {
  CEO: ['Revenue & Financials', 'Profit & Margins', 'Workforce & Payroll', 'Sales & CRM', 'Warehouse Inventory', 'Procurement & Operations'],
  SALES_MANAGER: ['Gross Sales & Revenue', 'Sales Order Fulfillment', 'B2B Customers', 'CRM Pipeline & Leads', 'Catalog Products'],
  HR_MANAGER: ['Workforce Directory', 'Employee Salaries & Payroll', 'Department Structure', 'Workforce Expenditures'],
  FINANCE_MANAGER: ['Revenue & Net Profit', 'Operating Expenses & COGS', 'Corporate P&L Trends', 'August Root-Cause Variance'],
  INVENTORY_MANAGER: ['Warehouse Valuation', 'Low-Stock Safety Alerts', 'Catalog Products', 'Supplier Purchase Orders'],
  ERP_MANAGER: ['Procurement Orders & Spend', 'Warehouse Stock Balances', 'Vendor Suppliers', 'Department Expenditures'],
  ADMIN: ['System Configuration', 'User Management', 'RBAC Role Management'],
};

export const Header: React.FC = () => {
  const { user, logout } = useAuth();
  const [searchQuery, setSearchQuery] = useState('');
  const [showUserMenu, setShowUserMenu] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    navigate(`/analytics?q=${encodeURIComponent(searchQuery.trim())}`);
    setSearchQuery('');
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setShowUserMenu(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSignOut = () => {
    setShowUserMenu(false);
    logout();
    navigate('/login');
  };

  const handleProfileClick = () => {
    setShowUserMenu(false);
    navigate('/settings');
  };

  const userRole = user?.role || 'CEO';
  const roleTitle = ROLE_TITLES[userRole] || userRole;
  const authorizedAreas = ROLE_AREAS[userRole] || ['Authorized Enterprise Analytics'];

  return (
    <header className="h-16 bg-[#0B0F19]/90 backdrop-blur-md border-b border-slate-800/80 fixed top-0 right-0 left-64 z-20 px-6 flex items-center justify-between">
      {/* Left: Branding subtitle */}
      <div className="hidden lg:block">
        <h2 className="text-sm font-semibold text-slate-100">FreshMart Agentic Analytics</h2>
        <p className="text-[11px] text-slate-400">AI-Powered Insights for Your Business</p>
      </div>

      {/* Center: Natural Language Query Input (NO MICROPHONE!) */}
      <form onSubmit={handleSearchSubmit} className="flex-1 max-w-xl mx-4">
        <div className="relative flex items-center">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder='Ask your business a question... (e.g. "Why did profit decrease in August?")'
            className="w-full bg-[#080C14] border border-slate-800 focus:border-emerald-500/60 rounded-xl pl-4 pr-11 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-emerald-500/40 transition-all shadow-inner"
          />
          <button
            type="submit"
            className="absolute right-1.5 p-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg transition-colors"
            title="Ask Analytics Assistant"
          >
            <Search className="w-3.5 h-3.5" />
          </button>
        </div>
      </form>

      {/* Right: Notifications & Compact Authenticated User Menu */}
      <div className="flex items-center gap-3">
        {/* Notification Bell */}
        <button
          type="button"
          className="p-2 text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 rounded-lg transition-colors relative"
          title="Notifications"
        >
          <Bell className="w-4 h-4" />
          <span className="w-2 h-2 rounded-full bg-emerald-500 absolute top-1.5 right-1.5 ring-2 ring-[#0B0F19]" />
        </button>

        {/* Compact Authenticated-User Menu */}
        <div className="relative" ref={menuRef}>
          <button
            onClick={() => setShowUserMenu(!showUserMenu)}
            className="flex items-center gap-2.5 p-1.5 pl-2.5 pr-2 rounded-xl bg-slate-900 border border-slate-800 hover:border-slate-700 transition-all text-left"
            aria-expanded={showUserMenu}
          >
            <div className="w-7 h-7 rounded-lg bg-emerald-600/20 border border-emerald-500/30 flex items-center justify-center text-emerald-400 font-semibold text-xs">
              {user?.full_name ? user.full_name.charAt(0) : 'U'}
            </div>
            <div className="hidden sm:block">
              <div className="text-xs font-semibold text-slate-200 leading-tight">
                {user?.full_name || 'Authenticated User'}
              </div>
              <div className="text-[10px] text-emerald-400 flex items-center gap-1 font-mono">
                <ShieldCheck className="w-3 h-3 text-emerald-400 inline" />
                {userRole}
              </div>
            </div>
            <ChevronDown className={`w-3.5 h-3.5 text-slate-400 transition-transform ${showUserMenu ? 'rotate-180' : ''}`} />
          </button>

          {/* Compact Authenticated Profile & Scope Card */}
          {showUserMenu && (
            <div className="absolute right-0 mt-2 w-64 bg-[#0F1626] border border-slate-800 rounded-xl shadow-2xl p-3 z-50 animate-in fade-in slide-in-from-top-2 duration-150">
              {/* User Header */}
              <div className="pb-2.5 border-b border-slate-800/80">
                <div className="flex items-center justify-between">
                  <p className="text-xs font-bold text-white truncate">{user?.full_name || 'Authenticated User'}</p>
                  <Badge variant="emerald" size="sm">{userRole}</Badge>
                </div>
                <p className="text-[11px] text-slate-400 mt-0.5">{roleTitle}</p>
                <p className="text-[10px] font-mono text-emerald-400/90 mt-1">Role: {userRole}</p>
              </div>

              {/* Authorized Areas */}
              <div className="py-2.5 border-b border-slate-800/80">
                <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider mb-1.5">
                  Authorized Areas:
                </p>
                <ul className="space-y-1">
                  {authorizedAreas.map((area) => (
                    <li key={area} className="text-[11px] text-slate-300 flex items-center gap-1.5">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 shrink-0" />
                      <span className="truncate">{area}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Actions: Profile & Sign Out */}
              <div className="pt-2 space-y-1">
                <button
                  onClick={handleProfileClick}
                  className="w-full flex items-center gap-2 px-2.5 py-1.5 text-xs text-slate-300 hover:text-white hover:bg-slate-800/60 rounded-lg transition-colors text-left"
                >
                  <UserIcon className="w-3.5 h-3.5 text-slate-400" />
                  <span>Profile & Permissions</span>
                </button>
                <button
                  onClick={handleSignOut}
                  className="w-full flex items-center gap-2 px-2.5 py-1.5 text-xs text-rose-400 hover:bg-rose-500/10 rounded-lg transition-colors text-left"
                >
                  <LogOut className="w-3.5 h-3.5 text-rose-400" />
                  <span>Sign Out</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
