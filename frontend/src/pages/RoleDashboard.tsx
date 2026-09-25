import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Calendar, RefreshCw, CheckCircle2, ShieldCheck, AlertCircle } from 'lucide-react';
import { useAuth, getRoleSlug } from '../context/AuthContext';
import { KPICard } from '../components/dashboard/KPICard';
import { SalesTrendChart } from '../components/dashboard/SalesTrendChart';
import { FinancialTrendChart } from '../components/dashboard/FinancialTrendChart';
import { CategoryChart } from '../components/dashboard/CategoryChart';
import { TopProductsTable } from '../components/dashboard/TopProductsTable';
import { TopCustomersTable } from '../components/dashboard/TopCustomersTable';
import { DepartmentSummaryTable } from '../components/dashboard/DepartmentSummaryTable';
import { LowStockTable } from '../components/dashboard/LowStockTable';
import { TopSuppliersTable } from '../components/dashboard/TopSuppliersTable';
import { ExpenseBreakdownChart } from '../components/dashboard/ExpenseBreakdownChart';
import { RootCauseHighlightCard } from '../components/dashboard/RootCauseHighlightCard';
import { InsightCard } from '../components/dashboard/InsightCard';
import { getRoleDashboard } from '../services/analyticsApi';
import type { DateRangeOption, RoleDashboardData } from '../types/dashboard';

const DATE_RANGES: { id: DateRangeOption; label: string }[] = [
  { id: 'today', label: 'Today' },
  { id: '7d', label: 'Last 7 Days' },
  { id: '30d', label: 'Last 30 Days' },
  { id: '90d', label: 'Last 90 Days' },
  { id: '12m', label: 'Last 12 Months' },
];

interface RoleDashboardProps {
  roleSlug?: string;
}

