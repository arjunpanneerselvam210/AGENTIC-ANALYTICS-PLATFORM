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

interface CategoryChartProps {
  data: CategoryPoint[];
}

export const CategoryChart: React.FC<CategoryChartProps> = ({ data }) => {
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-[#0B0F19] border border-slate-700/80 rounded-lg p-2.5 shadow-xl text-xs">
          <p className="font-semibold text-white">{payload[0].name}</p>
          <p className="text-emerald-400 font-mono mt-0.5">{payload[0].value}% of Total Orders</p>
        </div>
      );
    }
    return null;
  };

  return (
    <Card className="flex flex-col">
      <div className="mb-2">
        <h3 className="text-sm font-bold text-white">Orders by Product Category</h3>
        <p className="text-xs text-slate-400">Order share distribution across operating segments</p>
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
          <span className="text-xs text-slate-400 font-medium">Categories</span>
          <span className="text-base font-bold text-white font-mono">{data.length}</span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-x-2 gap-y-1.5 mt-2 pt-3 border-t border-slate-800/80">
        {data.map((cat) => (
          <div key={cat.name} className="flex items-center justify-between text-xs py-0.5">
            <div className="flex items-center gap-1.5 truncate">
              <span className="w-2 h-2 rounded-full flex-shrink-0" style={{ backgroundColor: cat.color }}></span>
              <span className="text-slate-300 truncate">{cat.name}</span>
            </div>
            <span className="font-mono text-slate-400 font-semibold">{cat.value}%</span>
          </div>
        ))}
      </div>
    </Card>
  );
};
