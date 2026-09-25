import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  PanelsTopLeft,
  Plus,
  ArrowRight,
  Layout,
  Clock,
  Search,
  Building2,
  ShoppingCart,
  DollarSign,
  Users,
  Package,
  Truck,
  Sparkles
} from 'lucide-react';
import { Button } from '../components/common/Button';
import { Card } from '../components/common/Card';
import { Badge } from '../components/common/Badge';
import { useAuth } from '../context/AuthContext';
import { formatISTDate } from '../utils/dateUtils';

interface RealDashboardCard {
  id: string;
  slug: string;
  title: string;
  description: string;
  domain: string;
  icon: any;
  widgetsCount: number;
  kpisCount: number;
  chartsCount: number;
  roles: string[];
  status: 'Live Telemetry' | 'Synchronized';
}

const REAL_SAVED_DASHBOARDS: RealDashboardCard[] = [
  {
    id: 'DASH-01',
    slug: 'ceo',
    title: 'Executive Overview Dashboard',
    description: 'Cross-domain telemetry uniting commercial revenues, gross margins, corporate headcounts, and warehouse inventory.',
    domain: 'Executive',
    icon: Building2,
    widgetsCount: 7,
    kpisCount: 4,
    chartsCount: 3,
    roles: ['CEO', 'ADMIN'],
    status: 'Live Telemetry'
  },
  {
    id: 'DASH-02',
    slug: 'sales',
    title: 'Sales & Commercial Operations',
    description: 'Real-time sales velocity, top grossing SKUs, repeat enterprise customers, and CRM lead conversion funnel.',
    domain: 'Sales & CRM',
    icon: ShoppingCart,
    widgetsCount: 6,
    kpisCount: 4,
    chartsCount: 2,
    roles: ['CEO', 'SALES_MANAGER', 'ADMIN'],
    status: 'Live Telemetry'
  },
  {
    id: 'DASH-03',
    slug: 'finance',
    title: 'Corporate Finance & P&L Analysis',
    description: 'Gross revenue, operating overheads, logistics cost spikes, EBITDA margins, and August 2026 variance diagnostics.',
    domain: 'Finance',
    icon: DollarSign,
    widgetsCount: 6,
    kpisCount: 4,
    chartsCount: 2,
    roles: ['CEO', 'FINANCE_MANAGER', 'ADMIN'],
    status: 'Live Telemetry'
  },
  {
    id: 'DASH-04',
    slug: 'hr',
    title: 'Workforce & Headcount Ledger',
    description: '10 departmental divisions, employee headcount allocations, average compensation bands, and monthly payroll.',
    domain: 'HRMS',
    icon: Users,
    widgetsCount: 5,
    kpisCount: 4,
    chartsCount: 2,
    roles: ['CEO', 'HR_MANAGER', 'ADMIN'],
    status: 'Live Telemetry'
  },
  {
    id: 'DASH-05',
    slug: 'inventory',
    title: 'Warehouse Stock & Buffer Deficit',
    description: 'Real-time stock on hand valuation, low-stock safety buffer warnings, category distributions, and supplier PO volume.',
    domain: 'Inventory',
    icon: Package,
    widgetsCount: 5,
    kpisCount: 4,
    chartsCount: 2,
    roles: ['CEO', 'INVENTORY_MANAGER', 'ADMIN'],
    status: 'Live Telemetry'
  },
  {
    id: 'DASH-06',
    slug: 'erp',
    title: 'ERP Procurement & Supply Chain',
    description: 'Enterprise procurement orders, active vendor relationships, purchase order fulfillment, and replenishment tracking.',
    domain: 'Operations',
    icon: Truck,
    widgetsCount: 5,
    kpisCount: 4,
    chartsCount: 2,
    roles: ['CEO', 'ERP_MANAGER', 'ADMIN'],
    status: 'Live Telemetry'
  },
];

