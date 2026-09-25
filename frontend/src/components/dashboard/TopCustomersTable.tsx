import React from 'react';
import { Card } from '../common/Card';
import { Building2 } from 'lucide-react';

interface TopCustomersTableProps {
  customers?: Array<{
    company_name: string;
    orders: number;
    spend: number;
    city?: string;
    industry?: string;
  }>;
}

export const TopCustomersTable: React.FC<TopCustomersTableProps> = ({ customers = [] }) => {
  return (
    <Card className="flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Building2 className="w-4 h-4 text-emerald-400" />
            <span>Top B2B Commercial Clients</span>
          </h3>
          <p className="text-xs text-slate-400">High-volume wholesale accounts ranked by cumulative gross spend</p>
        </div>
        <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
          CRM & Orders
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="border-b border-slate-800 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
              <th className="pb-2.5">Company Name</th>
              <th className="pb-2.5">Industry</th>
              <th className="pb-2.5">Region</th>
              <th className="pb-2.5 text-right">Orders</th>
              <th className="pb-2.5 text-right">Total Spend</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {customers.map((c, idx) => (
              <tr key={c.company_name + idx} className="hover:bg-slate-800/30 transition-colors">
                <td className="py-2.5 font-medium text-slate-200">
                  <div className="flex items-center gap-2">
                    <span className="w-5 h-5 rounded bg-slate-800 flex items-center justify-center text-[10px] text-slate-400 font-mono">
                      #{idx + 1}
                    </span>
                    <span className="truncate max-w-[180px]">{c.company_name}</span>
                  </div>
                </td>
                <td className="py-2.5 text-slate-400">{c.industry || 'Wholesale'}</td>
                <td className="py-2.5 text-slate-400">{c.city || 'Regional'}</td>
                <td className="py-2.5 text-right font-mono text-slate-300">{c.orders}</td>
                <td className="py-2.5 text-right font-mono font-semibold text-emerald-400">
                  ₹{Number(c.spend).toLocaleString('en-IN', { maximumFractionDigits: 0 })}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
};
