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


interface DepartmentSalaryChartProps {
  departments?: Array<{
    department?: string;
    dept_name?: string;
    headcount?: number;
    avg_salary?: number;
    total_payroll?: number;
  }>;
}

export const DepartmentSalaryChart: React.FC<DepartmentSalaryChartProps> = ({ departments = [] }) => {
  const chartData = departments.map((d) => ({
    name: d.department || d.dept_name || 'Dept',
    avgSalary: Number(d.avg_salary || 0),
    totalPayroll: Number(d.total_payroll || 0),
    headcount: Number(d.headcount || 0),
  }));

  const formatCurrency = (val: number) => {
    if (val >= 10000000) return `₹${(val / 10000000).toFixed(2)}Cr`;
    if (val >= 100000) return `₹${(val / 100000).toFixed(1)}L`;
    if (val >= 1000) return `₹${(val / 1000).toFixed(0)}k`;
    return `₹${val.toLocaleString()}`;
  };

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-[#0B0F19] border border-slate-700/80 rounded-xl p-3.5 shadow-2xl text-xs space-y-1.5 min-w-[200px]">
          <p className="font-bold text-white border-b border-slate-800 pb-1.5">{data.name}</p>
          <div className="flex items-center justify-between text-slate-300">
            <span>Average Base Salary:</span>
            <span className="font-mono font-bold text-emerald-400">{formatCurrency(data.avgSalary)}/mo</span>
          </div>
          <div className="flex items-center justify-between text-slate-300">
            <span>Total Monthly Payroll:</span>
            <span className="font-mono font-bold text-cyan-400">{formatCurrency(data.totalPayroll)}</span>
          </div>
          <div className="flex items-center justify-between text-slate-400 pt-1 border-t border-slate-800/80 text-[11px]">
            <span>Active Headcount:</span>
            <span className="font-mono text-slate-200">{data.headcount} employees</span>
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
            <h3 className="text-sm font-bold text-white">Department Average Compensation Benchmark</h3>
            <span className="text-[10px] font-bold text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded-full">
              Monthly Base
            </span>
          </div>
          <p className="text-xs text-slate-400">Mean base salary across operational workforce divisions</p>
        </div>
        <div className="flex items-center gap-1.5 text-xs text-slate-300">
          <span className="w-2.5 h-2.5 rounded bg-emerald-500"></span>
          <span>Avg Salary</span>
        </div>
      </div>

      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            margin={{ top: 10, right: 15, left: 10, bottom: 25 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" vertical={false} />
            <XAxis
              dataKey="name"
              stroke="#64748B"
              fontSize={11}
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
            <Bar dataKey="avgSalary" fill="#10B981" radius={[4, 4, 0, 0]} maxBarSize={32} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </Card>
  );
};
