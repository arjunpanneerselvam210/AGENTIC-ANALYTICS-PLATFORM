import React, { useState } from 'react';
import { X, CheckCircle, Database, ShoppingBag, Users, Layers, Server } from 'lucide-react';
import { Button } from '../common/Button';

interface AddDataSourceModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const AddDataSourceModal: React.FC<AddDataSourceModalProps> = ({ isOpen, onClose }) => {
  const [selectedSource, setSelectedSource] = useState<string | null>(null);
  const [isConnecting, setIsConnecting] = useState(false);
  const [connectedSuccessfully, setConnectedSuccessfully] = useState(false);

  if (!isOpen) return null;

  const sources = [
    { id: 'erp', name: 'FreshMart ERP Connector', icon: Layers, desc: 'Suppliers, Purchase Orders, Warehouses & Stock' },
    { id: 'crm', name: 'FreshMart CRM & B2B Leads', icon: Users, desc: 'Enterprise customers, leads, pipeline and call interactions' },
    { id: 'hrms', name: 'FreshMart HRMS Directory', icon: Users, desc: 'Workforce records, employee profiles, department budgets' },
    { id: 'ecom', name: 'FreshMart E-Commerce Store', icon: ShoppingBag, desc: 'Real-time retail orders, checkout transactions & line items' },
    { id: 'mysql', name: 'External MySQL Database', icon: Server, desc: 'Custom analytical replica (read-only query pipeline)' },
    { id: 'postgres', name: 'PostgreSQL Relational DB', icon: Database, desc: 'Enterprise auth, security logs & application metadata' },
  ];

  const handleConnect = () => {
    if (!selectedSource) return;
    setIsConnecting(true);
    setTimeout(() => {
      setIsConnecting(false);
      setConnectedSuccessfully(true);
      setTimeout(() => {
        setConnectedSuccessfully(false);
        onClose();
      }, 1200);
    }, 1000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fadeIn">
      <div className="bg-[#0F1626] border border-slate-800 rounded-2xl w-full max-w-lg shadow-2xl p-6 relative">
        <button
          onClick={onClose}
          className="absolute top-5 right-5 text-slate-400 hover:text-white transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        <h3 className="text-base font-bold text-white mb-1">Add Enterprise Data Source</h3>
        <p className="text-xs text-slate-400 mb-5">
          Connect your business domain or database replica to the Model Context Protocol (MCP) data bridge.
        </p>

        {connectedSuccessfully ? (
          <div className="py-8 flex flex-col items-center justify-center text-center">
            <CheckCircle className="w-12 h-12 text-emerald-400 mb-3 animate-bounce" />
            <p className="text-sm font-semibold text-white">Data Source Connected Successfully!</p>
            <p className="text-xs text-slate-400 mt-1">Schema introspected and registered into MCP server catalog.</p>
          </div>
        ) : (
          <>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-6">
              {sources.map((src) => {
                const Icon = src.icon;
                const isSelected = selectedSource === src.id;
                return (
                  <button
                    key={src.id}
                    onClick={() => setSelectedSource(src.id)}
                    className={`p-3.5 rounded-xl border text-left transition-all ${
                      isSelected
                        ? 'border-emerald-500 bg-emerald-500/10 text-white shadow-md shadow-emerald-950/20'
                        : 'border-slate-800/80 bg-slate-900/60 hover:border-slate-700 text-slate-300'
                    }`}
                  >
                    <div className="flex items-center gap-2.5 mb-1.5">
                      <div className={`p-1.5 rounded-lg ${isSelected ? 'bg-emerald-500 text-white' : 'bg-slate-800 text-slate-400'}`}>
                        <Icon className="w-4 h-4" />
                      </div>
                      <span className="font-semibold text-xs text-white">{src.name}</span>
                    </div>
                    <p className="text-[11px] text-slate-400 leading-tight">{src.desc}</p>
                  </button>
                );
              })}
            </div>

            <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800/80">
              <Button variant="ghost" size="sm" onClick={onClose}>
                Cancel
              </Button>
              <Button
                variant="primary"
                size="sm"
                disabled={!selectedSource}
                isLoading={isConnecting}
                onClick={handleConnect}
              >
                Connect to MCP Pipeline
              </Button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};
