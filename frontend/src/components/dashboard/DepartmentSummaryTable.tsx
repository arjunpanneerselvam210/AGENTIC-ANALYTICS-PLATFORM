import React from 'react';
import { Card } from '../common/Card';
import { Users2, ShieldAlert } from 'lucide-react';

interface DepartmentSummaryTableProps {
  departments?: Array<{
    department: string;
    headcount: number;
    avg_salary: number;
    total_payroll: number;
  }>;
}

export const DepartmentSummaryTable: React.FC<DepartmentSummaryTableProps> = ({ departments = [] }) => {
  return (
    <Card className="flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Users2 className="w-4 h-4 text-emerald-400" />
            <span>Operational Department Headcount & Payroll</span>
          </h3>
          <p className="text-xs text-slate-400">Authorized workforce directory with departmental compensation metrics</p>
        </div>
        <div className="flex items-center gap-1.5 px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-[11px] font-mono">
          <ShieldAlert className="w-3 h-3" />
          <span>VIEW_EMPLOYEE_SALARY Authorized</span>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="border-b border-slate-800 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
              <th className="pb-2.5">Department</th>
              <th className="pb-2.5 text-right">Headcount</th>
              <th className="pb-2.5 text-right">Share of Workforce</th>
              <th className="pb-2.5 text-right">Average Base Salary</th>
              <th className="pb-2.5 text-right">Monthly Payroll</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {departments.map((d) => {
              const totalWorkforce = 500;
              const pct = ((d.headcount / totalWorkforce) * 100).toFixed(1);
              return (
                <tr key={d.department} className="hover:bg-slate-800/30 transition-colors">
                  <td className="py-2.5 font-medium text-slate-200">
                    <span className="font-semibold text-white">{d.department}</span>
                  </td>
                  <td className="py-2.5 text-right font-mono text-slate-300">
                    {d.headcount} emps
                  </td>
                  <td className="py-2.5 text-right font-mono text-slate-400">
                    {pct}%
                  </td>
                  <td className="py-2.5 text-right font-mono text-emerald-400 font-semibold">
                    ₹{Number(d.avg_salary).toLocaleString('en-IN', { maximumFractionDigits: 0 })}
                  </td>
                  <td className="py-2.5 text-right font-mono text-slate-200 font-semibold">
                    ₹{Number(d.total_payroll).toLocaleString('en-IN', { maximumFractionDigits: 0 })}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </Card>
  );
};
