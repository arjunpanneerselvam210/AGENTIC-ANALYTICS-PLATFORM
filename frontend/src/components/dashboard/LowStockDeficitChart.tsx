import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';
import { Card } from '../common/Card';
import { AlertTriangle } from 'lucide-react';

interface LowStockDeficitChartProps {
  items?: Array<{
    product_id: string;
    product_name: string;
    category?: string;
    quantity_on_hand: number;
    reorder_level: number;
    deficit: number;
  }>;
}

export const LowStockDeficitChart: React.FC<LowStockDeficitChartProps> = ({ items = [] }) => {
  const chartData = items.slice(0, 8).map((it) => ({
    name: it.product_name.length > 18 ? it.product_name.slice(0, 18) + '...' : it.product_name,
    fullName: it.product_name,
    category: it.category || 'Retail',
    onHand: it.quantity_on_hand,
    reorderLevel: it.reorder_level,
    deficit: it.deficit,
  }));

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-[#0B0F19] border border-slate-700/80 rounded-xl p-3.5 shadow-2xl text-xs space-y-1.5 min-w-[210px]">
          <div className="flex items-center gap-1.5 text-rose-400 font-bold border-b border-slate-800 pb-1">
            <AlertTriangle className="w-3.5 h-3.5" />
            <span>{data.fullName}</span>
          </div>
          <div className="flex items-center justify-between text-slate-300">
            <span>Category:</span>
            <span className="font-mono text-slate-200">{data.category}</span>
          </div>
          <div className="flex items-center justify-between text-slate-300">
            <span>Current Stock:</span>
            <span className="font-mono font-bold text-amber-400">{data.onHand} units</span>
          </div>
          <div className="flex items-center justify-between text-slate-300">
            <span>Safety Reorder Level:</span>
            <span className="font-mono font-bold text-slate-300">{data.reorderLevel} units</span>
          </div>
          <div className="flex items-center justify-between text-rose-400 pt-1 border-t border-slate-800/80 font-bold">
            <span>Deficit to Restock:</span>
            <span className="font-mono">-{data.deficit} units</span>
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
            <h3 className="text-sm font-bold text-white">Critical Stock Deficits</h3>
            <span className="text-[10px] font-bold text-rose-400 bg-rose-500/10 border border-rose-500/20 px-2 py-0.5 rounded-full">
              Urgent PO Needed
            </span>
          </div>
          <p className="text-xs text-slate-400">Inventory on-hand compared against warehouse minimum safety reorder thresholds</p>
        </div>
        <div className="flex items-center gap-3 text-xs font-medium">
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded bg-amber-400"></span>
            <span className="text-slate-300">On-Hand</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded bg-slate-600"></span>
            <span className="text-slate-300">Target Threshold</span>
          </div>
        </div>
      </div>

      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            margin={{ top: 10, right: 10, left: -10, bottom: 25 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" vertical={false} />
            <XAxis
              dataKey="name"
              stroke="#64748B"
              fontSize={10}
              tickLine={false}
              axisLine={false}
              angle={-20}
              textAnchor="end"
              interval={0}
            />
            <YAxis
              stroke="#64748B"
              fontSize={11}
              tickLine={false}
              axisLine={false}
            />
            <Tooltip content={<CustomTooltip />} />
            <Bar
              dataKey="onHand"
              name="Stock On Hand"
              fill="#F59E0B"
              radius={[4, 4, 0, 0]}
              maxBarSize={28}
            />
            <Bar
              dataKey="reorderLevel"
              name="Safety Reorder Level"
              fill="#475569"
              radius={[4, 4, 0, 0]}
              maxBarSize={28}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
};
