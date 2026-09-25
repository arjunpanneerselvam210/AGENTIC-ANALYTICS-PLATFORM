import type {
  KPICardData,
  SalesTrendPoint,
  CategoryPoint,
  TopProductItem,
  KeyInsightItem,
  ReportItem,
  DataSourceItem,
  SavedDashboardItem
} from '../types/dashboard';
import type { AnalyticsResponse } from '../types/analytics';

export const mockKPIData: Record<string, KPICardData[]> = {
  'Last 30 Days': [
    { title: 'Total Revenue', value: '₹12.8M', change: '+12.4%', isPositive: true, periodText: 'vs previous 30 days' },
    { title: 'Total Customers', value: '24,680', change: '+8.2%', isPositive: true, periodText: 'vs previous 30 days' },
    { title: 'Total Orders', value: '8,492', change: '+15.7%', isPositive: true, periodText: 'vs previous 30 days' },
    { title: 'Active Employees', value: '486', change: '+2.1%', isPositive: true, periodText: 'vs previous 30 days' },
  ],
  'Last 12 Months': [
    { title: 'Total Revenue', value: '₹142.5M', change: '+18.6%', isPositive: true, periodText: 'vs previous fiscal year' },
    { title: 'Total Customers', value: '28,450', change: '+14.1%', isPositive: true, periodText: 'vs previous fiscal year' },
    { title: 'Total Orders', value: '98,240', change: '+22.3%', isPositive: true, periodText: 'vs previous fiscal year' },
    { title: 'Active Employees', value: '500', change: '+5.4%', isPositive: true, periodText: 'vs previous fiscal year' },
  ],
  'Today': [
    { title: 'Total Revenue', value: '₹420.5K', change: '+6.1%', isPositive: true, periodText: 'vs yesterday' },
    { title: 'Total Customers', value: '840', change: '+3.4%', isPositive: true, periodText: 'vs yesterday' },
    { title: 'Total Orders', value: '294', change: '+8.9%', isPositive: true, periodText: 'vs yesterday' },
    { title: 'Active Employees', value: '486', change: '0.0%', isPositive: true, periodText: 'vs yesterday' },
  ],
  'Last 7 Days': [
    { title: 'Total Revenue', value: '₹2.95M', change: '+9.3%', isPositive: true, periodText: 'vs previous 7 days' },
    { title: 'Total Customers', value: '5,820', change: '+7.1%', isPositive: true, periodText: 'vs previous 7 days' },
    { title: 'Total Orders', value: '1,980', change: '+11.2%', isPositive: true, periodText: 'vs previous 7 days' },
    { title: 'Active Employees', value: '486', change: '+0.5%', isPositive: true, periodText: 'vs previous 7 days' },
  ]
};

export const MOCK_KPIS = mockKPIData['Last 30 Days'];

export const mockSalesTrendData: SalesTrendPoint[] = [
  { month: 'Oct 25', revenue: 9800000, orders: 6200 },
  { month: 'Nov 25', revenue: 10400000, orders: 6600 },
  { month: 'Dec 25', revenue: 12100000, orders: 7800 },
  { month: 'Jan 26', revenue: 10900000, orders: 6900 },
  { month: 'Feb 26', revenue: 11200000, orders: 7100 },
  { month: 'Mar 26', revenue: 12400000, orders: 8100 },
  { month: 'Apr 26', revenue: 13100000, orders: 8500 },
  { month: 'May 26', revenue: 12800000, orders: 8300 },
  { month: 'Jun 26', revenue: 13600000, orders: 8900 },
  { month: 'Jul 26', revenue: 14200000, orders: 9400 },
  { month: 'Aug 26', revenue: 13900000, orders: 9100 },
  { month: 'Sep 26', revenue: 14800000, orders: 9700 },
];

export const MOCK_SALES_TREND = mockSalesTrendData;

export const mockCategoryData: CategoryPoint[] = [
  { name: 'Fresh Groceries', value: 38, color: '#10B981' }, // emerald
  { name: 'Beverages', value: 22, color: '#06B6D4' },        // cyan
  { name: 'Household & Cleaning', value: 16, color: '#6366F1' }, // indigo
  { name: 'Personal Care', value: 12, color: '#F59E0B' },     // amber
  { name: 'Electronics & Accessories', value: 8, color: '#EC4899' }, // pink
  { name: 'Packaged Foods', value: 4, color: '#8B5CF6' },    // purple
];

export const MOCK_CATEGORY_DATA = mockCategoryData;

