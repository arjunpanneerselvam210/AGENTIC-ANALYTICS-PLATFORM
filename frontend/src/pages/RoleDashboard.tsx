import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Calendar,
  RefreshCw,
  CheckCircle2,
  ShieldCheck,
  AlertCircle,
  Users,
  ShoppingCart,
  DollarSign,
  Package,
  Truck,
  Building2,
} from 'lucide-react';
import { useAuth, getRoleSlug } from '../context/AuthContext';
import { KPICard } from '../components/dashboard/KPICard';
import { SalesTrendChart } from '../components/dashboard/SalesTrendChart';
import { FinancialTrendChart } from '../components/dashboard/FinancialTrendChart';
import { ProfitMarginTrendChart } from '../components/dashboard/ProfitMarginTrendChart';
import { CategoryChart } from '../components/dashboard/CategoryChart';
import { TopProductsTable } from '../components/dashboard/TopProductsTable';
import { TopCustomersTable } from '../components/dashboard/TopCustomersTable';
import { DepartmentSummaryTable } from '../components/dashboard/DepartmentSummaryTable';
import { DepartmentSalaryChart } from '../components/dashboard/DepartmentSalaryChart';
import { LowStockTable } from '../components/dashboard/LowStockTable';
import { TopSuppliersTable } from '../components/dashboard/TopSuppliersTable';
import { ExpenseBreakdownChart } from '../components/dashboard/ExpenseBreakdownChart';
import { RootCauseHighlightCard } from '../components/dashboard/RootCauseHighlightCard';
import { InsightCard } from '../components/dashboard/InsightCard';
import { DepartmentHeadcountChart } from '../components/dashboard/DepartmentHeadcountChart';
import { LowStockDeficitChart } from '../components/dashboard/LowStockDeficitChart';
import { StockByCategoryChart } from '../components/dashboard/StockByCategoryChart';
import { CRMPipelineChart } from '../components/dashboard/CRMPipelineChart';
import { SupplierSpendChart } from '../components/dashboard/SupplierSpendChart';
import { RoleAnalyticsAssistant } from '../components/dashboard/RoleAnalyticsAssistant';
import { UserManagement } from './UserManagement';
import { getRoleDashboard } from '../services/analyticsApi';
import type { DateRangeOption, RoleDashboardData } from '../types/dashboard';

