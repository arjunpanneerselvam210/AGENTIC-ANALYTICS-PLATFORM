import React, { useState, useEffect } from 'react';
import { Calendar, RefreshCw, CheckCircle2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { KPICard } from '../components/dashboard/KPICard';
import { SalesTrendChart } from '../components/dashboard/SalesTrendChart';
import { CategoryChart } from '../components/dashboard/CategoryChart';
import { TopProductsTable } from '../components/dashboard/TopProductsTable';
import { InsightCard } from '../components/dashboard/InsightCard';
import { getDashboardMetrics } from '../services/analyticsApi';
import {
  MOCK_KPIS,
  MOCK_SALES_TREND,
  MOCK_CATEGORY_DATA,
  MOCK_TOP_PRODUCTS,
  MOCK_INSIGHTS
} from '../data/mockData';
import type {
  DateRangeOption,
  DashboardResponse,
  KPICardData,
  SalesTrendPoint,
  CategoryPoint,
  TopProductItem,
  KeyInsightItem
} from '../types/dashboard';

const DATE_RANGES: { id: DateRangeOption; label: string }[] = [
  { id: 'today', label: 'Today' },
  { id: '7d', label: 'Last 7 Days' },
  { id: '30d', label: 'Last 30 Days' },
  { id: '90d', label: 'Last 90 Days' },
  { id: '12m', label: 'Last 12 Months' },
  { id: 'custom', label: 'Custom Range' },
];

export const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [selectedRange, setSelectedRange] = useState<DateRangeOption>('12m');
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isLive, setIsLive] = useState(false);

  const [kpis, setKpis] = useState<KPICardData[]>(MOCK_KPIS);
  const [salesTrend, setSalesTrend] = useState<SalesTrendPoint[]>(MOCK_SALES_TREND);
  const [categoryData, setCategoryData] = useState<CategoryPoint[]>(MOCK_CATEGORY_DATA);
  const [topProducts, setTopProducts] = useState<TopProductItem[]>(MOCK_TOP_PRODUCTS);
  const [insights, setInsights] = useState<KeyInsightItem[]>(MOCK_INSIGHTS);

  const fetchDashboardData = async (range: DateRangeOption) => {
    setIsRefreshing(true);
    try {
      const data: DashboardResponse = await getDashboardMetrics(range);
      if (data && data.kpis && data.kpis.length > 0) {
        setKpis(data.kpis);
        if (data.sales_trend && data.sales_trend.length > 0) {
          setSalesTrend(data.sales_trend);
        }
        if (data.category_distribution && data.category_distribution.length > 0) {
          setCategoryData(data.category_distribution);
        }
        if (data.top_products && data.top_products.length > 0) {
          setTopProducts(data.top_products);
        }
        if (data.insights && data.insights.length > 0) {
          setInsights(data.insights);
        }
        setIsLive(true);
      }
    } catch (err) {
      console.warn('Live dashboard fetch failed, keeping local fallback:', err);
      setIsLive(false);
    } finally {
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchDashboardData(selectedRange);
  }, [selectedRange]);

  const handleRefresh = () => {
    fetchDashboardData(selectedRange);
  };

  return (
    <div className="space-y-6">
      {/* Top Banner / Greeting */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-slate-900/60 p-5 rounded-xl border border-slate-800 shadow-sm">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-white tracking-tight">
              Good Morning, {user?.name?.split(' ')[0] || user?.full_name?.split(' ')[0] || 'Executive'}!
            </h1>
            {isLive && (
              <span className="inline-flex items-center gap-1 text-[11px] px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                <CheckCircle2 className="w-3 h-3" />
                <span>Live MySQL Telemetry</span>
              </span>
            )}
          </div>
          <p className="text-slate-400 text-sm mt-1">
            Real-time business performance across FreshMart's unified ERP, CRM, HRMS, and Sales domains.
          </p>
        </div>

        {/* Date Filter & Refresh */}
        <div className="flex flex-wrap items-center gap-2">
          <div className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-800/80 border border-slate-700/60 rounded-lg text-xs text-slate-300">
            <Calendar className="w-3.5 h-3.5 text-emerald-400" />
            <select
              value={selectedRange}
              onChange={(e) => setSelectedRange(e.target.value as DateRangeOption)}
              className="bg-transparent border-none text-slate-200 focus:outline-none cursor-pointer"
            >
              {DATE_RANGES.map((r) => (
                <option key={r.id} value={r.id} className="bg-slate-900 text-slate-200">
                  {r.label}
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={handleRefresh}
            className={`p-2 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700/60 text-slate-300 transition-colors ${
              isRefreshing ? 'animate-spin' : ''
            }`}
            title="Refresh Dashboard"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {kpis.map((kpi, idx) => (
          <KPICard key={kpi.id || idx} kpi={kpi} />
        ))}
      </div>

      {/* Main Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <SalesTrendChart data={salesTrend} />
        </div>
        <div>
          <CategoryChart data={categoryData} />
        </div>
      </div>

      {/* Bottom Row: Top Products & Key Insights */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <TopProductsTable products={topProducts} />
        </div>
        <div>
          <InsightCard insights={insights} />
        </div>
      </div>
    </div>
  );
};
