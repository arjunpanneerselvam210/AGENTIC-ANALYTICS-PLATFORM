import React from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';
import { Card } from '../common/Card';

interface DepartmentHeadcountChartProps {
  departments?: Array<{
    department: string;
    headcount: number;
    avg_salary: number;
    total_payroll: number;
  }>;
}

export const DepartmentHeadcountChart: React.FC<DepartmentHeadcountChartProps> = ({
  departments = [],
}) => {
  const formatSalary = (val: number) => {
    if (val >= 100000) return `₹${(val / 100000).toFixed(1)}L`;
    if (val >= 1000) return `₹${(val / 1000).toFixed(0)}k`;
    return `₹${val}`;
  };

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-[#0B0F19] border border-slate-700/80 rounded-xl p-3.5 shadow-2xl text-xs space-y-1.5 min-w-[200px]">
          <p className="font-bold text-white border-b border-slate-800 pb-1 text-sm">{label}</p>
          <div className="flex items-center justify-between text-slate-300">
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
              <span>Active Headcount:</span>
            </span>
            <span className="font-mono font-bold text-emerald-400">{data.headcount} employees</span>
          </div>
          <div className="flex items-center justify-between text-slate-300">
            <span className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-cyan-400"></span>
              <span>Avg Base Salary:</span>
            </span>
            <span className="font-mono font-bold text-cyan-400">₹{Number(data.avg_salary).toLocaleString()}/mo</span>
          </div>
          <div className="flex items-center justify-between text-slate-400 pt-1 border-t border-slate-800/80 text-[11px]">
            <span>Total Monthly Payroll:</span>
            <span className="font-mono text-slate-200 font-semibold">₹{(data.total_payroll / 100000).toFixed(2)}L</span>
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
          <h3 className="text-sm font-bold text-white">Workforce Distribution & Compensation</h3>
          <p className="text-xs text-slate-400">Headcount allocation and average monthly salary across operating divisions</p>
        </div>
        <div className="flex items-center gap-4 text-xs font-medium">
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded bg-emerald-500"></span>
            <span className="text-slate-300">Headcount</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-cyan-400"></span>
            <span className="text-slate-300">Avg Salary</span>
          </div>
        </div>
      </div>

      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart
            data={departments}
            margin={{ top: 10, right: 20, left: -10, bottom: 25 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" vertical={false} />
            <XAxis
              dataKey="department"
              stroke="#64748B"
              fontSize={10}
              tickLine={false}
              axisLine={false}
              angle={-20}
              textAnchor="end"
              interval={0}
            />
            {/* Left Axis: Headcount */}
            <YAxis
              yAxisId="left"
              stroke="#64748B"
              fontSize={11}
              tickLine={false}
              axisLine={false}
            />
            {/* Right Axis: Salary */}
            <YAxis
              yAxisId="right"
              orientation="right"
              stroke="#64748B"
              fontSize={10}
              tickLine={false}
              axisLine={false}
              tickFormatter={formatSalary}
            />
            <Tooltip content={<CustomTooltip />} />
            <Bar
              yAxisId="left"
              dataKey="headcount"
              name="Headcount"
              fill="#10B981"
              radius={[4, 4, 0, 0]}
              maxBarSize={42}
            />
            <Line
              yAxisId="right"
              type="monotone"
              dataKey="avg_salary"
              name="Avg Salary"
              stroke="#06B6D4"
              strokeWidth={2.5}
              dot={{ r: 3, fill: '#06B6D4' }}
              activeDot={{ r: 5 }}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
};