export const mockTopProducts: TopProductItem[] = [
  { id: 'P012', name: 'Premium Arabica Coffee Beans 1kg', category: 'Beverages', revenue: 842000, orders: 1240, growth: '+24.5%', stock: 42 },
  { id: 'P004', name: 'Organic Royal Basmati Rice 5kg', category: 'Groceries', revenue: 765000, orders: 980, growth: '+18.2%', stock: 15 },
  { id: 'P029', name: 'Fresh Cow Milk 1L (Case of 12)', category: 'Dairy', revenue: 689000, orders: 1650, growth: '+12.8%', stock: 85 },
  { id: 'P054', name: 'Cold Pressed Extra Virgin Olive Oil 1L', category: 'Groceries', revenue: 594000, orders: 740, growth: '+15.4%', stock: 28 },
  { id: 'P088', name: 'Eco-Clean Concentrated Detergent 4L', category: 'Household', revenue: 512000, orders: 890, growth: '+9.7%', stock: 110 },
  { id: 'P112', name: 'Pro-Audio Wireless Bluetooth Earbuds', category: 'Electronics', revenue: 489000, orders: 320, growth: '+31.4%', stock: 18 },
];

export const MOCK_TOP_PRODUCTS = mockTopProducts;

export const mockKeyInsights: KeyInsightItem[] = [
  {
    id: 'INS-01',
    title: 'Strong Multi-Category Revenue Expansion',
    description: 'Quarterly revenue increased 12.4% with Beverages and Electronics experiencing the highest month-over-month sales acceleration.',
    category: 'Sales',
    impact: 'high',
    date: 'Today, 09:30 AM',
    source: 'sales_orders, sales_order_items'
  },
  {
    id: 'INS-02',
    title: 'August 2026 Operating Cost Surge Identified',
    description: 'Root-cause diagnostic confirmed August net profit dropped 50% from ₹1.20M to ₹600K due to emergency logistics and re-routed cold transit shipping expenses.',
    category: 'Finance',
    impact: 'high',
    date: 'Yesterday, 04:15 PM',
    source: 'company_financials, expenses'
  },
  {
    id: 'INS-03',
    title: 'Inventory Reorder Alert: High Sales, Low Stock',
    description: '17 top-selling SKUs including Royal Basmati Rice and Arabica Coffee are operating below safety stock reorder thresholds.',
    category: 'Inventory',
    impact: 'medium',
    date: 'Sep 24, 2026',
    source: 'inventory, products, sales_order_items'
  },
  {
    id: 'INS-04',
    title: 'Workforce Allocation Across 10 Operating Units',
    description: 'FreshMart employs 500 personnel across 10 departments, with Retail Operations (96) and Sales & Marketing (86) constituting 36% of the workforce.',
    category: 'HR',
    impact: 'low',
    date: 'Sep 23, 2026',
    source: 'departments, employees'
  },
];

export const MOCK_INSIGHTS = mockKeyInsights;

export const mockReports: ReportItem[] = [
  { id: 'REP-001', title: 'Monthly Executive Sales Performance', name: 'Monthly Executive Sales Performance', domain: 'Sales', date: '2026-09-01', status: 'Ready', fileSize: '2.4 MB', format: 'PDF' },
  { id: 'REP-002', title: 'Warehouse Inventory Health & Reorder Audit', name: 'Warehouse Inventory Health & Reorder Audit', domain: 'Inventory', date: '2026-09-15', status: 'Ready', fileSize: '1.8 MB', format: 'XLSX' },
  { id: 'REP-003', title: 'Workforce Headcount & Payroll Allocation', name: 'Workforce Headcount & Payroll Allocation', domain: 'HRMS', date: '2026-09-01', status: 'Ready', fileSize: '3.1 MB', format: 'PDF' },
  { id: 'REP-004', title: 'August 2026 Net Profit Diagnostic Analysis', name: 'August 2026 Net Profit Diagnostic Analysis', domain: 'Finance', date: '2026-08-31', status: 'Ready', fileSize: '4.2 MB', format: 'PDF' },
  { id: 'REP-005', title: 'CRM B2B Customer Pipeline & Lead Conversions', name: 'CRM B2B Customer Pipeline & Lead Conversions', domain: 'CRM', date: '2026-09-20', status: 'Ready', fileSize: '1.2 MB', format: 'CSV' },
  { id: 'REP-006', title: 'Procurement Supplier Performance & PO Volume', name: 'Procurement Supplier Performance & PO Volume', domain: 'Purchasing', date: '2026-09-10', status: 'Ready', fileSize: '2.9 MB', format: 'XLSX' },
];

