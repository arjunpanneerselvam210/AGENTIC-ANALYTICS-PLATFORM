import React, { useState, useEffect } from 'react';
import { Database, Plus, CheckCircle2, Server, ShieldCheck, HardDrive, RefreshCw, Cpu, Activity } from 'lucide-react';
import { Button } from '../components/common/Button';
import { Badge } from '../components/common/Badge';
import { Card } from '../components/common/Card';
import { AddDataSourceModal } from '../components/layout/AddDataSourceModal';
import { apiClient } from '../services/api';
import { formatISTTime } from '../utils/dateUtils';
import type { DataSourceItem } from '../types/dashboard';

export const DataSources: React.FC = () => {
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isSyncing, setIsSyncing] = useState(false);
  const [lastCheckTime, setLastCheckTime] = useState<string>(formatISTTime(new Date(), true));
  const [dataSources, setDataSources] = useState<DataSourceItem[]>([
    {
      id: 'DS-01',
      name: 'FreshMart MySQL 8.0 Enterprise Database',
      type: 'mysql',
      status: 'connected',
      tablesCount: 16,
      lastSync: `${formatISTTime(new Date())} IST (localhost:3306)`,
      description: 'Primary transactional datastore housing sales_orders, products, inventory, customers, employees, and financials.'
    },
    {
      id: 'DS-02',
      name: 'PostgreSQL 16 Security & RBAC Datastore',
      type: 'postgresql',
      status: 'connected',
      tablesCount: 5,
      lastSync: `${formatISTTime(new Date())} IST (localhost:5432)`,
      description: 'Dedicated security datastore managing users, bcrypt password credentials, RBAC roles, and granular permissions.'
    },
    {
      id: 'DS-03',
      name: 'Ollama Local LLM Agent & SQL Engine',
      type: 'ai_engine',
      status: 'connected',
      tablesCount: 2,
      lastSync: `${formatISTTime(new Date())} IST (localhost:11434)`,
      description: 'Local dual-model inference server executing Llama 3.1 8B (agent reasoning) and Qwen 2.5-Coder 7B (SQL generation).'
    },
    {
      id: 'DS-04',
      name: 'FreshMart ERP & Procurement Domain',
      type: 'domain',
      status: 'connected',
      tablesCount: 5,
      lastSync: 'Real-time (MCP)',
      description: 'Unified operational schema: suppliers, purchase_orders, purchase_order_items, products, and inventory balances.'
    },
    {
      id: 'DS-05',
      name: 'FreshMart HRMS & Workforce Compensation',
      type: 'domain',
      status: 'connected',
      tablesCount: 3,
      lastSync: 'Real-time (MCP)',
      description: 'Workforce operational schema: departments, active employees, and employee base compensation salaries.'
    },
    {
      id: 'DS-06',
      name: 'FreshMart Commercial Sales & CRM Domain',
      type: 'domain',
      status: 'connected',
      tablesCount: 4,
      lastSync: 'Real-time (MCP)',
      description: 'Commercial schema: B2B customers, inbound commercial leads, retail sales orders, and order item line items.'
    },
  ]);

  const fetchHealthTelemetry = async () => {
    setIsSyncing(true);
    try {
      const res = await apiClient.get('/health');
      const healthData = res.data;
      const nowIST = formatISTTime(new Date(), true);
      setLastCheckTime(nowIST);

      const services = healthData?.services || {};
      const mysqlOnline = services.mysql?.status === 'online';
      const pgOnline = services.postgresql?.status === 'online';
      const ollamaOnline = services.ollama?.status === 'online';

      setDataSources((prev) =>
        prev.map((item) => {
          if (item.type === 'mysql') {
            return {
              ...item,
              status: mysqlOnline ? 'connected' : 'degraded',
              lastSync: `${nowIST} IST (${services.mysql?.host || 'localhost:3306'})`,
              description: `Primary MySQL server (${services.mysql?.version || '8.0.36'}) queried via Model Context Protocol (MCP) read-only pooling.`
            };
          }
          if (item.type === 'postgresql') {
            return {
              ...item,
              status: pgOnline ? 'connected' : 'degraded',
              lastSync: `${nowIST} IST (${services.postgresql?.host || 'localhost:5432'})`,
              description: `Security PostgreSQL server (${services.postgresql?.version || 'PostgreSQL 16'}) enforcing RBAC authentication boundaries.`
            };
          }
          if (item.type === 'ai_engine') {
            return {
              ...item,
              status: ollamaOnline ? 'connected' : 'degraded',
              lastSync: `${nowIST} IST (${services.ollama?.url || 'localhost:11434'})`,
              description: `Ollama inference engine (${services.ollama?.available_models?.length || 2} models active: llama3.1:8b & qwen2.5-coder:7b).`
            };
          }
          return {
            ...item,
            lastSync: `${nowIST} IST (Real-time MCP)`
          };
        })
      );
    } catch (err) {
      console.warn('Live health check ping failed:', err);
    } finally {
      setIsSyncing(false);
    }
  };

  useEffect(() => {
    fetchHealthTelemetry();
  }, []);

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
            onClick={fetchHealthTelemetry}
            className="flex items-center gap-1.5"
            disabled={isSyncing}
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isSyncing ? 'animate-spin' : ''}`} />
            <span>{isSyncing ? 'Inspecting...' : 'Live Health Check'}</span>
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

      {/* Telemetry Status Ribbon */}
      <div className="p-4 bg-slate-900/40 border border-slate-800 rounded-xl flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <Server className="w-5 h-5 text-emerald-400 shrink-0" />
          <div className="text-xs text-slate-300 leading-relaxed">
            <strong className="text-white">Active Architecture:</strong> Business datastore in <strong>MySQL 8.0</strong>, authentication in <strong>PostgreSQL 16</strong>, and LLM reasoning via local <strong>Ollama</strong>.
          </div>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <Activity className="w-4 h-4 text-emerald-400 animate-pulse" />
          <span className="text-[11px] font-mono text-slate-400">Last Telemetry: <span className="text-emerald-400 font-semibold">{lastCheckTime} IST</span></span>
        </div>
      </div>

      {/* Data Sources Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {dataSources.map((source) => (
          <Card key={source.id} className="p-5 flex flex-col justify-between hover:border-slate-700 transition-colors">
            <div>
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2.5">
                  <div className="w-9 h-9 rounded-lg bg-slate-800 border border-slate-700/60 flex items-center justify-center text-emerald-400">
                    {source.type === 'postgresql' ? (
                      <ShieldCheck className="w-5 h-5 text-indigo-400" />
                    ) : source.type === 'mysql' ? (
                      <Database className="w-5 h-5 text-blue-400" />
                    ) : source.type === 'ai_engine' ? (
                      <Cpu className="w-5 h-5 text-amber-400" />
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
                  <span className={`w-1.5 h-1.5 rounded-full mr-1.5 ${source.status === 'connected' ? 'bg-emerald-400 animate-pulse' : 'bg-amber-400'}`} />
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
                  <span className="text-slate-200 font-medium font-mono text-[11px]">{source.lastSync}</span>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between pt-3 border-t border-slate-800/80 text-[11px] text-slate-400">
              <span className="flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                <span>Live Telemetry Active</span>
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
