import React from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ReferenceLine,
} from 'recharts';
import { Card } from '../common/Card';
import { Percent } from 'lucide-react';


interface ProfitMarginTrendChartProps {
  data?: Array<{
    fiscal_year: number;
    month_name: string;
    total_revenue: number;
    cogs: number;
    operating_expenses: number;
    net_profit: number;
    profit_margin_pct: number;
  }>;
}

export const ProfitMarginTrendChart: React.FC<ProfitMarginTrendChartProps> = ({ data = [] }) => {
  const chartData = data.map((d) => ({
    period: `${d.month_name.slice(0, 3)} ${String(d.fiscal_year).slice(2)}`,
    margin: Number(d.profit_margin_pct || 0),
    profit: Number(d.net_profit || 0),
    isAugust: d.month_name === 'August' && d.fiscal_year === 2026,
  }));

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const isAug = payload[0].payload.isAugust;
      return (
        <div className="bg-[#0B0F19] border border-slate-700/80 rounded-xl p-3 shadow-xl text-xs space-y-1 min-w-[170px]">
          <div className="flex items-center justify-between border-b border-slate-800 pb-1">
            <span className="font-bold text-white">{label}</span>
            {isAug && (
              <span className="text-[10px] bg-rose-500/20 text-rose-400 font-bold px-1.5 py-0.5 rounded">
                Variance Outlier
              </span>
            )}
          </div>
          <div className="flex items-center justify-between text-slate-300">
            <span>Net Margin:</span>
            <span className={`font-mono font-bold ${isAug ? 'text-rose-400' : 'text-emerald-400'}`}>
              {payload[0].value.toFixed(1)}%
            </span>
          </div>
          <div className="flex items-center justify-between text-slate-400 text-[11px]">
            <span>Net Profit:</span>
            <span className="font-mono text-slate-200">
              ₹{(payload[0].payload.profit / 100000).toFixed(1)}L
            </span>
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
          <div className="flex items-center gap-2">
            <h3 className="text-sm font-bold text-white">Corporate Net Margin % Trajectory</h3>
            <span className="text-[10px] font-bold text-teal-400 bg-teal-500/10 border border-teal-500/20 px-2 py-0.5 rounded-full flex items-center gap-1">
              <Percent className="w-3 h-3" />
              <span>Target: &gt;20%</span>
            </span>
          </div>
          <p className="text-xs text-slate-400">Monthly net profit margin corridor with August outlier detection</p>
        </div>
        <div className="flex items-center gap-2 text-xs">
          <span className="w-2.5 h-2.5 rounded-full bg-teal-400"></span>
          <span className="text-slate-300">Margin %</span>
        </div>
      </div>

      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 10, right: 15, left: -10, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" vertical={false} />
            <XAxis dataKey="period" stroke="#64748B" fontSize={11} tickLine={false} />
            <YAxis
              stroke="#64748B"
              fontSize={11}
              tickLine={false}
              tickFormatter={(v) => `${v}%`}
              domain={[0, 35]}
            />
            <Tooltip content={<CustomTooltip />} />
            <ReferenceLine y={20} stroke="#475569" strokeDasharray="4 4" label={{ value: '20% Target', fill: '#94A3B8', fontSize: 10 }} />
            <Line
              type="monotone"
              dataKey="margin"
              stroke="#2DD4BF"
              strokeWidth={2.5}
              dot={(props: any) => {
                const isAug = props.payload?.isAugust;
                return (
                  <circle
                    key={props.key}
                    cx={props.cx}
                    cy={props.cy}
                    r={isAug ? 6 : 3.5}
                    fill={isAug ? '#F43F5E' : '#2DD4BF'}
                    stroke={isAug ? '#FFE4E6' : '#0B0F19'}
                    strokeWidth={2}
                  />
                );
              }}
              activeDot={{ r: 7 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
};
