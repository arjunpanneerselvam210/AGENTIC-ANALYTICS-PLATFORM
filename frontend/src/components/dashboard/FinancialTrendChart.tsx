import React from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts';
import { Card } from '../common/Card';

interface FinancialTrendChartProps {
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

export const FinancialTrendChart: React.FC<FinancialTrendChartProps> = ({ data = [] }) => {
  const chartData = data.map((d) => ({
    period: `${d.month_name.slice(0, 3)} ${String(d.fiscal_year).slice(2)}`,
    revenue: d.total_revenue,
    expenses: d.cogs + d.operating_expenses,
    profit: d.net_profit,
  }));

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-[#0B0F19] border border-slate-700/80 rounded-lg p-3 shadow-xl text-xs space-y-1">
          <p className="font-semibold text-white mb-1.5">{label}</p>
          <div className="flex items-center justify-between gap-4 text-emerald-400">
            <span>Revenue:</span>
            <span className="font-mono font-semibold">₹{(payload[0].value / 100000).toFixed(1)}L</span>
          </div>
          <div className="flex items-center justify-between gap-4 text-amber-400">
            <span>Total Expenses:</span>
            <span className="font-mono font-semibold">₹{(payload[1].value / 100000).toFixed(1)}L</span>
          </div>
          <div className="flex items-center justify-between gap-4 text-teal-300">
            <span>Net Profit:</span>
            <span className="font-mono font-semibold">₹{(payload[2].value / 100000).toFixed(1)}L</span>
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
          <h3 className="text-sm font-bold text-white">12-Month P&L Velocity: Revenue, Expenses & Net Profit</h3>
          <p className="text-xs text-slate-400">Monthly corporate operating performance and margin trajectory</p>
        </div>
        <div className="flex items-center gap-3 text-xs">
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
            <span className="text-slate-300 text-[11px]">Revenue</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500" />
            <span className="text-slate-300 text-[11px]">Expenses</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-teal-400" />
            <span className="text-slate-300 text-[11px]">Net Profit</span>
          </div>
        </div>
      </div>

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
            <defs>
              <linearGradient id="colorRev" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10B981" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#10B981" stopOpacity={0.0} />
              </linearGradient>
              <linearGradient id="colorExp" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#F59E0B" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#F59E0B" stopOpacity={0.0} />
              </linearGradient>
              <linearGradient id="colorProf" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#2DD4BF" stopOpacity={0.5} />
                <stop offset="95%" stopColor="#2DD4BF" stopOpacity={0.0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" vertical={false} />
            <XAxis dataKey="period" stroke="#64748B" fontSize={11} tickLine={false} axisLine={false} />
            <YAxis
              stroke="#64748B"
              fontSize={11}
              tickLine={false}
              axisLine={false}
              tickFormatter={(v) => `₹${(v / 100000).toFixed(0)}L`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Area type="monotone" dataKey="revenue" stroke="#10B981" strokeWidth={2} fillOpacity={1} fill="url(#colorRev)" />
            <Area type="monotone" dataKey="expenses" stroke="#F59E0B" strokeWidth={2} fillOpacity={1} fill="url(#colorExp)" />
            <Area type="monotone" dataKey="profit" stroke="#2DD4BF" strokeWidth={2.5} fillOpacity={1} fill="url(#colorProf)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
};
