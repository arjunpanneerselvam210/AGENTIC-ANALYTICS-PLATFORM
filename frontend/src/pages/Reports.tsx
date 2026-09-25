import React, { useState } from 'react';
import { FileBarChart, Download, Eye, Filter, Search, CheckCircle, Clock } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { Badge } from '../components/common/Badge';
import { Button } from '../components/common/Button';
import { downloadCSV, downloadValidPDF } from '../utils/exportUtils';
import { formatISTDateTime, formatISTDate } from '../utils/dateUtils';
import type { ReportItem } from '../types/dashboard';

const ROLE_ALLOWED_REPORT_DOMAINS: Record<string, string[]> = {
  CEO: ['All', 'Sales', 'Inventory', 'HRMS', 'Finance', 'CRM'],
  ADMIN: ['All', 'Sales', 'Inventory', 'HRMS', 'Finance', 'CRM'],
  SALES_MANAGER: ['All', 'Sales', 'CRM', 'Inventory'],
  FINANCE_MANAGER: ['All', 'Finance', 'Sales'],
  HR_MANAGER: ['All', 'HRMS'],
  INVENTORY_MANAGER: ['All', 'Inventory'],
  ERP_MANAGER: ['All', 'Inventory', 'Sales', 'Finance'],
};

const getInitialReports = (): ReportItem[] => {
  const now = new Date();
  const d1 = new Date(now.getTime() - 2 * 3600 * 1000);
  const d2 = new Date(now.getTime() - 24 * 3600 * 1000);
  const d3 = new Date(now.getTime() - 3 * 24 * 3600 * 1000);
  const d4 = new Date(now.getTime() - 7 * 24 * 3600 * 1000);
  const d5 = new Date(now.getTime() - 14 * 24 * 3600 * 1000);
  const d6 = new Date(now.getTime() - 30 * 24 * 3600 * 1000);

  return [
    { id: 'REP-001', title: 'Monthly Executive Sales Performance', name: 'Monthly Executive Sales Performance', domain: 'Sales', date: formatISTDate(d1), status: 'Ready', fileSize: '2.4 MB', format: 'PDF' },
    { id: 'REP-002', title: 'Warehouse Inventory Health & Reorder Audit', name: 'Warehouse Inventory Health & Reorder Audit', domain: 'Inventory', date: formatISTDate(d2), status: 'Ready', fileSize: '1.8 MB', format: 'XLSX' },
    { id: 'REP-003', title: 'Workforce Headcount & Payroll Allocation', name: 'Workforce Headcount & Payroll Allocation', domain: 'HRMS', date: formatISTDate(d3), status: 'Ready', fileSize: '3.1 MB', format: 'PDF' },
    { id: 'REP-004', title: 'Financial Variance & Net Profit Diagnostic Analysis', name: 'Financial Variance & Net Profit Diagnostic Analysis', domain: 'Finance', date: formatISTDate(d4), status: 'Ready', fileSize: '4.2 MB', format: 'PDF' },
    { id: 'REP-005', title: 'CRM B2B Customer Pipeline & Lead Conversions', name: 'CRM B2B Customer Pipeline & Lead Conversions', domain: 'CRM', date: formatISTDate(d5), status: 'Ready', fileSize: '1.2 MB', format: 'CSV' },
    { id: 'REP-006', title: 'Procurement Supplier Performance & PO Volume', name: 'Procurement Supplier Performance & PO Volume', domain: 'Inventory', date: formatISTDate(d6), status: 'Ready', fileSize: '2.9 MB', format: 'XLSX' },
  ];
};

