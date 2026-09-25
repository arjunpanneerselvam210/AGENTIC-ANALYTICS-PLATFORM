import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Lightbulb, Filter, ArrowRight, TrendingUp, AlertTriangle, Info, CheckCircle2, Sparkles, Loader2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { Badge } from '../components/common/Badge';
import { Card } from '../components/common/Card';
import { MOCK_INSIGHTS } from '../data/mockData';
import { getEnterpriseInsights } from '../services/analyticsApi';
import type { KeyInsightItem } from '../types/dashboard';

const ROLE_ALLOWED_INSIGHT_DOMAINS: Record<string, string[]> = {
  CEO: ['All', 'Sales', 'Inventory', 'Finance', 'HR', 'CRM', 'Operations'],
  ADMIN: ['All', 'Sales', 'Inventory', 'Finance', 'HR', 'CRM', 'Operations'],
  SALES_MANAGER: ['All', 'Sales', 'CRM', 'Inventory'],
  FINANCE_MANAGER: ['All', 'Finance', 'Sales', 'Operations'],
  HR_MANAGER: ['All', 'HR'],
  INVENTORY_MANAGER: ['All', 'Inventory', 'Operations'],
  ERP_MANAGER: ['All', 'Operations', 'Inventory', 'Sales'],
};

export const Insights: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const userRole = user?.role || 'CEO';
  const categories = ROLE_ALLOWED_INSIGHT_DOMAINS[userRole] || ['All', 'Sales'];

  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [insightsList, setInsightsList] = useState<KeyInsightItem[]>(MOCK_INSIGHTS as KeyInsightItem[]);
  const [loading, setLoading] = useState<boolean>(true);

  // If role changes or current selection is not permitted, fallback to 'All'
  useEffect(() => {
    if (!categories.includes(selectedCategory)) {
      setSelectedCategory('All');
    }
  }, [categories, selectedCategory]);

  useEffect(() => {
    let isMounted = true;
    getEnterpriseInsights()
      .then((res) => {
        if (!isMounted || !res || !res.insights) return;
        const mapped = res.insights.map((item: any, idx: number) => ({
          id: item.id || `INS-LIVE-${idx}`,
          title: item.title,
          description: item.summary,
          category: item.category.replace(' Insights', '').replace(' Alerts', '').replace(' Recommendations', ''),
          impact: item.impact.toLowerCase(),
          date: item.change || 'Real-time Telemetry',
          source: item.evidence,
          recommendation: item.recommendation
        }));
        if (mapped.length > 0) {
          setInsightsList(mapped);
        }
      })
      .catch((err) => {
        console.warn('Live insights fetch failed, falling back to cached baseline:', err);
      })
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, []);

  const filteredInsights = insightsList.filter((ins: KeyInsightItem) => {
    // 1. RBAC check: Manager can only see insights matching their allowed domains
    const isDomainAllowed = categories.some(
      (cat) => cat !== 'All' && ins.category.toLowerCase().includes(cat.toLowerCase())
    );
    if (!isDomainAllowed) return false;

    // 2. Active filter selection check
    return selectedCategory === 'All' || ins.category.toLowerCase().includes(selectedCategory.toLowerCase());
  });


  const getImpactBadge = (impact: string) => {
    switch (impact.toLowerCase()) {
      case 'high':
        return <Badge variant="danger">High Impact</Badge>;
      case 'medium':
        return <Badge variant="warning">Medium Impact</Badge>;
      default:
        return <Badge variant="info">Standard</Badge>;
    }
  };

  const getImpactIcon = (impact: string) => {
    switch (impact.toLowerCase()) {
      case 'high':
        return <AlertTriangle className="w-4 h-4 text-rose-400" />;
      case 'medium':
        return <TrendingUp className="w-4 h-4 text-amber-400" />;
      default:
        return <Info className="w-4 h-4 text-blue-400" />;
    }
  };

  const handleInvestigate = (insightTitle: string) => {
    navigate(`/analytics?q=${encodeURIComponent(`Investigate why: ${insightTitle}`)}`);
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/60 p-5 rounded-xl border border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
              <Lightbulb className="w-4 h-4" />
            </div>
            <h1 className="text-xl font-bold text-white tracking-tight">Agentic Business Insights</h1>
          </div>
          <p className="text-slate-400 text-sm mt-1">
            Autonomous multi-agent discoveries and operational anomaly alerts from FreshMart's unified data.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-xs text-emerald-400">
            {loading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <CheckCircle2 className="w-3.5 h-3.5" />}
            <span>{loading ? 'Refreshing Live Insights...' : 'Autonomous Agent Active'}</span>
          </div>
        </div>
      </div>

      {/* Category Filter Pills */}
      <div className="flex items-center gap-2 bg-slate-900/40 p-4 rounded-xl border border-slate-800 overflow-x-auto">
        <Filter className="w-4 h-4 text-slate-400 mr-2 shrink-0" />
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-medium transition-colors shrink-0 ${
              selectedCategory === cat
                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40'
                : 'bg-slate-800/60 text-slate-400 hover:text-slate-200 border border-slate-700/40'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Insights List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {filteredInsights.map((ins: KeyInsightItem) => (
          <Card key={ins.id} className="p-5 flex flex-col justify-between hover:border-slate-700 transition-colors">
            <div>
              <div className="flex items-center justify-between gap-3 mb-2">
                <div className="flex items-center gap-2">
                  {getImpactIcon(ins.impact)}
                  <span className="text-xs font-semibold text-slate-300 uppercase tracking-wider">
                    {ins.category} Domain
                  </span>
                </div>
                {getImpactBadge(ins.impact)}
              </div>

              <h3 className="text-base font-semibold text-white mt-1">
                {ins.title}
              </h3>
              <p className="text-xs text-slate-300 mt-2 leading-relaxed">
                {ins.description}
              </p>

              {(ins as any).recommendation && (
                <div className="mt-3 p-2.5 rounded-lg bg-blue-950/30 border border-blue-500/20 text-xs">
                  <div className="flex items-center gap-1.5 text-blue-300 font-semibold text-[11px] mb-1">
                    <Sparkles className="w-3 h-3 text-blue-400" />
                    <span>Actionable Recommendation</span>
                  </div>
                  <p className="text-slate-300 text-[11px]">
                    {(ins as any).recommendation}
                  </p>
                </div>
              )}
            </div>

            <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between">
              <span className="text-[11px] text-slate-500">
                Source: <strong className="text-slate-400">{ins.source}</strong>
              </span>

              <button
                onClick={() => handleInvestigate(ins.title)}
                className="flex items-center gap-1.5 text-xs text-emerald-400 hover:text-emerald-300 font-medium transition-colors"
              >
                <span>Ask Agent</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};
