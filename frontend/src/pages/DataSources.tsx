import React, { useState } from 'react';
import { Database, Plus, CheckCircle2, Server, ShieldCheck, HardDrive, RefreshCw } from 'lucide-react';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { Card } from '../components/common/Card';
import { AddDataSourceModal } from '../components/layout/AddDataSourceModal';
import { MOCK_DATA_SOURCES } from '../data/mockData';
import type { DataSourceItem } from '../types/dashboard';

export const DataSources: React.FC = () => {
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);

  const handleSyncAll = () => {
    setIsSyncing(true);
    setTimeout(() => setIsSyncing(false), 800);
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/60 p-5 rounded-xl border border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
              <Database className="w-4 h-4" />
            </div>
            <h1 className="text-xl font-bold text-white tracking-tight">Data Sources & Connected Systems</h1>
          </div>
          <p className="text-slate-400 text-sm mt-1">
            Enterprise application domains and physical databases integrated into the MCP agentic pipeline.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleSyncAll}
            className="flex items-center gap-1.5"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isSyncing ? 'animate-spin' : ''}`} />
            <span>Health Check</span>
          </Button>
          <Button
            variant="primary"
            size="sm"
            onClick={() => setIsAddModalOpen(true)}
            className="flex items-center gap-1.5"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Add Data Source</span>
          </Button>
        </div>
      </div>

      {/* Architecture Disclaimer / Context Callout */}
      <div className="p-4 bg-slate-900/40 border border-slate-800 rounded-xl flex items-start gap-3">
        <Server className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
        <div className="text-xs text-slate-300 leading-relaxed">
          <strong className="text-white">Architecture Overview:</strong> In FreshMart's enterprise architecture,
          business application domains (ERP, CRM, HRMS, E-Commerce) reside within the consolidated <strong>FreshMart MySQL</strong> database,
          while authentication, user roles, and security policies are stored in <strong>PostgreSQL</strong>.
          The LangGraph multi-agent pipeline interfaces securely with these domains via Model Context Protocol (MCP).
        </div>
      </div>

      {/* Data Sources Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {(MOCK_DATA_SOURCES as DataSourceItem[]).map((source: DataSourceItem) => (
          <Card key={source.id} className="p-5 flex flex-col justify-between hover:border-slate-700 transition-colors">
            <div>
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2.5">
                  <div className="w-9 h-9 rounded-lg bg-slate-800 border border-slate-700/60 flex items-center justify-center text-emerald-400">
                    {source.type === 'postgresql' ? (
                      <ShieldCheck className="w-5 h-5 text-indigo-400" />
                    ) : source.type === 'mysql' ? (
                      <Database className="w-5 h-5 text-blue-400" />
                    ) : (
                      <HardDrive className="w-5 h-5 text-emerald-400" />
                    )}
                  </div>
                  <div>
                    <h3 className="text-sm font-semibold text-white">{source.name}</h3>
                    <p className="text-[11px] text-slate-400 uppercase tracking-wider">{source.type}</p>
                  </div>
                </div>

                <Badge variant={source.status === 'connected' ? 'success' : 'warning'}>
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mr-1.5 animate-pulse" />
                  {source.status === 'connected' ? 'Connected' : 'Degraded'}
                </Badge>
              </div>

              <p className="text-xs text-slate-300 mt-2 mb-4 leading-relaxed">
                {source.description}
              </p>

              <div className="grid grid-cols-2 gap-2 text-xs bg-slate-900/60 p-3 rounded-lg border border-slate-800/80 mb-4">
                <div>
                  <span className="text-slate-500 text-[10px] block">Tables / Entities</span>
                  <span className="text-slate-200 font-semibold">{source.tablesCount} schema objects</span>
                </div>
                <div>
                  <span className="text-slate-500 text-[10px] block">Last Schema Sync</span>
                  <span className="text-slate-200 font-medium">{source.lastSync}</span>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between pt-3 border-t border-slate-800/80 text-[11px] text-slate-400">
              <span className="flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                <span>MCP Tool Active</span>
              </span>
              <button
                onClick={() => setIsAddModalOpen(true)}
                className="text-emerald-400 hover:text-emerald-300 font-medium hover:underline"
              >
                Configure
              </button>
            </div>
          </Card>
        ))}
      </div>

      <AddDataSourceModal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
      />
    </div>
  );
};
