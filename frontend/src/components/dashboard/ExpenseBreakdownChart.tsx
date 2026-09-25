import React from 'react';
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
} from 'recharts';
import { Card } from '../common/Card';

interface ExpenseBreakdownChartProps {
  data?: Array<{
    category: string;
    total: number;
  }>;
}

const EXPENSE_COLORS = ['#10B981', '#06B6D4', '#6366F1', '#F59E0B', '#EC4899', '#8B5CF6'];

export const ExpenseBreakdownChart: React.FC<ExpenseBreakdownChartProps> = ({ data = [] }) => {
  const chartData = data.map((d, i) => ({
    name: d.category,
    value: d.total,
    color: EXPENSE_COLORS[i % EXPENSE_COLORS.length],
  }));

  const totalExpense = data.reduce((acc, curr) => acc + curr.total, 0);

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const pct = totalExpense > 0 ? ((payload[0].value / totalExpense) * 100).toFixed(1) : 0;
      return (
        <div className="bg-[#0B0F19] border border-slate-700/80 rounded-lg p-2.5 shadow-xl text-xs">
          <p className="font-semibold text-white">{payload[0].name}</p>
          <p className="text-amber-400 font-mono mt-0.5">
            ₹{(payload[0].value / 100000).toFixed(1)}L ({pct}%)
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <Card className="flex flex-col">
      <div className="mb-2">
        <h3 className="text-sm font-bold text-white">Operating Expense Allocations</h3>
        <p className="text-xs text-slate-400">Expense distribution across operating categories and workforce</p>
      </div>

      <div className="h-56 w-full relative flex items-center justify-center">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Tooltip content={<CustomTooltip />} />
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              innerRadius={55}
              outerRadius={80}
              paddingAngle={3}
              dataKey="value"
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} stroke="#0F1626" strokeWidth={2} />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
          <span className="text-[10px] text-slate-400 font-medium">Total Ledger</span>
          <span className="text-sm font-bold text-white font-mono">
            ₹{(totalExpense / 10000000).toFixed(1)}Cr
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-x-2 gap-y-1 mt-3 pt-3 border-t border-slate-800/60">
        {chartData.slice(0, 4).map((c) => (
          <div key={c.name} className="flex items-center gap-1.5 text-[11px]">
            <span className="w-2 h-2 rounded-full shrink-0" style={{ backgroundColor: c.color }} />
            <span className="text-slate-300 truncate">{c.name}</span>
          </div>
        ))}
      </div>
    </Card>
  );
};
