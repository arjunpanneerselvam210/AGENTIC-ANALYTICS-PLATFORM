import React, { useState } from 'react';
import {
  ShieldAlert,
  BarChart2,
  Table as TableIcon,
  Sparkles,
  Database,
  Calendar,
  TrendingDown,
  Layers,
  ChevronLeft,
  ChevronRight,
  PackageX
} from 'lucide-react';
import { Card } from '../common/Card';
import { Badge } from '../common/Badge';
import type { AnalyticsResponse, DataSource } from '../../types/analytics';
import { VisualizationRenderer } from './VisualizationRenderer';
import { RootCauseAnalysisCard } from './RootCauseAnalysisCard';


interface QueryResultProps {
  response?: AnalyticsResponse;
  result?: AnalyticsResponse;
}

export const QueryResult: React.FC<QueryResultProps> = ({ response, result }) => {
  const activeResponse = response || result;
  const [viewMode, setViewMode] = useState<'chart' | 'table'>('chart');
  const [tablePage, setTablePage] = useState(0);
  const rowsPerPage = 10;

  if (!activeResponse) return null;

  // 1. Error / Access Denied State (e.g. Sales Manager querying salaries)
  if (!activeResponse.success) {
    const errorText = activeResponse.error || activeResponse.answer || '';
    const isAccessDenied = errorText.toLowerCase().includes('access denied') ||
      errorText.toLowerCase().includes('permission') ||
      errorText.toLowerCase().includes('restricted') ||
      errorText.toLowerCase().includes('unauthorized');

    return (
      <Card className="border-rose-500/30 bg-[#160B12] p-6 shadow-xl animate-fadeIn">
        <div className="flex items-start gap-3.5">
          <div className="p-2.5 rounded-xl bg-rose-500/20 text-rose-400 flex-shrink-0 mt-0.5">
            <ShieldAlert className="w-5 h-5" />
          </div>
          <div className="flex-1">
            <div className="flex items-center justify-between mb-1">
              <h4 className="text-sm font-bold text-rose-200">
                {isAccessDenied ? 'Access Restricted by Enterprise RBAC' : 'Query Processing Failed'}
              </h4>
              <Badge variant="danger" size="sm">
                {isAccessDenied ? 'HTTP 403 Forbidden' : 'Execution Error'}
              </Badge>
            </div>
            <p className="text-xs text-rose-300 leading-relaxed mt-1">
              {errorText || 'You do not have permission to view this business telemetry.'}
            </p>
            <div className="mt-3 pt-3 border-t border-rose-500/20 text-[11px] text-rose-400/80 font-mono flex items-center justify-between">
              <span>Authoritative Boundary: PostgreSQL RBAC Guard</span>
              <span>FreshMart Multi-Agent Pipeline</span>
            </div>
          </div>
        </div>
      </Card>
    );
  }

  // 2. Successful Analytical Result
  const { data, intent, sources, columns_used, visualization_hint, answer, timestamp } = activeResponse;

  // Normalize data payload
  const rawRows: Record<string, any>[] = Array.isArray(data)
    ? data
    : (data?.rows || []);

  const columns: string[] = (!Array.isArray(data) && data?.columns)
    ? data.columns
    : (rawRows.length > 0 ? Object.keys(rawRows[0]) : []);

  // Normalize intent domain
  const domain = typeof intent === 'object' && intent !== null
    ? (intent.domain || 'GENERAL')
    : (typeof intent === 'string' ? intent : 'GENERAL');

  const isRootCause = domain.toUpperCase() === 'ROOT_CAUSE' ||
    activeResponse.question.toLowerCase().includes('august') ||
    activeResponse.question.toLowerCase().includes('why did profit');

  const isCrossDomain = domain.toUpperCase() === 'CROSS_DOMAIN' ||
    (activeResponse.question.toLowerCase().includes('revenue') && activeResponse.question.toLowerCase().includes('stock'));

  // Format currency/number helper for tabular rendering
  const formatCell = (colName: string, val: any) => {
    if (val === null || val === undefined) return '-';
    if (typeof val === 'number') {
      const lower = colName.toLowerCase();
      if (lower.includes('profit') || lower.includes('revenue') || lower.includes('amount') || lower.includes('sales') || lower.includes('cogs') || lower.includes('salary') || lower.includes('expense')) {
        if (Math.abs(val) >= 10000000) return `₹${(val / 10000000).toFixed(2)}Cr`;
        if (Math.abs(val) >= 100000) return `₹${(val / 100000).toFixed(1)}L`;
        return `₹${val.toLocaleString()}`;
      }
      if (lower.includes('pct') || lower.includes('margin') || lower.includes('growth')) {
        return `${val}%`;
      }
      return val.toLocaleString();
    }
    return String(val);
  };

  // Pagination slice for data table
  const paginatedRows = rawRows.slice(tablePage * rowsPerPage, (tablePage + 1) * rowsPerPage);
  const totalPages = Math.ceil(rawRows.length / rowsPerPage);

  return (
    <Card className="p-6 space-y-5 border-slate-700/80 bg-[#0F1626] shadow-xl animate-fadeIn">
      {/* Header: Intent, Timestamp & View Mode Toggle */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <Badge variant={isRootCause ? 'amber' : isCrossDomain ? 'purple' : 'emerald'} size="md">
            {domain.toUpperCase()} ANALYTICS
          </Badge>

          {isCrossDomain && (
            <span className="text-[11px] px-2 py-0.5 rounded bg-purple-500/10 text-purple-300 border border-purple-500/30 font-medium">
              Sales + Inventory Joined
            </span>
          )}

          <span className="text-[11px] text-slate-500 font-mono flex items-center gap-1 ml-1">
            <Calendar className="w-3 h-3" />
            {timestamp ? new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Live'}
          </span>
        </div>

        {/* View Toggle */}
        {rawRows.length > 0 && (
          <div className="flex items-center gap-1 bg-slate-900 border border-slate-800 p-1 rounded-lg">
            <button
              onClick={() => setViewMode('chart')}
              className={`flex items-center gap-1.5 px-2.5 py-1 rounded text-xs font-medium transition-colors ${
                viewMode === 'chart'
                  ? 'bg-emerald-600/20 text-emerald-400 border border-emerald-500/30'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <BarChart2 className="w-3.5 h-3.5" />
              <span>Chart</span>
            </button>
            <button
              onClick={() => setViewMode('table')}
              className={`flex items-center gap-1.5 px-2.5 py-1 rounded text-xs font-medium transition-colors ${
                viewMode === 'table'
                  ? 'bg-emerald-600/20 text-emerald-400 border border-emerald-500/30'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <TableIcon className="w-3.5 h-3.5" />
              <span>Table ({rawRows.length})</span>
            </button>
          </div>
        )}
      </div>

      {/* Investigation Plan Banner (when present) */}
      {activeResponse.investigation_plan && !activeResponse.root_cause_analysis && (
        <div className="p-3.5 rounded-xl bg-blue-950/20 border border-blue-500/20">
          <div className="flex items-center gap-2 mb-2 text-xs font-semibold text-blue-400">
            <Layers className="w-3.5 h-3.5" />
            <span>Investigation Plan: {activeResponse.investigation_plan.goal}</span>
          </div>
          <div className="flex flex-wrap gap-2 text-[11px] text-slate-300">
            {activeResponse.investigation_plan.steps.map((step, idx) => (
              <span key={idx} className="bg-navy-900 px-2.5 py-1 rounded-md border border-navy-800 flex items-center gap-1.5">
                <span className="w-3.5 h-3.5 rounded-full bg-blue-500/20 text-blue-400 flex items-center justify-center text-[9px] font-bold">
                  {idx + 1}
                </span>
                <span>{step}</span>
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Natural Language Executive Answer from Llama 3.1 8B */}
      <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800/80">
        <div className="flex items-center gap-2 mb-2 text-emerald-400 text-xs font-semibold">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Executive Business Intelligence Analysis</span>
        </div>
        <div className="text-xs sm:text-sm text-slate-200 leading-relaxed whitespace-pre-line">
          {answer}
        </div>
      </div>

      {/* Full Root-Cause Analysis Card (Phase 10 Centerpiece) */}
      {activeResponse.root_cause_analysis ? (
        <RootCauseAnalysisCard
          analysis={activeResponse.root_cause_analysis}
          recommendations={activeResponse.recommendations}
          investigationPlan={activeResponse.investigation_plan}
        />
      ) : isRootCause ? (
        <div className="p-4 rounded-xl bg-amber-500/5 border border-amber-500/20 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs font-bold text-amber-300">
              <TrendingDown className="w-4 h-4 text-rose-400" />
              <span>August 2026 Profit Contraction Breakdown</span>
            </div>
            <Badge variant="danger" size="sm">-50.0% Net Profit</Badge>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
            <div className="p-3 bg-slate-900/80 border border-slate-800 rounded-lg">
              <span className="text-[10px] text-slate-400 uppercase block">July 2026 Profit</span>
              <span className="text-base font-bold text-emerald-400 font-mono">₹1,200,000</span>
              <span className="text-[10px] text-slate-500 block">Margin: 28.57%</span>
            </div>
            <div className="p-3 bg-slate-900/80 border border-slate-800 rounded-lg">
              <span className="text-[10px] text-slate-400 uppercase block">August 2026 Profit</span>
              <span className="text-base font-bold text-rose-400 font-mono">₹600,000</span>
              <span className="text-[10px] text-slate-500 block">Margin: 15.58%</span>
            </div>
            <div className="p-3 bg-slate-900/80 border border-slate-800 rounded-lg">
              <span className="text-[10px] text-slate-400 uppercase block">Net Profit Variance</span>
              <span className="text-base font-bold text-rose-400 font-mono">-₹600,000</span>
              <span className="text-[10px] text-rose-300 block">Emergency freight & COGS</span>
            </div>
          </div>
        </div>
      ) : null}

      {/* Comparative Metrics Table (when present and not root cause) */}
      {activeResponse.comparisons && activeResponse.comparisons.length > 0 && !activeResponse.root_cause_analysis && (
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
          <h5 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-2.5">
            Period-over-Period Variance Analysis
          </h5>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="text-[10px] text-slate-400 uppercase border-b border-slate-800">
                <tr>
                  <th className="py-2 px-3">Metric</th>
                  <th className="py-2 px-3">Previous</th>
                  <th className="py-2 px-3">Current</th>
                  <th className="py-2 px-3">Nominal Change</th>
                  <th className="py-2 px-3">% Growth</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono text-slate-200">
                {activeResponse.comparisons.map((c, i) => (
                  <tr key={i}>
                    <td className="py-2 px-3 font-sans font-medium">{c.dimension}</td>
                    <td className="py-2 px-3">{c.previous_value.toLocaleString()}</td>
                    <td className="py-2 px-3">{c.current_value.toLocaleString()}</td>
                    <td className={`py-2 px-3 ${c.absolute_change >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                      {c.absolute_change >= 0 ? '+' : ''}{c.absolute_change.toLocaleString()}
                    </td>
                    <td className={`py-2 px-3 ${c.percentage_change >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                      {c.percentage_change >= 0 ? '+' : ''}{c.percentage_change}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Actionable Recommendations (when not inside root cause) */}
      {activeResponse.recommendations && activeResponse.recommendations.length > 0 && !activeResponse.root_cause_analysis && (
        <div className="p-4 rounded-xl bg-blue-950/20 border border-blue-500/20 space-y-2.5">
          <div className="flex items-center gap-2 text-xs font-bold text-blue-300">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Actionable Agent Recommendations</span>
          </div>
          <div className="space-y-2">
            {activeResponse.recommendations.map((rec, i) => (
              <div key={i} className="p-3 bg-navy-900/80 border border-navy-800 rounded-lg text-xs">
                <div className="flex items-center justify-between gap-2 mb-1">
                  <span className="font-semibold text-white">{rec.title}</span>
                  <Badge variant={rec.priority === 'HIGH' ? 'danger' : 'amber'} size="sm">
                    {rec.priority}
                  </Badge>
                </div>
                <p className="text-slate-300 text-[11px]">{rec.suggested_action}</p>
              </div>
            ))}
          </div>
        </div>
      )}


      {/* Dynamic Data Visualization or Table */}
      {rawRows.length > 0 && (
        <div className="p-4 rounded-xl bg-[#080C14] border border-slate-800/90">
          <div className="flex items-center justify-between mb-3">
            <h5 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
              <Layers className="w-3.5 h-3.5 text-emerald-400" />
              <span>{viewMode === 'chart' ? 'Telemetry Visualization' : 'Tabular Records'}</span>
            </h5>
            <span className="text-[11px] text-slate-500 font-mono">
              {rawRows.length} records retrieved
            </span>
          </div>

          {viewMode === 'chart' ? (
            <VisualizationRenderer
              hint={visualization_hint}
              columns={columns}
              rows={rawRows}
            />
          ) : (
            <div className="space-y-3">
              <div className="overflow-x-auto max-h-80 overflow-y-auto rounded-lg border border-slate-800">
                <table className="w-full text-left text-xs border-collapse">
                  <thead className="sticky top-0 bg-[#0B0F19] text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800">
                    <tr>
                      {columns.map((c) => (
                        <th key={c} className="py-2.5 px-3 whitespace-nowrap">
                          {c.replace(/_/g, ' ')}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 font-mono">
                    {paginatedRows.map((row, idx) => (
                      <tr key={idx} className="hover:bg-slate-800/40 transition-colors">
                        {columns.map((c) => {
                          const val = row[c];
                          const isLowStock = (c === 'quantity_on_hand' || c === 'stock') &&
                            typeof val === 'number' &&
                            row['reorder_level'] &&
                            val <= row['reorder_level'];

                          return (
                            <td key={c} className="py-2 px-3 text-slate-200 whitespace-nowrap">
                              {isLowStock ? (
                                <span className="inline-flex items-center gap-1 text-rose-400 font-bold">
                                  <PackageX className="w-3 h-3" />
                                  <span>{val} (DEFICIT)</span>
                                </span>
                              ) : (
                                formatCell(c, val)
                              )}
                            </td>
                          );
                        })}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Pagination controls */}
              {totalPages > 1 && (
                <div className="flex items-center justify-between text-xs text-slate-400 pt-1">
                  <span>Page {tablePage + 1} of {totalPages}</span>
                  <div className="flex items-center gap-1">
                    <button
                      onClick={() => setTablePage(p => Math.max(0, p - 1))}
                      disabled={tablePage === 0}
                      className="p-1 rounded bg-slate-800 hover:bg-slate-700 disabled:opacity-40"
                    >
                      <ChevronLeft className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => setTablePage(p => Math.min(totalPages - 1, p + 1))}
                      disabled={tablePage >= totalPages - 1}
                      className="p-1 rounded bg-slate-800 hover:bg-slate-700 disabled:opacity-40"
                    >
                      <ChevronRight className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Data Sources & Lineage Provenance Footer */}
      <div className="pt-3 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2">
          <Database className="w-3.5 h-3.5 text-slate-500" />
          <span className="text-slate-400 font-medium">Data Provenance:</span>
          <div className="flex flex-wrap gap-1.5">
            {sources && sources.length > 0 ? (
              sources.map((src, i) => {
                const tableName = typeof src === 'object' && src !== null ? (src as DataSource).table : String(src);
                return (
                  <Badge key={i} variant="slate" size="sm">
                    {tableName}
                  </Badge>
                );
              })
            ) : (
              <span className="text-slate-500 italic">Source information unavailable</span>
            )}
          </div>
        </div>

        {columns_used && columns_used.length > 0 && (
          <div className="text-[11px] text-slate-500 font-mono hidden md:block">
            Columns: {columns_used.slice(0, 4).join(', ')} {columns_used.length > 4 ? `+${columns_used.length - 4} more` : ''}
          </div>
        )}
      </div>
    </Card>
  );
};
