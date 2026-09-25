import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../common/Card';
import { TrendingDown, AlertCircle, Sparkles } from 'lucide-react';
import { Button } from '../common/Button';

interface RootCauseHighlightCardProps {
  data?: {
    period: string;
    july_profit: number;
    august_profit: number;
    change_pct: number;
    primary_driver: string;
    cogs_expansion: string;
    action_taken: string;
  };
}

export const RootCauseHighlightCard: React.FC<RootCauseHighlightCardProps> = ({ data }) => {
  const navigate = useNavigate();

  if (!data) return null;

  const handleLaunchDeepDive = () => {
    navigate('/analytics?q=Why%20did%20profit%20decrease%20in%20August%3F');
  };

  return (
    <Card className="border border-rose-500/30 bg-gradient-to-br from-rose-950/20 via-[#0B0F19] to-[#0B0F19] p-5 relative overflow-hidden">
      <div className="absolute top-0 right-0 w-64 h-64 bg-rose-500/5 rounded-full blur-3xl pointer-events-none" />

      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-rose-500/20">
        <div>
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-rose-500/15 text-rose-400 border border-rose-500/30 text-[11px] font-semibold">
              <AlertCircle className="w-3.5 h-3.5" />
              <span>Centerpiece Root-Cause Diagnostic</span>
            </span>
            <span className="text-[11px] text-slate-400 font-mono">{data.period}</span>
          </div>
          <h3 className="text-base font-bold text-white mt-1.5">
            August 2026 Fiscal Anomaly: Net Profit Contraction ({data.change_pct}%)
          </h3>
          <p className="text-xs text-slate-300 mt-0.5">
            Verified financial variance isolated across freight invoices and spot procurement premiums
          </p>
        </div>

        <Button
          variant="primary"
          size="sm"
          onClick={handleLaunchDeepDive}
          className="shrink-0 bg-rose-600 hover:bg-rose-500 border-rose-500 text-white shadow-lg shadow-rose-950/40"
          icon={<Sparkles className="w-3.5 h-3.5" />}
        >
          Run Root-Cause AI Deep Dive
        </Button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 my-4">
        <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
          <span className="text-[11px] text-slate-400 font-medium block">Baseline (July 2026)</span>
          <span className="text-xl font-bold font-mono text-emerald-400 mt-0.5 block">
            ₹{(data.july_profit / 100000).toFixed(1)}L
          </span>
          <span className="text-[10px] text-slate-500">Normal operating run-rate</span>
        </div>

        <div className="p-3 rounded-xl bg-slate-900/60 border border-rose-900/40">
          <span className="text-[11px] text-slate-400 font-medium block">Trough (August 2026)</span>
          <span className="text-xl font-bold font-mono text-rose-400 mt-0.5 block">
            ₹{(data.august_profit / 100000).toFixed(1)}L
          </span>
          <span className="text-[10px] text-rose-400/80 flex items-center gap-1">
            <TrendingDown className="w-3 h-3" />
            <span>-50.0% variance contraction</span>
          </span>
        </div>

        <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
          <span className="text-[11px] text-slate-400 font-medium block">Primary Ledger Outlier</span>
          <span className="text-xs font-semibold text-amber-300 mt-1 block">
            Emergency Air Freight Spike
          </span>
          <span className="text-[10px] text-slate-400">+381.4% surge (+₹3.41L)</span>
        </div>
      </div>

      <div className="text-xs text-slate-300 bg-slate-900/40 p-3 rounded-xl border border-slate-800/80 flex items-start gap-2.5">
        <div className="w-2 h-2 rounded-full bg-rose-400 shrink-0 mt-1.5" />
        <div>
          <span className="font-semibold text-white">Root-Cause Telemetry Attribution: </span>
          <span>{data.primary_driver} Secondary cost driver: {data.cogs_expansion}. Corrective policy: {data.action_taken}</span>
        </div>
      </div>
    </Card>
  );
};