export const Dashboards: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const userRole = user?.role || 'CEO';
  const [searchTerm, setSearchTerm] = useState('');
  const [infoMessage, setInfoMessage] = useState<string | null>(null);

  const filteredDashboards = REAL_SAVED_DASHBOARDS.filter((d) =>
    d.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    d.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
    d.domain.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/60 p-5 rounded-xl border border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
              <PanelsTopLeft className="w-4 h-4" />
            </div>
            <h1 className="text-xl font-bold text-white tracking-tight">Enterprise Analytics Dashboards</h1>
          </div>
          <p className="text-slate-400 text-sm mt-1">
            Real-time role-based operational dashboards powered by live MySQL and PostgreSQL telemetry.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {/* Search Bar */}
          <div className="relative w-48 sm:w-60">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search dashboards..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-slate-800/80 border border-slate-700/60 rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-emerald-500"
            />
          </div>

          <Button
            variant="primary"
            size="sm"
            onClick={() => {
              navigate('/analytics');
            }}
            className="flex items-center gap-1.5 shrink-0"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>AI Query Assistant</span>
          </Button>
        </div>
      </div>

      {infoMessage && (
        <div className="p-3 bg-blue-500/10 border border-blue-500/30 text-blue-300 text-xs rounded-lg animate-fade-in">
          {infoMessage}
        </div>
      )}

      {/* Grid of Dashboard Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredDashboards.map((dashboard) => {
          const IconComponent = dashboard.icon;
          const isAllowed = userRole === 'CEO' || userRole === 'ADMIN' || dashboard.roles.includes(userRole);

          return (
            <Card
              key={dashboard.id}
              className={`p-5 flex flex-col justify-between transition-all group ${
                isAllowed
                  ? 'hover:border-emerald-500/50 cursor-pointer hover:shadow-lg hover:shadow-emerald-950/20'
                  : 'opacity-75'
              }`}
              onClick={() => {
                if (isAllowed) {
                  navigate(`/dashboard/${dashboard.slug}`);
                } else {
                  setInfoMessage(`Access restricted: ${dashboard.title} requires ${dashboard.roles.join(' or ')} permission.`);
                  setTimeout(() => setInfoMessage(null), 3000);
                }
              }}
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2.5">
                    <div className="w-9 h-9 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 group-hover:scale-105 transition-transform">
                      <IconComponent className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="text-sm font-semibold text-white group-hover:text-emerald-400 transition-colors">
                        {dashboard.title}
                      </h3>
                      <p className="text-[11px] text-slate-400">{dashboard.domain}</p>
                    </div>
                  </div>

                  <Badge variant={isAllowed ? 'emerald' : 'secondary'}>
                    <span className={`w-1.5 h-1.5 rounded-full mr-1.5 ${isAllowed ? 'bg-emerald-400 animate-pulse' : 'bg-slate-500'}`} />
                    {isAllowed ? dashboard.status : 'Restricted'}
                  </Badge>
                </div>

                <p className="text-xs text-slate-300 mb-4 line-clamp-2 leading-relaxed">
                  {dashboard.description}
                </p>

                <div className="grid grid-cols-3 gap-2 text-center text-xs bg-slate-900/60 p-2.5 rounded-lg border border-slate-800/80 mb-4">
                  <div>
                    <span className="text-slate-500 text-[10px] block">Live Widgets</span>
                    <span className="text-slate-200 font-semibold">{dashboard.widgetsCount}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 text-[10px] block">KPI Cards</span>
                    <span className="text-slate-200 font-semibold">{dashboard.kpisCount}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 text-[10px] block">Telemetry Charts</span>
                    <span className="text-slate-200 font-semibold">{dashboard.chartsCount}</span>
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-between pt-3 border-t border-slate-800/80 text-[11px]">
                <div className="flex items-center gap-1.5 text-slate-400 font-mono text-[10px]">
                  <Clock className="w-3 h-3 text-slate-500" />
                  <span>Real-time • IST Synced</span>
                </div>

                <div className="flex items-center gap-1 text-emerald-400 font-medium group-hover:translate-x-0.5 transition-transform">
                  <span>{isAllowed ? 'Open Dashboard' : 'View Scope'}</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </div>
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
};