export const RoleDashboard: React.FC<RoleDashboardProps> = ({ roleSlug: propRoleSlug }) => {
  const { roleSlug: paramRoleSlug } = useParams<{ roleSlug: string }>();
  const { user } = useAuth();
  const navigate = useNavigate();

  const userDefaultSlug = getRoleSlug(user?.role);
  const activeSlug = propRoleSlug || paramRoleSlug || userDefaultSlug;

  const [selectedRange, setSelectedRange] = useState<DateRangeOption>('12m');
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [dashboardData, setDashboardData] = useState<RoleDashboardData | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const fetchRoleData = async (slug: string, range: DateRangeOption) => {
    setIsRefreshing(true);
    setErrorMsg(null);
    try {
      const data = await getRoleDashboard(slug, range);
      setDashboardData(data);
    } catch (err: any) {
      console.error('Role dashboard fetch failed:', err);
      if (err.response?.status === 403) {
        setErrorMsg(`Access Restricted: Your role (${user?.role}) does not have permission to view the ${slug.toUpperCase()} dashboard.`);
      } else {
        setErrorMsg('Unable to retrieve real-time dashboard telemetry. Please check database connection.');
      }
    } finally {
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchRoleData(activeSlug, selectedRange);
  }, [activeSlug, selectedRange]);

  const handleRefresh = () => {
    fetchRoleData(activeSlug, selectedRange);
  };

  if (errorMsg) {
    return (
      <div className="space-y-6">
        <div className="p-8 rounded-2xl bg-[#0F1626] border border-rose-500/30 text-center space-y-4">
          <div className="w-12 h-12 rounded-2xl bg-rose-500/10 border border-rose-500/30 flex items-center justify-center mx-auto text-rose-400">
            <AlertCircle className="w-6 h-6" />
          </div>
          <h2 className="text-xl font-bold text-white">RBAC Access Boundary Enforced</h2>
          <p className="text-sm text-rose-300 max-w-lg mx-auto">{errorMsg}</p>
          <div className="pt-2">
            <button
              onClick={() => navigate(`/dashboard/${userDefaultSlug}`)}
              className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold transition-colors"
            >
              Return to Your Authorized Dashboard ({user?.role})
            </button>
          </div>
        </div>
      </div>
    );
  }

  const kpis = dashboardData?.kpis || [];
  const insights = dashboardData?.insights || [];

  return (
    <div className="space-y-6">
      {/* Top Banner / Greeting with Role Context */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/60 p-5 rounded-2xl border border-slate-800 shadow-sm">
        <div>
          <div className="flex items-center gap-2.5 flex-wrap">
            <h1 className="text-2xl font-bold text-white tracking-tight">
              Good Morning, {user?.name?.split(' ')[0] || user?.full_name?.split(' ')[0] || 'Executive'}!
            </h1>
            <span className="inline-flex items-center gap-1 text-[11px] px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-medium">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Live MySQL Telemetry</span>
            </span>
            <span className="inline-flex items-center gap-1 text-[11px] px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700 font-mono">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              <span>{dashboardData?.scope_badge || `${user?.role} Scope`}</span>
            </span>
          </div>
          <p className="text-slate-400 text-xs sm:text-sm mt-1">
            {dashboardData?.role_title || 'Enterprise Analytics Dashboard'} — Real-time FreshMart operational data
          </p>
        </div>

        {/* Date Range Selector & Refresh */}
        <div className="flex items-center gap-2 self-start md:self-auto">
          <div className="flex items-center bg-[#080C14] border border-slate-800 rounded-xl p-1 text-xs">
            <Calendar className="w-3.5 h-3.5 text-slate-400 ml-2 mr-1" />
            <select
              value={selectedRange}
              onChange={(e) => setSelectedRange(e.target.value as DateRangeOption)}
              className="bg-transparent text-slate-200 focus:outline-none pr-3 py-1 cursor-pointer font-medium text-xs"
            >
              {DATE_RANGES.map((r) => (
                <option key={r.id} value={r.id} className="bg-[#0F1626] text-white">
                  {r.label}
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="p-2 bg-[#080C14] border border-slate-800 hover:border-slate-700 text-slate-300 rounded-xl transition-colors disabled:opacity-50"
            title="Refresh Live Data"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin text-emerald-400' : ''}`} />
          </button>
        </div>
      </div>

      {/* 4 Dedicated Top-Line KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {kpis.map((kpi, index) => (
          <KPICard
            key={kpi.title + index}
            title={kpi.title}
            value={kpi.value}
            change={kpi.change}
            isPositive={kpi.isPositive}
            periodText={kpi.periodText}
          />
        ))}
      </div>

      {/* Root-Cause Highlight (Displayed for CEO and Finance Manager) */}
      {dashboardData?.root_cause_highlight && (
        <RootCauseHighlightCard data={dashboardData.root_cause_highlight} />
      )}

      {/* Role-Specific Primary Chart Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column (2 spans): Primary Velocity Chart */}
        <div className="lg:col-span-2">
          {activeSlug === 'finance' && dashboardData?.financial_trend ? (
            <FinancialTrendChart data={dashboardData.financial_trend} />
          ) : activeSlug === 'hr' && dashboardData?.expense_breakdown ? (
            <ExpenseBreakdownChart data={dashboardData.expense_breakdown} />
          ) : (
            <SalesTrendChart data={dashboardData?.sales_trend || []} />
          )}
        </div>

        {/* Right Column (1 span): Breakdown Chart */}
        <div className="lg:col-span-1">
          {activeSlug === 'finance' && dashboardData?.expense_breakdown ? (
            <ExpenseBreakdownChart data={dashboardData.expense_breakdown} />
          ) : (
            <CategoryChart data={dashboardData?.category_distribution || []} />
          )}
        </div>
      </div>

      {/* Role-Specific Tables & Detail Blocks */}
      <div>
        {activeSlug === 'sales' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <TopCustomersTable customers={dashboardData?.top_customers} />
            <TopProductsTable products={dashboardData?.top_products || []} />
          </div>
        )}

        {activeSlug === 'hr' && (
          <DepartmentSummaryTable departments={dashboardData?.department_summary} />
        )}

        {activeSlug === 'inventory' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <LowStockTable items={dashboardData?.low_stock_items} />
            <TopSuppliersTable suppliers={dashboardData?.top_suppliers} />
          </div>
        )}

        {activeSlug === 'erp' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <TopSuppliersTable suppliers={dashboardData?.top_suppliers} />
            <LowStockTable items={dashboardData?.low_stock_items} />
          </div>
        )}

        {activeSlug === 'ceo' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <TopProductsTable products={dashboardData?.top_products || []} />
            {dashboardData?.financial_trend && (
              <FinancialTrendChart data={dashboardData.financial_trend} />
            )}
          </div>
        )}

        {activeSlug === 'finance' && dashboardData?.sales_trend && (
          <SalesTrendChart data={dashboardData.sales_trend} />
        )}
      </div>

      {/* Telemetry-Grounded Domain Insights Section */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-white">Grounded Operational Insights</h2>
            <p className="text-xs text-slate-400">Automated multi-domain observations derived directly from FreshMart telemetry</p>
          </div>
          <span className="text-[11px] font-mono text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-lg border border-emerald-500/20">
            {insights.length} Active Observations
          </span>
        </div>

        <InsightCard insights={insights} onViewAll={() => navigate('/insights')} />
      </div>
    </div>
  );
};