const CEO_DOMAINS = [
  { slug: 'ceo', label: 'Executive Overview', icon: Building2 },
  { slug: 'sales', label: 'Sales Domain', icon: ShoppingCart },
  { slug: 'finance', label: 'Finance Domain', icon: DollarSign },
  { slug: 'hr', label: 'HR Workforce', icon: Users },
  { slug: 'inventory', label: 'Inventory & Stock', icon: Package },
  { slug: 'erp', label: 'ERP Operations', icon: Truck },
  { slug: 'admin', label: 'User & Role Admin', icon: ShieldCheck, badge: 'CEO' },
];

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

  const isCeo = user?.role === 'CEO' || user?.role === 'ADMIN';
  const [activeTab, setActiveTab] = useState<string>(activeSlug);

  useEffect(() => {
    setActiveTab(activeSlug);
  }, [activeSlug]);

  const handleTabChange = (slug: string) => {
    setActiveTab(slug);
    if (slug === 'admin') {
      navigate('/admin/users');
    } else {
      navigate(`/dashboard/${slug}`);
    }
  };

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
        setErrorMsg(
          `Access Restricted: Your role (${user?.role}) does not have permission to view the ${slug.toUpperCase()} dashboard.`
        );
      } else {
        setErrorMsg('Unable to retrieve real-time dashboard telemetry. Please check database connection.');
      }
    } finally {
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    if (activeTab !== 'admin') {
      fetchRoleData(activeTab, selectedRange);
    }
  }, [activeTab, selectedRange]);

  const handleRefresh = () => {
    if (activeTab !== 'admin') {
      fetchRoleData(activeTab, selectedRange);
    }
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
              className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold transition-colors cursor-pointer"
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
  const isLoadingInitial = dashboardData === null && isRefreshing;

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
              <span>
                {activeTab === 'admin'
                  ? 'CEO Administration'
                  : dashboardData?.scope_badge || `${user?.role} Scope`}
              </span>
            </span>
          </div>
          <p className="text-slate-400 text-xs sm:text-sm mt-1">
            {activeTab === 'admin'
              ? 'User & Role Management — Provision and administer application accounts for workforce employees'
              : (dashboardData?.role_title || 'Enterprise Analytics Dashboard') +
                ' — Real-time FreshMart operational data'}
          </p>
        </div>

        {/* Date Range Selector & Refresh */}
        {activeTab !== 'admin' && (
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
              className="p-2 bg-[#080C14] border border-slate-800 hover:border-slate-700 text-slate-300 rounded-xl transition-colors disabled:opacity-50 cursor-pointer"
              title="Refresh Live Data"
            >
              <RefreshCw
                className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin text-emerald-400' : ''}`}
              />
            </button>
          </div>
        )}
      </div>

      {/* CEO-Only Multi-Domain Switcher */}
      {isCeo && (
        <div className="flex items-center gap-1.5 p-1.5 bg-[#080C14] border border-slate-800 rounded-xl overflow-x-auto scrollbar-none shadow-sm">
          {CEO_DOMAINS.map((domain) => {
            const Icon = domain.icon;
            const isSelected = activeTab === domain.slug;

            return (
              <button
                key={domain.slug}
                onClick={() => handleTabChange(domain.slug)}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold whitespace-nowrap transition-all cursor-pointer ${
                  isSelected
                    ? 'bg-emerald-600/25 text-emerald-400 border border-emerald-500/40 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40 border border-transparent'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{domain.label}</span>
                {domain.badge && (
                  <span className="text-[9px] bg-emerald-500/20 text-emerald-300 font-mono px-1 py-0.5 rounded font-bold">
                    {domain.badge}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      )}

      {/* Main Body */}
      {activeTab === 'admin' ? (
        <UserManagement />
      ) : (
        <>
          {/* Embedded Role-Scoped AI Analytics Assistant (Persistent Session History & Charts) */}
          <RoleAnalyticsAssistant roleSlug={activeTab} />

          {/* CEO-Only Administration Quick Access Banner */}
          {activeTab === 'ceo' && isCeo && (
            <div className="bg-gradient-to-r from-emerald-950/40 via-slate-900 to-slate-900 border border-emerald-500/30 rounded-2xl p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-sm">
              <div className="flex items-start sm:items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 shrink-0">
                  <ShieldCheck className="w-5 h-5" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-white font-bold text-sm">
                      Administration: User & Role Management
                    </span>
                    <span className="text-[10px] bg-emerald-500/20 text-emerald-300 font-mono px-1.5 py-0.5 rounded border border-emerald-500/30 font-semibold">
                      CEO ONLY
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Provision application logins for employees, reassign roles, and enforce RBAC policies.
                  </p>
                </div>
              </div>
              <button
                onClick={() => handleTabChange('admin')}
                className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold flex items-center justify-center gap-2 transition-colors shrink-0 shadow-md shadow-emerald-950/30 cursor-pointer"
              >
                <Users className="w-3.5 h-3.5" />
                <span>Open User & Role Management</span>
              </button>
            </div>
          )}

          {/* Data Refreshing Shimmer Bar */}
          {isRefreshing && (
            <div className="w-full bg-slate-800/60 rounded-full h-1 overflow-hidden">
              <div className="bg-gradient-to-r from-emerald-500 via-teal-400 to-emerald-500 h-full w-full animate-pulse" />
            </div>
          )}

          {/* Initial Domain Loading Skeleton State (Eliminates Dark Screen) */}
          {isLoadingInitial ? (
            <div className="space-y-6 animate-pulse">
              {/* 4 Skeleton KPI Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {[1, 2, 3, 4].map((i) => (
                  <div
                    key={i}
                    className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-3"
                  >
                    <div className="flex items-center justify-between">
                      <div className="h-3.5 w-24 bg-slate-800 rounded-md" />
                      <div className="h-6 w-14 bg-slate-800/80 rounded-full" />
                    </div>
                    <div className="h-7 w-32 bg-slate-800 rounded-md" />
                    <div className="h-3 w-20 bg-slate-800/60 rounded-md" />
                  </div>
                ))}
              </div>

              {/* Skeleton Primary Charts */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 p-5 rounded-2xl bg-slate-900/70 border border-slate-800 h-80 flex flex-col justify-between">
                  <div className="flex items-center justify-between">
                    <div className="space-y-1.5">
                      <div className="h-4 w-36 bg-slate-800 rounded-md" />
                      <div className="h-3 w-48 bg-slate-800/60 rounded-md" />
                    </div>
                    <div className="h-4 w-16 bg-slate-800 rounded-md" />
                  </div>
                  <div className="h-48 w-full bg-slate-800/30 rounded-xl flex items-center justify-center">
                    <RefreshCw className="w-6 h-6 animate-spin text-emerald-500/40" />
                  </div>
                </div>

                <div className="lg:col-span-1 p-5 rounded-2xl bg-slate-900/70 border border-slate-800 h-80 flex flex-col justify-between">
                  <div className="space-y-1.5">
                    <div className="h-4 w-28 bg-slate-800 rounded-md" />
                    <div className="h-3 w-36 bg-slate-800/60 rounded-md" />
                  </div>
                  <div className="h-48 w-full bg-slate-800/30 rounded-full flex items-center justify-center">
                    <div className="w-32 h-32 rounded-full border-4 border-slate-800 border-t-emerald-500/40 animate-spin" />
                  </div>
                </div>
              </div>

              {/* Skeleton Secondary Section */}
              <div className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800 h-64 flex flex-col justify-between">
                <div className="h-4 w-40 bg-slate-800 rounded-md" />
                <div className="space-y-2">
                  {[1, 2, 3].map((r) => (
                    <div key={r} className="h-8 bg-slate-800/40 rounded-lg w-full" />
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <>
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

          {/* Primary Chart Section */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left Column (2 spans): Primary Domain Velocity Chart */}
            <div className="lg:col-span-2">
              {activeTab === 'hr' ? (
                <DepartmentHeadcountChart departments={dashboardData?.department_summary || []} />
              ) : activeTab === 'inventory' ? (
                <LowStockDeficitChart items={dashboardData?.low_stock_items || []} />
              ) : activeTab === 'erp' ? (
                <SupplierSpendChart suppliers={dashboardData?.top_suppliers || []} />
              ) : activeTab === 'finance' && dashboardData?.financial_trend ? (
                <FinancialTrendChart data={dashboardData.financial_trend} />
              ) : activeTab === 'ceo' && dashboardData?.financial_trend ? (
                <FinancialTrendChart data={dashboardData.financial_trend} />
              ) : (
                <SalesTrendChart data={dashboardData?.sales_trend || []} />
              )}
            </div>

            {/* Right Column (1 span): Domain Breakdown / Distribution Chart */}
            <div className="lg:col-span-1">
              {activeTab === 'hr' ? (
                <ExpenseBreakdownChart data={dashboardData?.expense_breakdown || []} />
              ) : activeTab === 'inventory' ? (
                <StockByCategoryChart data={dashboardData?.category_distribution || []} />
              ) : activeTab === 'erp' ? (
                <ExpenseBreakdownChart data={dashboardData?.expense_breakdown || []} />
              ) : activeTab === 'finance' && dashboardData?.expense_breakdown ? (
                <ExpenseBreakdownChart data={dashboardData.expense_breakdown} />
              ) : (
                <CategoryChart data={dashboardData?.category_distribution || []} />
              )}
            </div>
          </div>

          {/* Secondary Visualizations & Tables Tailored per Role */}
          <div>
            {/* 1. SALES DOMAIN */}
            {activeTab === 'sales' && (
              <div className="space-y-6">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <CRMPipelineChart pipeline={dashboardData?.crm_pipeline || []} />
                  <TopCustomersTable customers={dashboardData?.top_customers} />
                </div>
                <TopProductsTable products={dashboardData?.top_products || []} />
              </div>
            )}

            {/* 2. HR WORKFORCE DOMAIN */}
            {activeTab === 'hr' && (
              <div className="space-y-6">
                <DepartmentSalaryChart departments={dashboardData?.department_summary} />
                <DepartmentSummaryTable departments={dashboardData?.department_summary} />
              </div>
            )}

            {/* 3. INVENTORY & STOCK DOMAIN */}
            {activeTab === 'inventory' && (
              <div className="space-y-6">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <LowStockTable items={dashboardData?.low_stock_items} />
                  <TopSuppliersTable suppliers={dashboardData?.top_suppliers} />
                </div>
              </div>
            )}

            {/* 4. ERP OPERATIONS DOMAIN */}
            {activeTab === 'erp' && (
              <div className="space-y-6">
                {dashboardData?.sales_trend && (
                  <SalesTrendChart data={dashboardData.sales_trend} />
                )}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <TopSuppliersTable suppliers={dashboardData?.top_suppliers} />
                  <LowStockTable items={dashboardData?.low_stock_items} />
                </div>
              </div>
            )}

            {/* 5. FINANCE DOMAIN */}
            {activeTab === 'finance' && (
              <div className="space-y-6">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {dashboardData?.financial_trend && (
                    <ProfitMarginTrendChart data={dashboardData.financial_trend} />
                  )}
                  {dashboardData?.sales_trend && (
                    <SalesTrendChart data={dashboardData.sales_trend} />
                  )}
                </div>
              </div>
            )}

            {/* 6. CEO EXECUTIVE OVERVIEW */}
            {activeTab === 'ceo' && (
              <div className="space-y-6">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <SalesTrendChart data={dashboardData?.sales_trend || []} />
                  {dashboardData?.financial_trend && (
                    <ProfitMarginTrendChart data={dashboardData.financial_trend} />
                  )}
                </div>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <TopProductsTable products={dashboardData?.top_products || []} />
                  <DepartmentSalaryChart departments={dashboardData?.department_summary || []} />
                </div>
              </div>
            )}
          </div>

          {/* Telemetry-Grounded Domain Insights Section */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-base font-bold text-white">Grounded Operational Insights</h2>
                <p className="text-xs text-slate-400">
                  Automated multi-domain observations derived directly from FreshMart telemetry
                </p>
              </div>
              <span className="text-[11px] font-mono text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-lg border border-emerald-500/20">
                {insights.length} Active Observations
              </span>
            </div>

            <InsightCard insights={insights} onViewAll={() => navigate('/insights')} />
          </div>
            </>
          )}
        </>
      )}
    </div>
  );
};
