import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  MessageSquare,
  Database,
  FileBarChart,
  PanelsTopLeft,
  Lightbulb,
  Settings,
  Plus,
  Server
} from 'lucide-react';
import { Button } from '../common/Button';

interface SidebarProps {
  onAddDataSource: () => void;
  isOpen?: boolean;
  onClose?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ onAddDataSource }) => {
  const location = useLocation();
  const navItems = [
    { label: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { label: 'Analytics Assistant', path: '/analytics', icon: MessageSquare, badge: 'AI' },
    { label: 'Data Sources', path: '/data-sources', icon: Database },
    { label: 'Reports', path: '/reports', icon: FileBarChart },
    { label: 'Dashboards', path: '/dashboards', icon: PanelsTopLeft },
    { label: 'Insights', path: '/insights', icon: Lightbulb },
    { label: 'Settings', path: '/settings', icon: Settings },
  ];

  const connectedSystems = [
    { name: 'ERP', domain: 'Operations & POs', color: 'bg-emerald-400' },
    { name: 'CRM', domain: 'Customers & Leads', color: 'bg-emerald-400' },
    { name: 'HRMS', domain: 'Workforce & Directory', color: 'bg-emerald-400' },
    { name: 'E-Commerce', domain: 'Orders & Sales', color: 'bg-emerald-400' },
  ];

  return (
    <aside className="w-64 bg-[#0B0F19] border-r border-slate-800/80 flex flex-col h-screen fixed left-0 top-0 z-30 select-none">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-800/80 flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-700 flex items-center justify-center shadow-md shadow-emerald-950/40">
          <Server className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="font-bold text-white text-base tracking-tight leading-none">FreshMart</h1>
          <span className="text-[11px] font-medium text-emerald-400 tracking-wider uppercase">Agentic Analytics</span>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = item.path === '/dashboard'
            ? location.pathname.startsWith('/dashboard')
            : location.pathname === item.path;

          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={
                `flex items-center justify-between px-3.5 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-emerald-600/15 text-emerald-400 border border-emerald-500/25 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`
              }
            >
              <div className="flex items-center gap-3">
                <Icon className="w-4 h-4" />
                <span>{item.label}</span>
              </div>
              {item.badge && (
                <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-emerald-500/20 text-emerald-300">
                  {item.badge}
                </span>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* Connected Systems & Data Sources Box */}
      <div className="p-4 border-t border-slate-800/80 bg-[#080C14]">
        <div className="flex items-center justify-between mb-2.5">
          <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">Connected Systems</span>
          <span className="text-[10px] text-emerald-400 font-mono">4/4 Unified</span>
        </div>

        <div className="space-y-1.5 mb-3">
          {connectedSystems.map((sys) => (
            <div key={sys.name} className="flex items-center justify-between text-xs py-1 px-2 rounded bg-slate-900/60 border border-slate-800/40">
              <span className="text-slate-300 font-medium">{sys.name}</span>
              <div className="flex items-center gap-1.5">
                <span className={`w-1.5 h-1.5 rounded-full ${sys.color} animate-pulse`}></span>
                <span className="text-[11px] text-slate-400">Connected</span>
              </div>
            </div>
          ))}
        </div>

        <Button
          onClick={onAddDataSource}
          variant="outline"
          size="sm"
          className="w-full text-xs border-dashed border-slate-700 hover:border-emerald-500/50 text-slate-300 hover:text-emerald-400"
          icon={<Plus className="w-3.5 h-3.5" />}
        >
          Add Data Source
        </Button>
      </div>
    </aside>
  );
};
