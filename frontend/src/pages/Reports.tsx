import React, { useState } from 'react';
import { FileBarChart, Download, Eye, Filter, Search, CheckCircle, Clock } from 'lucide-react';
import { Badge } from '../components/common/Badge';
import { Button } from '../components/common/Button';
import { MOCK_REPORTS } from '../data/mockData';
import type { ReportItem } from '../types/dashboard';

export const Reports: React.FC = () => {
  const [reports] = useState<ReportItem[]>(MOCK_REPORTS as ReportItem[]);
  const [selectedDomain, setSelectedDomain] = useState<string>('All');
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [viewingReport, setViewingReport] = useState<ReportItem | null>(null);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const domains = ['All', 'Sales', 'Inventory', 'HRMS', 'Finance', 'CRM'];

  const filteredReports = reports.filter((r) => {
    const reportTitle = r.title || r.name || '';
    const matchesDomain = selectedDomain === 'All' || r.domain.toLowerCase() === selectedDomain.toLowerCase();
    const matchesSearch = reportTitle.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesDomain && matchesSearch;
  });

  const handleDownload = (report: ReportItem) => {
    const name = report.title || report.name || 'Report';
    setToastMessage(`Downloading ${name} (${report.format})...`);
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
              setToastMessage('Agent is compiling new scheduled executive report...');
              setTimeout(() => setToastMessage(null), 2500);
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
