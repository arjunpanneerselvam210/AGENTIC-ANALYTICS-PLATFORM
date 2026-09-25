import React from 'react';
import { Card } from '../common/Card';
import { AlertTriangle, PackageX } from 'lucide-react';
import { Badge } from '../common/Badge';

interface LowStockTableProps {
  items?: Array<{
    product_id: string;
    product_name: string;
    category: string;
    quantity_on_hand: number;
    reorder_level: number;
    deficit: number;
    unit_cost?: number;
  }>;
}

export const LowStockTable: React.FC<LowStockTableProps> = ({ items = [] }) => {
  return (
    <Card className="flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-amber-400" />
            <span>Critical Low-Stock Inventory Alerts</span>
          </h3>
          <p className="text-xs text-slate-400">Products currently below safety reorder threshold requiring replenishment</p>
        </div>
        <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/30">
          Action Required ({items.length} SKUs)
        </span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="border-b border-slate-800 text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
              <th className="pb-2.5">SKU / Product</th>
              <th className="pb-2.5">Category</th>
              <th className="pb-2.5 text-right">Stock On Hand</th>
              <th className="pb-2.5 text-right">Reorder Level</th>
              <th className="pb-2.5 text-right">Deficit</th>
              <th className="pb-2.5 text-center">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {items.map((item) => (
              <tr key={item.product_id} className="hover:bg-slate-800/30 transition-colors">
                <td className="py-2.5 font-medium text-slate-200">
                  <div>
                    <span className="font-semibold text-white block truncate max-w-[220px]">{item.product_name}</span>
                    <span className="text-[10px] text-slate-500 font-mono">{item.product_id}</span>
                  </div>
                </td>
                <td className="py-2.5 text-slate-400">{item.category}</td>
                <td className="py-2.5 text-right font-mono font-semibold text-rose-400">
                  {item.quantity_on_hand} units
                </td>
                <td className="py-2.5 text-right font-mono text-slate-400">
                  {item.reorder_level} units
                </td>
                <td className="py-2.5 text-right font-mono text-amber-400 font-bold">
                  -{item.deficit}
                </td>
                <td className="py-2.5 text-center">
                  <Badge variant="rose" size="sm">Urgent PO</Badge>
                </td>
              </tr>
            ))}
            {items.length === 0 && (
              <tr>
                <td colSpan={6} className="py-6 text-center text-slate-500">
                  <div className="flex flex-col items-center gap-1.5">
                    <PackageX className="w-6 h-6 text-slate-600" />
                    <span>All warehouse inventory balances are currently above safety thresholds.</span>
                  </div>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </Card>
  );
};
