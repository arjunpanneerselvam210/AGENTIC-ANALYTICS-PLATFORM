import React from 'react';
import { Card } from '../common/Card';
import { Badge } from '../common/Badge';
import type { TopProductItem } from '../../types/dashboard';

interface TopProductsTableProps {
  products: TopProductItem[];
}

export const TopProductsTable: React.FC<TopProductsTableProps> = ({ products }) => {
  return (
    <Card className="flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-bold text-white">Top Products by Revenue</h3>
          <p className="text-xs text-slate-400">Highest grossing SKUs and inventory stock levels</p>
        </div>
        <Badge variant="emerald" size="sm">Live Catalog</Badge>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className="border-b border-slate-800 text-slate-400 font-semibold uppercase tracking-wider text-[10px]">
              <th className="py-2.5 px-3">Product</th>
              <th className="py-2.5 px-3">Category</th>
              <th className="py-2.5 px-3 text-right">Revenue</th>
              <th className="py-2.5 px-3 text-right">Orders</th>
              <th className="py-2.5 px-3 text-right">Stock</th>
              <th className="py-2.5 px-3 text-right">Growth</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {products.map((prod) => (
              <tr key={prod.id} className="hover:bg-slate-800/30 transition-colors">
                <td className="py-3 px-3">
                  <span className="font-medium text-slate-200 block">{prod.name}</span>
                  <span className="text-[10px] text-slate-500 font-mono">ID: {prod.id}</span>
                </td>
                <td className="py-3 px-3">
                  <Badge variant="slate" size="sm">{prod.category}</Badge>
                </td>
                <td className="py-3 px-3 text-right font-mono font-semibold text-slate-100">
                  ₹{prod.revenue.toLocaleString()}
                </td>
                <td className="py-3 px-3 text-right font-mono text-slate-300">
                  {prod.orders.toLocaleString()}
                </td>
                <td className="py-3 px-3 text-right">
                  <span className={`font-mono text-xs font-semibold ${prod.stock <= 20 ? 'text-amber-400' : 'text-slate-300'}`}>
                    {prod.stock} units
                  </span>
                </td>
                <td className="py-3 px-3 text-right">
                  <span className="text-emerald-400 font-semibold font-mono text-xs">
                    {prod.growth}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
};