export const MOCK_REPORTS = mockReports;

export const mockDataSources: DataSourceItem[] = [
  {
    id: 'DS-01',
    name: 'FreshMart ERP & Operations',
    type: 'Unified Business Domain',
    status: 'connected',
    tablesCount: 5,
    lastSync: 'Real-time (MCP)',
    description: 'Suppliers, purchase orders, purchase items, catalog products, and warehouse inventories.'
  },
  {
    id: 'DS-02',
    name: 'FreshMart CRM & Customer Experience',
    type: 'Unified Business Domain',
    status: 'connected',
    tablesCount: 4,
    lastSync: 'Real-time (MCP)',
    description: 'B2B enterprise customers, inbound sales leads, communications, and customer interactions.'
  },
  {
    id: 'DS-03',
    name: 'FreshMart HRMS Workforce',
    type: 'Unified Business Domain',
    status: 'connected',
    tablesCount: 3,
    lastSync: 'Real-time (MCP)',
    description: 'Workforce directory, departmental operating budgets, hierarchical managers, and employee compensation.'
  },
  {
    id: 'DS-04',
    name: 'FreshMart Sales & Point of Sale',
    type: 'Unified Business Domain',
    status: 'connected',
    tablesCount: 2,
    lastSync: 'Real-time (MCP)',
    description: 'Online e-commerce orders, retail store transactions, line items, and promotional pricing.'
  },
  {
    id: 'DS-05',
    name: 'MySQL 8.0 Business Database',
    type: 'mysql',
    status: 'connected',
    tablesCount: 16,
    lastSync: 'Localhost:3306 (company_analytics)',
    description: 'Central transactional MySQL server queried securely via Model Context Protocol (MCP) read-only reader.'
  },
  {
    id: 'DS-06',
    name: 'PostgreSQL 18 Auth & RBAC Server',
    type: 'postgresql',
    status: 'connected',
    tablesCount: 4,
    lastSync: 'Localhost:5432 (company_auth)',
    description: 'Dedicated relational security database enforcing role hierarchies and granular permissions.'
  },
];

export const MOCK_DATA_SOURCES = mockDataSources;

export const mockSavedDashboards: SavedDashboardItem[] = [
  { id: 'DASH-01', title: 'Executive Overview', description: 'Cross-domain summary of revenues, margins, headcounts, and supply health.', category: 'Executive', widgetsCount: 6, kpisCount: 6, chartsCount: 4, updatedAt: '1 hour ago', lastUpdated: '1 hour ago' },
  { id: 'DASH-02', title: 'Sales Performance & Regional Trends', description: 'Monthly revenue velocity, top sales reps, and customer order volumes.', category: 'Sales', widgetsCount: 4, kpisCount: 4, chartsCount: 3, updatedAt: '3 hours ago', lastUpdated: '3 hours ago' },
  { id: 'DASH-03', title: 'Inventory Health & Deficit Tracker', description: 'Warehouse stock balances, low-stock alerts, and pending PO replenishments.', category: 'Inventory', widgetsCount: 4, kpisCount: 4, chartsCount: 2, updatedAt: 'Yesterday', lastUpdated: 'Yesterday' },
  { id: 'DASH-04', title: 'Financial P&L & Expense Breakdown', description: 'Gross profit, operating overheads, logistics costs, and EBITDA margins.', category: 'Finance', widgetsCount: 5, kpisCount: 5, chartsCount: 4, updatedAt: '2 days ago', lastUpdated: '2 days ago' },
  { id: 'DASH-05', title: 'CRM B2B Conversion Funnel', description: 'Lead statuses, pipeline valuations, conversion timelines, and rep workloads.', category: 'CRM', widgetsCount: 3, kpisCount: 3, chartsCount: 2, updatedAt: '3 days ago', lastUpdated: '3 days ago' },
  { id: 'DASH-06', title: 'Workforce & Departmental Metrics', description: 'Personnel distributions, experience bands, and compensation allocations.', category: 'HR', widgetsCount: 4, kpisCount: 4, chartsCount: 2, updatedAt: 'Sep 20, 2026', lastUpdated: 'Sep 20, 2026' },
];

export const MOCK_SAVED_DASHBOARDS = mockSavedDashboards;

