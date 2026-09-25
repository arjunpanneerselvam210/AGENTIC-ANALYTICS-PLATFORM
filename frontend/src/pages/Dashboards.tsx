import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { PanelsTopLeft, Plus, ArrowRight, Layout, Clock, Search } from 'lucide-react';
import { Button } from '../components/common/Button';
import { Card } from '../components/common/Card';
import { MOCK_SAVED_DASHBOARDS } from '../data/mockData';
import type { SavedDashboardItem } from '../types/dashboard';

export const Dashboards: React.FC = () => {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');
  const [infoMessage, setInfoMessage] = useState<string | null>(null);

  const filteredDashboards = (MOCK_SAVED_DASHBOARDS as SavedDashboardItem[]).filter((d: SavedDashboardItem) =>
    d.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    d.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/60 p-5 rounded-xl border border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
              <PanelsTopLeft className="w-4 h-4" />
            </div>
            <h1 className="text-xl font-bold text-white tracking-tight">Saved Dashboards</h1>
          </div>
          <p className="text-slate-400 text-sm mt-1">
            Curated and customizable executive dashboards across FreshMart operational units.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {/* Search Bar */}
          <div className="relative w-48 sm:w-60">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search dashboards..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full bg-slate-800/80 border border-slate-700/60 rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-emerald-500"
            />
          </div>

          <Button
            variant="primary"
            size="sm"
            onClick={() => {
              setInfoMessage('Dashboard builder modal is available in enterprise expansion mode.');
              setTimeout(() => setInfoMessage(null), 3000);
            }}
            className="flex items-center gap-1.5 shrink-0"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Create Dashboard</span>
          </Button>
        </div>
      </div>

      {infoMessage && (
        <div className="p-3 bg-blue-500/10 border border-blue-500/30 text-blue-300 text-xs rounded-lg animate-fade-in">
          {infoMessage}
        </div>
      )}

      {/* Grid of Dashboard Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredDashboards.map((dash: SavedDashboardItem) => (
          <Card
            key={dash.id}
            className="p-5 flex flex-col justify-between hover:border-slate-700 hover:shadow-xl transition-all group"
          >
            <div>
              <div className="flex items-start justify-between gap-3 mb-3">
                <div className="w-9 h-9 rounded-lg bg-slate-800/80 border border-slate-700/60 flex items-center justify-center text-emerald-400 group-hover:border-emerald-500/40 transition-colors">
                  <Layout className="w-4 h-4" />
                </div>
                <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700/40">
                  {dash.widgetsCount || 4} widgets
                </span>
              </div>

              <h3 className="text-base font-semibold text-white group-hover:text-emerald-300 transition-colors">
                {dash.title}
              </h3>
              <p className="text-xs text-slate-400 mt-2 line-clamp-2 leading-relaxed">
                {dash.description}
              </p>
            </div>

            <div className="mt-5 pt-4 border-t border-slate-800/80 flex items-center justify-between">
              <span className="flex items-center gap-1 text-[11px] text-slate-500">
                <Clock className="w-3 h-3" />
                <span>{dash.lastUpdated || dash.updatedAt}</span>
              </span>

              <button
                onClick={() => navigate('/dashboard')}
                className="flex items-center gap-1 text-xs font-medium text-emerald-400 hover:text-emerald-300 transition-colors"
              >
                <span>Launch</span>
                <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
              </button>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};
