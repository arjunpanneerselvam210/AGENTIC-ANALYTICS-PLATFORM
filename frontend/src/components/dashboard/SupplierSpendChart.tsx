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

interface SupplierSpendChartProps {
  suppliers?: Array<{
    supplier_name: string;
    po_count: number;
    total_spend: number;
    payment_terms?: string;
  }>;
}

export const SupplierSpendChart: React.FC<SupplierSpendChartProps> = ({ suppliers = [] }) => {
  const chartData = suppliers.slice(0, 6).map((s) => ({
    name: s.supplier_name.length > 18 ? s.supplier_name.slice(0, 18) + '...' : s.supplier_name,
    fullName: s.supplier_name,
    spend: s.total_spend,
    poCount: s.po_count,
    city: (s as any).city || 'India',
  }));

  const formatCurrency = (val: number) => {
    if (val >= 10000000) return `₹${(val / 10000000).toFixed(2)}Cr`;
    if (val >= 100000) return `₹${(val / 100000).toFixed(1)}L`;
    return `₹${val.toLocaleString()}`;
  };

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-[#0B0F19] border border-slate-700/80 rounded-xl p-3.5 shadow-2xl text-xs space-y-1.5 min-w-[210px]">
          <p className="font-bold text-white border-b border-slate-800 pb-1">{data.fullName}</p>
          <div className="flex items-center justify-between text-slate-300">
            <span>Procurement Spend:</span>
            <span className="font-mono font-bold text-emerald-400">{formatCurrency(data.spend)}</span>
          </div>
          <div className="flex items-center justify-between text-slate-300">
            <span>Purchase Orders:</span>
            <span className="font-mono font-bold text-cyan-400">{data.poCount} POs</span>
          </div>
          <div className="flex items-center justify-between text-slate-400 pt-1 border-t border-slate-800/80 text-[11px]">
            <span>Vendor City:</span>
            <span className="font-mono text-slate-200">{data.city}</span>
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
          <h3 className="text-sm font-bold text-white">Vendor Procurement Volume</h3>
          <p className="text-xs text-slate-400">Total purchase order capital allocation to key suppliers</p>
        </div>
        <div className="flex items-center gap-1.5 text-xs">
          <span className="w-2.5 h-2.5 rounded bg-emerald-500"></span>
          <span className="text-slate-300">PO Spend</span>
        </div>
      </div>

      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            margin={{ top: 10, right: 15, left: -5, bottom: 25 }}
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
              tickFormatter={formatCurrency}
            />
            <Tooltip content={<CustomTooltip />} />
            <Bar
              dataKey="spend"
              name="PO Spend"
              fill="#10B981"
              radius={[4, 4, 0, 0]}
              maxBarSize={38}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
};
