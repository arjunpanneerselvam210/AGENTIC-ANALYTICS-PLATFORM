import React from 'react';
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
} from 'recharts';
import { Card } from '../common/Card';
import type { CategoryPoint } from '../../types/dashboard';

interface StockByCategoryChartProps {
  data?: CategoryPoint[];
}

export const StockByCategoryChart: React.FC<StockByCategoryChartProps> = ({ data = [] }) => {
  const totalUnits = data.reduce((acc, curr) => acc + curr.value, 0);

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const pct = totalUnits > 0 ? ((payload[0].value / totalUnits) * 100).toFixed(1) : 0;
      return (
        <div className="bg-[#0B0F19] border border-slate-700/80 rounded-xl p-3 shadow-xl text-xs">
          <p className="font-semibold text-white">{payload[0].name}</p>
          <p className="text-emerald-400 font-mono mt-0.5 font-bold">
            {payload[0].value.toLocaleString()} units ({pct}%)
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <Card className="flex flex-col">
      <div className="mb-2">
        <h3 className="text-sm font-bold text-white">Stock Volume by Category</h3>
        <p className="text-xs text-slate-400">Total physical inventory units on hand across catalog categories</p>
      </div>

      <div className="h-56 w-full relative flex items-center justify-center">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Tooltip content={<CustomTooltip />} />
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={55}
              outerRadius={80}
              paddingAngle={3}
              dataKey="value"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} stroke="#0F1626" strokeWidth={2} />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
          <span className="text-[10px] text-slate-400 font-medium">Total Units</span>
          <span className="text-sm font-bold text-white font-mono">
            {totalUnits > 1000 ? `${(totalUnits / 1000).toFixed(1)}k` : totalUnits}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-x-2 gap-y-1.5 mt-2 pt-3 border-t border-slate-800/80">
        {data.map((cat) => (
          <div key={cat.name} className="flex items-center justify-between text-xs py-0.5">
            <div className="flex items-center gap-1.5 truncate">
              <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ backgroundColor: cat.color }}></span>
              <span className="text-slate-300 truncate">{cat.name}</span>
            </div>
            <span className="font-mono text-slate-400 font-semibold">{cat.value.toLocaleString()}</span>
          </div>
        ))}
      </div>
    </Card>
  );
};
