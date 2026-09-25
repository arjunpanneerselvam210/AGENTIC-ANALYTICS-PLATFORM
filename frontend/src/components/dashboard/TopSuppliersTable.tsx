import React from 'react';
import { Card } from '../common/Card';
import { Truck } from 'lucide-react';

interface TopSuppliersTableProps {
  suppliers?: Array<{
    supplier_name: string;
    po_count: number;
    total_spend: number;
    payment_terms?: string;
  }>;
}

export const TopSuppliersTable: React.FC<TopSuppliersTableProps> = ({ suppliers = [] }) => {
  return (
    <Card className="flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Truck className="w-4 h-4 text-emerald-400" />
            <span>Primary Strategic Suppliers</span>
          </h3>
          <p className="text-xs text-slate-400">Certified vendors ranked by total procurement purchase volume</p>
        </div>
        <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
          SCM Partners
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="border-b border-slate-800 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
              <th className="pb-2.5">Supplier Name</th>
              <th className="pb-2.5 text-right">POs Issued</th>
              <th className="pb-2.5 text-right">Payment Terms</th>
              <th className="pb-2.5 text-right">Total Procurement</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {suppliers.map((s, idx) => (
              <tr key={s.supplier_name + idx} className="hover:bg-slate-800/30 transition-colors">
                <td className="py-2.5 font-medium text-slate-200">
                  <div className="flex items-center gap-2">
                    <span className="w-5 h-5 rounded bg-slate-800 flex items-center justify-center text-[10px] text-slate-400 font-mono">
                      #{idx + 1}
                    </span>
                    <span className="truncate max-w-[200px] text-white font-semibold">{s.supplier_name}</span>
                  </div>
                </td>
                <td className="py-2.5 text-right font-mono text-slate-300">
                  {s.po_count} orders
                </td>
                <td className="py-2.5 text-right font-mono text-slate-400">
                  {s.payment_terms || 'Net 30'}
                </td>
                <td className="py-2.5 text-right font-mono text-emerald-400 font-semibold">
                  ₹{Number(s.total_spend).toLocaleString('en-IN', { maximumFractionDigits: 0 })}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
};