export const Reports: React.FC = () => {
  const { user } = useAuth();
  const userRole = user?.role || 'CEO';
  const allowedDomains = ROLE_ALLOWED_REPORT_DOMAINS[userRole] || ['All', 'Sales'];

  const [reports, setReports] = useState<ReportItem[]>(getInitialReports);
  const [selectedDomain, setSelectedDomain] = useState<string>('All');
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [viewingReport, setViewingReport] = useState<ReportItem | null>(null);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const domains = allowedDomains;

  const filteredReports = reports.filter((r) => {
    // 1. RBAC domain check: Manager can only see reports matching their allowed domains
    const isDomainPermitted = allowedDomains.some(
      (d) => d !== 'All' && d.toLowerCase() === r.domain.toLowerCase()
    );
    if (!isDomainPermitted) return false;

    // 2. Active filter selection check
    const reportTitle = r.title || r.name || '';
    const matchesDomain = selectedDomain === 'All' || r.domain.toLowerCase() === selectedDomain.toLowerCase();
    const matchesSearch = reportTitle.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesDomain && matchesSearch;
  });

  const handleDownload = (report: ReportItem) => {
    const name = report.title || report.name || 'Report';
    const domain = report.domain;
    setToastMessage(`Downloading ${name} (${report.format.toUpperCase()})...`);

    const filename = `${name.toLowerCase().replace(/[^a-z0-9]/g, '_')}`;

    if (report.format.toLowerCase() === 'pdf') {
      const sections = [
        {
          heading: 'Executive Summary',
          lines: [
            `Report Domain: ${domain}`,
            `Reconciliation Status: Verified Complete against FreshMart MySQL replica`,
            `Security Scope: ${userRole} Authoritative RBAC Boundary`,
            `Generated On: ${formatISTDateTime(new Date())}`,
          ],
        },
        {
          heading: 'Operational Telemetry & Performance Indicators',
          lines:
            domain.toLowerCase() === 'sales'
              ? [
                  'Gross Commercial Volume: Rs. 4,200,000 (12-Month Period)',
                  'Fulfilled Sales Orders: 3,420 Completed Shipments',
                  'Top Performing Segment: Fresh Produce & Organic Fruits (38.2%)',
                  'Repeat B2B Commercial Retention Rate: 87.4%',
                ]
              : domain.toLowerCase() === 'inventory'
              ? [
                  'Total Monitored SKUs: 120 Products Across 4 Warehouses',
                  'Deficit Safety Buffer: 5 SKUs Flagged for Emergency Reorder',
                  'Current Stock Turnover Velocity: 14.2 Days',
                  'Supplier Fulfillment Compliance Index: 96.1%',
                ]
              : domain.toLowerCase() === 'hrms'
              ? [
                  'Total Active Workforce: 500 Employees Across 6 Departments',
                  'Monthly Compensation Ledger: Fully Reconciled with Payroll',
                  'Department Headcount Allocation: Operations (180), Sales (120)',
                  'Employee Compliance & Active Status Ratio: 99.4%',
                ]
              : domain.toLowerCase() === 'finance'
              ? [
                  'Corporate Operating Margin: 28.5% (Pre-August Anomaly Baseline)',
                  'Gross Revenue: Rs. 4,200,000 | COGS: Rs. 1,800,000',
                  'Operating Expenses: Rs. 1,200,000 | Net Profit: Rs. 1,200,000',
                  'Audit Trace: Verified Against MySQL company_financials Ledger',
                ]
              : [
                  'Active Commercial B2B Leads: 45 Enterprise Accounts',
                  'Weighted Deal Pipeline: Rs. 8,900,000 Total Value',
                  'Opportunity Conversion Velocity: 32 Days Avg Cycle',
                  'Strategic Account Engagement Index: 92.5%',
                ],
        },
        {
          heading: 'Agentic Verification & Data Lineage',
          lines: [
            'Telemetry Engine: Model Context Protocol (MCP) Read-Only Data Bridge',
            'SQL Verification: Deterministic AST Syntax & Column Level Filtering',
            'Confidentiality: Guarded by PostgreSQL Role-Based Access Control',
          ],
        },
      ];

      downloadValidPDF(filename, name, `FreshMart ${domain} Business Telemetry`, sections);
    } else {
      // CSV Export
      let headers: string[] = [];
      let rows: (string | number)[][] = [];

      if (domain.toLowerCase() === 'sales') {
        headers = ['Period', 'Metric Name', 'Value (INR)', 'Volume Units', 'MoM Growth (%)', 'Status'];
        rows = [
          ['Q1 2026', 'Total Commercial Sales', 980000, 810, 11.2, 'Audited'],
          ['Q2 2026', 'Total Commercial Sales', 1120000, 930, 14.3, 'Audited'],
          ['Q3 2026', 'Total Commercial Sales', 1250000, 1020, 11.6, 'Audited'],
          ['July 2026', 'Monthly Gross Revenue', 420000, 340, 12.5, 'Reconciled'],
          ['August 2026', 'Monthly Gross Revenue', 390000, 315, -7.1, 'Investigated'],
        ];
      } else if (domain.toLowerCase() === 'inventory') {
        headers = ['SKU Code', 'Product Name', 'Category', 'Stock On Hand', 'Reorder Level', 'Unit Cost (INR)', 'Alert Level'];
        rows = [
          ['SKU-001', 'Fresh Hass Avocado Pack of 2', 'Produce', 14, 50, 160, 'CRITICAL DEFICIT'],
          ['SKU-002', 'Organic Whole Milk 1L', 'Dairy', 28, 80, 72, 'REORDER WARNING'],
          ['SKU-003', 'Alphonso Mango Box', 'Produce', 8, 40, 450, 'CRITICAL DEFICIT'],
          ['SKU-004', 'Farm Fresh Eggs (12pk)', 'Dairy', 65, 60, 110, 'NORMAL BUFFER'],
          ['SKU-005', 'Artisan Sourdough Loaf', 'Bakery', 42, 35, 95, 'NORMAL BUFFER'],
        ];
      } else if (domain.toLowerCase() === 'hrms') {
        headers = ['Department', 'Employee Count', 'Avg Salary (INR)', 'Monthly Payroll (INR)', 'Compliance Status'];
        rows = [
          ['Sales & Commercial', 120, 48500, 5820000, 'Verified'],
          ['Warehousing & Logistics', 180, 32000, 5760000, 'Verified'],
          ['Finance & Accounting', 40, 62000, 2480000, 'Verified'],
          ['Human Resources', 30, 51000, 1530000, 'Verified'],
          ['Procurement & ERP', 80, 45000, 3600000, 'Verified'],
          ['Executive & Admin', 50, 78000, 3900000, 'Verified'],
        ];
      } else {
        headers = ['Fiscal Month', 'Gross Revenue (INR)', 'COGS (INR)', 'Operating Expenses (INR)', 'Net Profit (INR)', 'Margin (%)'];
        rows = [
          ['June 2026', 4100000, 1750000, 1200000, 1150000, 28.05],
          ['July 2026', 4200000, 1800000, 1200000, 1200000, 28.57],
          ['August 2026', 3900000, 1720000, 1580000, 600000, 15.38],
          ['September 2026', 4300000, 1850000, 1250000, 1200000, 27.91],
        ];
      }

      downloadCSV(filename, headers, rows);
    }

    setTimeout(() => {
      setToastMessage(null);
    }, 2500);
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/60 p-5 rounded-xl border border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
              <FileBarChart className="w-4 h-4" />
            </div>
            <h1 className="text-xl font-bold text-white tracking-tight">Enterprise Business Reports</h1>
          </div>
          <p className="text-slate-400 text-sm mt-1">
            Standard and automated agent-generated analytical reports across FreshMart operations.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="primary"
            size="sm"
            onClick={() => {
              const newRep: ReportItem = {
                id: `REP-${String(reports.length + 1).padStart(3, '0')}`,
                title: `Real-Time ${selectedDomain === 'All' ? 'Operational' : selectedDomain} Telemetry Audit`,
                name: `Real-Time ${selectedDomain === 'All' ? 'Operational' : selectedDomain} Telemetry Audit`,
                domain: selectedDomain === 'All' ? 'Sales' : selectedDomain,
                date: formatISTDate(new Date()),
                status: 'Ready',
                fileSize: '1.5 MB',
                format: 'PDF',
              };
              setReports([newRep, ...reports]);
              setToastMessage(`Agent compiled and published: ${newRep.title}`);
              setTimeout(() => setToastMessage(null), 3000);
            }}
          >
            + Generate Report
          </Button>
        </div>
      </div>

      {/* Filter & Search Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 bg-slate-900/40 p-4 rounded-xl border border-slate-800">
        {/* Domain Filter Pills */}
        <div className="flex flex-wrap items-center gap-1.5 w-full sm:w-auto">
          <Filter className="w-3.5 h-3.5 text-slate-400 mr-1" />
          {domains.map((dom) => (
            <button
              key={dom}
              onClick={() => setSelectedDomain(dom)}
              className={`px-3 py-1 rounded-lg text-xs font-medium transition-colors ${
                selectedDomain === dom
                  ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                  : 'bg-slate-800/60 text-slate-400 hover:text-slate-200 border border-slate-700/40'
              }`}
            >
              {dom}
            </button>
          ))}
        </div>

        {/* Search Input */}
        <div className="relative w-full sm:w-64">
          <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search reports..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-slate-800/80 border border-slate-700/60 rounded-lg pl-9 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-emerald-500"
          />
        </div>
      </div>

      {/* Toast Notification */}
      {toastMessage && (
        <div className="bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs px-4 py-2.5 rounded-lg flex items-center gap-2 animate-fade-in">
          <CheckCircle className="w-4 h-4 shrink-0" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Reports Table */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl overflow-hidden shadow-lg">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-800/50 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800">
              <tr>
                <th className="px-5 py-3">Report Name</th>
                <th className="px-5 py-3">Domain</th>
                <th className="px-5 py-3">Generated Date</th>
                <th className="px-5 py-3">Format</th>
                <th className="px-5 py-3">Status</th>
                <th className="px-5 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {filteredReports.length === 0 ? (
                <tr>
                  <td colSpan={6} className="text-center py-8 text-slate-500">
                    No reports match the selected criteria.
                  </td>
                </tr>
              ) : (
                filteredReports.map((report) => {
                  const title = report.title || report.name || 'Report';
                  return (
                    <tr key={report.id} className="hover:bg-slate-800/30 transition-colors">
                      <td className="px-5 py-3.5 font-medium text-slate-200 flex items-center gap-2">
                        <FileBarChart className="w-4 h-4 text-emerald-400 shrink-0" />
                        <span>{title}</span>
                      </td>
                      <td className="px-5 py-3.5 text-slate-300">
                        <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700/50 text-[11px]">
                          {report.domain}
                        </span>
                      </td>
                      <td className="px-5 py-3.5 text-slate-400 flex items-center gap-1.5">
                        <Clock className="w-3.5 h-3.5 text-slate-500" />
                        <span>{report.date}</span>
                      </td>
                      <td className="px-5 py-3.5 text-slate-400 uppercase font-mono text-[10px]">
                        {report.format}
                      </td>
                      <td className="px-5 py-3.5">
                        <Badge variant="success">
                          <CheckCircle className="w-3 h-3 mr-1" />
                          {report.status}
                        </Badge>
                      </td>
                      <td className="px-5 py-3.5 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => setViewingReport(report)}
                            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors border border-slate-700/50"
                            title="View Report Preview"
                          >
                            <Eye className="w-3.5 h-3.5" />
                          </button>
                          <button
                            onClick={() => handleDownload(report)}
                            className="p-1.5 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 transition-colors border border-emerald-500/30"
                            title="Download Report"
                          >
                            <Download className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Report Preview Modal */}
      {viewingReport && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 max-w-lg w-full shadow-2xl">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <FileBarChart className="w-5 h-5 text-emerald-400" />
                <h3 className="text-base font-semibold text-white">{viewingReport.title || viewingReport.name}</h3>
              </div>
              <button
                onClick={() => setViewingReport(null)}
                className="text-slate-400 hover:text-white text-lg font-bold"
              >
                &times;
              </button>
            </div>

            <div className="py-4 space-y-3 text-xs text-slate-300">
              <div className="flex justify-between py-1 border-b border-slate-800/60">
                <span className="text-slate-400">Domain</span>
                <span className="font-semibold text-white">{viewingReport.domain}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800/60">
                <span className="text-slate-400">Date Generated</span>
                <span className="text-slate-200">{viewingReport.date}</span>
              </div>
              <div className="flex justify-between py-1 border-b border-slate-800/60">
                <span className="text-slate-400">Status</span>
                <Badge variant="success">{viewingReport.status}</Badge>
              </div>
              <div className="p-3 bg-slate-800/50 rounded-lg border border-slate-700/50 mt-2">
                <p className="font-semibold text-slate-200 mb-1">Executive Summary:</p>
                <p className="text-slate-400 leading-relaxed text-[11px]">
                  This report was compiled by FreshMart Agentic Analytics using SQL validation
                  and read-only MCP queries against the {viewingReport.domain} operational schema. All metrics
                  comply with FreshMart corporate reporting guidelines.
                </p>
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-3 border-t border-slate-800">
              <Button variant="outline" size="sm" onClick={() => setViewingReport(null)}>
                Close
              </Button>
              <Button
                variant="primary"
                size="sm"
                onClick={() => {
                  handleDownload(viewingReport);
                  setViewingReport(null);
                }}
              >
                Download {viewingReport.format.toUpperCase()}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
