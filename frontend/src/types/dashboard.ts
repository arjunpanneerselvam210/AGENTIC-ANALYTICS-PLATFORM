export type DateRangeOption = 'today' | '7d' | '30d' | '90d' | '12m' | 'custom';

export interface KPICardData {
  id?: string;
  title: string;
  value: string;
  change: string;
  isPositive: boolean;
  periodText: string;
}

export interface SalesTrendPoint {
  month: string;
  revenue: number;
  orders: number;
}

export interface CategoryPoint {
  name: string;
  value: number;
  color: string;
}

export interface TopProductItem {
  id: string;
  name: string;
  category: string;
  revenue: number;
  orders: number;
  growth: string;
  stock: number;
}

export interface KeyInsightItem {
  id: string;
  title: string;
  description: string;
  category: string;
  impact: string;
  date: string;
  source: string;
}

export interface ReportItem {
  id: string;
  title: string;
  name?: string;
  domain: string;
  date: string;
  status: string;
  fileSize?: string;
  format: string;
}

export interface DataSourceItem {
  id: string;
  name: string;
  type: string;
  status: string;
  tablesCount: number;
  lastSync: string;
  description: string;
}

export interface SavedDashboardItem {
  id: string;
  title: string;
  description: string;
  category?: string;
  widgetsCount?: number;
  kpisCount?: number;
  chartsCount?: number;
  updatedAt?: string;
  lastUpdated?: string;
}

export interface DashboardResponse {
  range: string;
  kpis: KPICardData[];
  sales_trend: SalesTrendPoint[];
  category_distribution: CategoryPoint[];
  top_products: TopProductItem[];
  insights: KeyInsightItem[];
}

export interface RoleDashboardData {
  role: string;
  role_title: string;
  scope_badge: string;
  range: string;
  kpis: KPICardData[];
  sales_trend?: SalesTrendPoint[];
  financial_trend?: Array<{
    fiscal_year: number;
    month_name: string;
    total_revenue: number;
    cogs: number;
    operating_expenses: number;
    net_profit: number;
    profit_margin_pct: number;
  }>;
  category_distribution?: CategoryPoint[];
  top_products?: TopProductItem[];
  top_customers?: Array<{
    company_name: string;
    orders: number;
    spend: number;
    city?: string;
    industry?: string;
  }>;
  crm_pipeline?: Array<{
    status: string;
    count: number;
  }>;
  department_summary?: Array<{
    department: string;
    headcount: number;
    avg_salary: number;
    total_payroll: number;
  }>;
  low_stock_items?: Array<{
    product_id: string;
    product_name: string;
    category: string;
    quantity_on_hand: number;
    reorder_level: number;
    deficit: number;
    unit_cost?: number;
  }>;
  top_suppliers?: Array<{
    supplier_name: string;
    po_count: number;
    total_spend: number;
    payment_terms?: string;
  }>;
  expense_breakdown?: Array<{
    category: string;
    total: number;
  }>;
  root_cause_highlight?: {
    period: string;
    july_profit: number;
    august_profit: number;
    change_pct: number;
    primary_driver: string;
    cogs_expansion: string;
    action_taken: string;
  };
  insights: KeyInsightItem[];
}

