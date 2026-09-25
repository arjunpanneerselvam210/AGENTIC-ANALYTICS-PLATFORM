import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Cell,
} from 'recharts';
import { Card } from '../common/Card';

interface CRMPipelineChartProps {
  pipeline?: Array<{
    status: string;
    count: number;
  }>;
}

const STAGE_COLORS: Record<string, string> = {
  New: '#3B82F6',
  Contacted: '#6366F1',
  Qualified: '#10B981',
  Proposal: '#F59E0B',
  Negotiation: '#EC4899',
  Won: '#059669',
  Lost: '#64748B',
};

export const CRMPipelineChart: React.FC<CRMPipelineChartProps> = ({ pipeline = [] }) => {
  const totalLeads = pipeline.reduce((acc, curr) => acc + curr.count, 0);

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      const pct = totalLeads > 0 ? ((data.count / totalLeads) * 100).toFixed(1) : 0;
      return (
        <div className="bg-[#0B0F19] border border-slate-700/80 rounded-xl p-3 shadow-xl text-xs space-y-1">
          <p className="font-bold text-white border-b border-slate-800 pb-1">{data.status} Stage</p>
          <div className="flex items-center justify-between gap-4 text-slate-300">
            <span>Leads Volume:</span>
            <span className="font-mono font-bold text-emerald-400">{data.count} leads</span>
          </div>
          <div className="flex items-center justify-between gap-4 text-slate-400 text-[11px]">
            <span>Pipeline Share:</span>
            <span className="font-mono text-slate-200">{pct}%</span>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <Card className="flex flex-col">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
        <div>
          <h3 className="text-sm font-bold text-white">Commercial CRM Pipeline Stages</h3>
          <p className="text-xs text-slate-400">Distribution of commercial prospects across the qualification funnel</p>
        </div>
        <div className="text-xs font-mono bg-slate-800/80 px-2.5 py-1 rounded-lg border border-slate-700 text-slate-300">
          Total: <strong className="text-emerald-400">{totalLeads}</strong> active leads
        </div>
      </div>

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={pipeline}
            layout="vertical"
            margin={{ top: 5, right: 25, left: 10, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" horizontal={false} />
            <XAxis
              type="number"
              stroke="#64748B"
              fontSize={11}
              tickLine={false}
              axisLine={false}
            />
            <YAxis
              type="category"
              dataKey="status"
              stroke="#64748B"
              fontSize={11}
              tickLine={false}
              axisLine={false}
              width={85}
            />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="count" radius={[0, 4, 4, 0]} maxBarSize={22}>
              {pipeline.map((entry, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={STAGE_COLORS[entry.status] || '#10B981'}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
};