export const SUGGESTED_QUESTIONS = [
  'Why did profit decrease in August?',
  'Show monthly sales for the last 12 months.',
  'Which products are low in stock?',
  'Show leads by status.',
  'Which products generated the highest revenue and are currently low in stock?',
  'Show employee salaries.', // Demonstrates RBAC 403 Forbidden for Sales Manager
];

export const MOCK_ANALYTICS_RESPONSES: Record<string, AnalyticsResponse> = {
  'Why did profit decrease in August?': {
    success: true,
    question: 'Why did profit decrease in August?',
    answer: 'In August 2026, FreshMart experienced an acute profit contraction of 50.0% (net profit fell from ₹1,200,000 to ₹600,000). While monthly revenue remained stable at ₹13.9M, operating expenses increased sharply due to emergency temperature-controlled supply route detours (+₹340,000) and promotional discount campaigns (+₹260,000).',
    intent: {
      domain: 'Finance',
      operation: 'profit_diagnostic',
      metric: 'net_profit',
      time_range: '2026-08',
    },
    sources: ['company_financials', 'expenses', 'departments'],
    columns_used: ['month_year', 'revenue', 'expenses', 'net_profit'],
    visualization_hint: 'bar_chart',
    data: {
      columns: ['month', 'revenue', 'expenses', 'net_profit'],
      rows: [
        { month: 'Jun 26', revenue: 13600000, expenses: 12300000, net_profit: 1300000 },
        { month: 'Jul 26', revenue: 14200000, expenses: 13000000, net_profit: 1200000 },
        { month: 'Aug 26', revenue: 13900000, expenses: 13300000, net_profit: 600000 },
        { month: 'Sep 26', revenue: 14800000, expenses: 13400000, net_profit: 1400000 },
      ],
      row_count: 4,
      truncated: false,
    },
    user_role: 'CEO',
    user_name: 'Vikram Malhotra',
    timestamp: new Date().toISOString(),
  },
  'Which products are low in stock?': {
    success: true,
    question: 'Which products are low in stock?',
    answer: 'There are currently 6 core SKUs operating below their defined safety reorder thresholds in the FreshMart Central Distribution Center. Most notably, Organic Royal Basmati Rice (15 units remaining, reorder threshold: 50) and Premium Arabica Coffee (42 units, threshold: 100) require urgent purchase orders.',
    intent: {
      domain: 'Inventory',
      operation: 'low_stock_audit',
      metric: 'quantity_on_hand',
    },
    sources: ['inventory', 'products', 'suppliers'],
    columns_used: ['product_name', 'sku', 'stock_quantity', 'reorder_level'],
    visualization_hint: 'bar_chart',
    data: {
      columns: ['product_name', 'stock_quantity', 'reorder_level'],
      rows: [
        { product_name: 'Organic Royal Basmati Rice 5kg', stock_quantity: 15, reorder_level: 50 },
        { product_name: 'Pro-Audio Wireless Earbuds', stock_quantity: 18, reorder_level: 40 },
        { product_name: 'Cold Pressed Olive Oil 1L', stock_quantity: 28, reorder_level: 60 },
        { product_name: 'Premium Arabica Coffee 1kg', stock_quantity: 42, reorder_level: 100 },
        { product_name: 'Fresh Cow Milk (Case of 12)', stock_quantity: 85, reorder_level: 120 },
      ],
      row_count: 5,
      truncated: false,
    },
    user_role: 'CEO',
    user_name: 'Vikram Malhotra',
    timestamp: new Date().toISOString(),
  },
  'Show leads by status.': {
    success: true,
    question: 'Show leads by status.',
    answer: 'FreshMart CRM currently tracks 185 commercial B2B sales leads across 5 lifecycle stages. 42 leads are qualified, 38 are actively in negotiation, and 56 new inbound leads have arrived this month.',
    intent: {
      domain: 'CRM',
      operation: 'lead_distribution',
      metric: 'count',
    },
    sources: ['crm_leads', 'customers'],
    columns_used: ['lead_status', 'count'],
    visualization_hint: 'pie_chart',
    data: {
      columns: ['status', 'count'],
      rows: [
        { status: 'New', count: 56 },
        { status: 'Contacted', count: 34 },
        { status: 'Qualified', count: 42 },
        { status: 'Proposal / Negotiation', count: 38 },
        { status: 'Closed Won', count: 15 },
      ],
      row_count: 5,
      truncated: false,
    },
    user_role: 'CEO',
    user_name: 'Vikram Malhotra',
    timestamp: new Date().toISOString(),
  },
};

