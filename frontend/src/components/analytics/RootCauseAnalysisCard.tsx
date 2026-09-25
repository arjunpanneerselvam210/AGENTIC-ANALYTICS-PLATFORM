import React from 'react';
import {
  TrendingDown,
  ShieldCheck,
  Sparkles,
  Layers,
  Database
} from 'lucide-react';
import type { RootCauseAnalysis, ActionableRecommendation, InvestigationPlan } from '../../types/analytics';


interface RootCauseAnalysisCardProps {
  analysis: RootCauseAnalysis;
  recommendations?: ActionableRecommendation[];
  investigationPlan?: InvestigationPlan;
}

export const RootCauseAnalysisCard: React.FC<RootCauseAnalysisCardProps> = ({
  analysis,
  recommendations = [],
  investigationPlan
}) => {
  const { metrics, factors, period, confidence, summary } = analysis;

  const formatCurrency = (val?: number) => {
    if (val === undefined || val === null) return '₹0';
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(val);
  };

  return (
    <div className="bg-navy-900/80 border border-red-500/20 rounded-xl overflow-hidden backdrop-blur-md shadow-2xl">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-red-950/40 via-navy-900 to-navy-900 p-5 border-b border-navy-800/80 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-red-500/10 border border-red-500/30 flex items-center justify-center text-red-400">
            <TrendingDown className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-red-500/20 text-red-300 border border-red-500/30 uppercase tracking-wider">
                Root Cause Diagnostic
              </span>
              <span className="text-xs px-2 py-0.5 rounded-full bg-green-500/10 text-green-400 border border-green-500/20 flex items-center gap-1">
                <ShieldCheck className="w-3 h-3" />
                Evidence Confidence: {confidence}
              </span>
            </div>
            <h3 className="text-lg font-bold text-white mt-1">
              August 2026 Profit Contraction Analysis
            </h3>
          </div>
        </div>

        {/* Headline KPI Pill */}
        <div className="bg-navy-950/80 border border-red-500/30 rounded-xl px-4 py-2 flex items-center gap-3">
          <span className="text-xs text-slate-400">Net Profit Shift:</span>
          <span className="text-xl font-bold text-red-400">
            {metrics?.profit_change_pct ? `${metrics.profit_change_pct}%` : '-50.0%'}
          </span>
          <span className="text-xs text-slate-400">
            ({formatCurrency(metrics?.profit_change)})
          </span>
        </div>
      </div>

      <div className="p-6 space-y-6">
        {/* Executive Summary */}
        <div className="bg-navy-950/60 border border-navy-800/80 rounded-xl p-4">
          <p className="text-sm text-slate-300 leading-relaxed">
            {summary}
          </p>
        </div>

        {/* Investigation Plan Steps */}
        {investigationPlan && investigationPlan.steps?.length > 0 && (
          <div className="bg-navy-950/40 border border-blue-500/20 rounded-xl p-4">
            <div className="flex items-center gap-2 mb-3">
              <Layers className="w-4 h-4 text-blue-400" />
              <span className="text-xs font-semibold text-blue-300 uppercase tracking-wider">
                Agentic Investigation Plan Executed
              </span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-xs text-slate-300">
              {investigationPlan.steps.map((step, idx) => (
                <div key={idx} className="flex items-start gap-2 bg-navy-900/60 p-2 rounded-lg border border-navy-800">
                  <span className="w-4 h-4 rounded-full bg-blue-500/20 text-blue-400 flex items-center justify-center text-[10px] font-bold shrink-0 mt-0.5">
                    {idx + 1}
                  </span>
                  <span>{step}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Financial Comparison Table */}
        <div>
          <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
            Financial Baseline Comparison ({period?.previous} vs {period?.current})
          </h4>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-sm">
              <thead>
                <tr className="border-b border-navy-800 text-xs text-slate-400 uppercase bg-navy-950/40">
                  <th className="py-2.5 px-3">Metric</th>
                  <th className="py-2.5 px-3">{period?.previous || 'July 2026'}</th>
                  <th className="py-2.5 px-3">{period?.current || 'August 2026'}</th>
                  <th className="py-2.5 px-3">Nominal Delta</th>
                  <th className="py-2.5 px-3">% Growth</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-navy-800/60 text-slate-200">
                <tr className="hover:bg-navy-800/20">
                  <td className="py-2.5 px-3 font-medium">Gross Revenue</td>
                  <td className="py-2.5 px-3">{formatCurrency(metrics?.july_revenue)}</td>
                  <td className="py-2.5 px-3">{formatCurrency(metrics?.august_revenue)}</td>
                  <td className="py-2.5 px-3 text-red-400 font-mono">{formatCurrency(metrics?.revenue_change)}</td>
                  <td className="py-2.5 px-3 text-red-400 font-mono">{metrics?.revenue_change_pct}%</td>
                </tr>
                <tr className="hover:bg-navy-800/20">
                  <td className="py-2.5 px-3 font-medium">Cost of Goods Sold (COGS)</td>
                  <td className="py-2.5 px-3">{formatCurrency(metrics?.july_cogs)}</td>
                  <td className="py-2.5 px-3">{formatCurrency(metrics?.august_cogs)}</td>
                  <td className="py-2.5 px-3 text-red-400 font-mono">+{formatCurrency(metrics?.cogs_change)}</td>
                  <td className="py-2.5 px-3 text-red-400 font-mono">+{metrics?.cogs_change_pct}%</td>
                </tr>
                <tr className="hover:bg-navy-800/20">
                  <td className="py-2.5 px-3 font-medium">Operating Expenses</td>
                  <td className="py-2.5 px-3">{formatCurrency(metrics?.july_expenses)}</td>
                  <td className="py-2.5 px-3">{formatCurrency(metrics?.august_expenses)}</td>
                  <td className="py-2.5 px-3 text-red-400 font-mono">+{formatCurrency(metrics?.expenses_change)}</td>
                  <td className="py-2.5 px-3 text-red-400 font-mono">+{metrics?.expenses_change_pct}%</td>
                </tr>
                <tr className="bg-red-500/5 font-semibold text-white">
                  <td className="py-2.5 px-3">Net Profit</td>
                  <td className="py-2.5 px-3 text-green-400">{formatCurrency(metrics?.july_profit)}</td>
                  <td className="py-2.5 px-3 text-amber-400">{formatCurrency(metrics?.august_profit)}</td>
                  <td className="py-2.5 px-3 text-red-400 font-mono">{formatCurrency(metrics?.profit_change)}</td>
                  <td className="py-2.5 px-3 text-red-400 font-mono">{metrics?.profit_change_pct}%</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* Contributing Factors Breakdown */}
        <div>
          <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
            Contributing Factors (Ranked by Evidence Impact)
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {factors.map((factor, idx) => (
              <div
                key={idx}
                className="bg-navy-950/70 border border-navy-800 rounded-xl p-4 flex flex-col justify-between hover:border-red-500/30 transition-all"
              >
                <div>
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <span className="text-xs font-bold text-white flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-red-400" />
                      {factor.factor}
                    </span>
                    <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-green-500/10 text-green-400 border border-green-500/20">
                      {factor.confidence} Evidence
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-xs text-slate-400 mt-2 font-mono">
                    <div>
                      Baseline: <span className="text-slate-200">{formatCurrency(factor.previous_value)}</span>
                    </div>
                    <div>
                      August: <span className="text-slate-200">{formatCurrency(factor.current_value)}</span>
                    </div>
                  </div>
                </div>

                <div className="mt-3 pt-2 border-t border-navy-800/80 flex items-center justify-between text-xs">
                  <span className="text-red-400 font-semibold font-mono">
                    Variance: {factor.change_pct ? `${factor.change_pct > 0 ? '+' : ''}${factor.change_pct}%` : ''} ({formatCurrency(factor.change)})
                  </span>
                  {factor.source && (
                    <span className="text-[10px] text-slate-400 flex items-center gap-1">
                      <Database className="w-2.5 h-2.5 text-slate-400" />
                      {factor.source.join(', ')}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Actionable Recommendations */}
        {recommendations && recommendations.length > 0 && (
          <div>
            <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-2">
              <Sparkles className="w-3.5 h-3.5 text-blue-400" />
              Actionable Agent Recommendations
            </h4>
            <div className="space-y-2.5">
              {recommendations.map((rec, idx) => (
                <div
                  key={idx}
                  className="bg-navy-950/60 border border-blue-500/20 rounded-xl p-3.5 flex items-start gap-3"
                >
                  <div className="mt-0.5 shrink-0">
                    {rec.priority === 'HIGH' ? (
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-red-500/20 text-red-300 border border-red-500/30">
                        HIGH
                      </span>
                    ) : (
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30">
                        MEDIUM
                      </span>
                    )}
                  </div>
                  <div className="flex-1">
                    <h5 className="text-sm font-semibold text-white">
                      {rec.title}
                    </h5>
                    <p className="text-xs text-slate-300 mt-1">
                      {rec.suggested_action}
                    </p>
                    <div className="flex items-center gap-2 mt-2 text-[11px] text-slate-400">
                      <span>Reason: {rec.reason}</span>
                      <span>•</span>
                      <span className="text-blue-400">{rec.related_domain}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
