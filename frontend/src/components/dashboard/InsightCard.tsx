import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, ArrowRight, MessageSquare } from 'lucide-react';
import { Card } from '../common/Card';
import { Badge } from '../common/Badge';
import type { KeyInsightItem } from '../../types/dashboard';

interface InsightCardProps {
  insights: KeyInsightItem[];
  onViewAll?: () => void;
  onAskAI?: (question: string) => void;
}

export const InsightCard: React.FC<InsightCardProps> = ({ insights, onViewAll, onAskAI }) => {
  const navigate = useNavigate();

  const getBadgeVariant = (cat: string) => {
    switch (cat) {
      case 'Finance': return 'rose';
      case 'Sales': return 'emerald';
      case 'Inventory': return 'amber';
      case 'HR': return 'blue';
      default: return 'purple';
    }
  };

  const handleInvestigate = (insight: KeyInsightItem) => {
    const q = insight.title;
    if (onAskAI) {
      onAskAI(q);
    } else {
      navigate(`/analytics?q=${encodeURIComponent(q)}`);
    }
  };

  return (
    <Card className="flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-xl bg-emerald-500/20 text-emerald-400">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white">Grounded Operational Observations</h3>
            <p className="text-xs text-slate-400">Autonomous multi-agent findings strictly anchored in FreshMart ledger data</p>
          </div>
        </div>
        {onViewAll && (
          <button
            onClick={onViewAll}
            className="text-xs text-emerald-400 hover:text-emerald-300 font-medium flex items-center gap-1 transition-colors cursor-pointer"
          >
            <span>View All</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {insights.slice(0, 4).map((ins) => (
          <div
            key={ins.id}
            className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800/80 hover:border-slate-700/80 transition-all flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between gap-2 mb-1.5">
                <span className="font-semibold text-xs text-white leading-snug">{ins.title}</span>
                <Badge variant={getBadgeVariant(ins.category) as any} size="sm">
                  {ins.category}
                </Badge>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed mb-3">{ins.description}</p>
            </div>
            <div className="flex items-center justify-between text-[11px] text-slate-500 pt-2 border-t border-slate-800/50">
              <span className="font-mono text-[10px]">Source: {ins.source}</span>
              <button
                type="button"
                onClick={() => handleInvestigate(ins)}
                className="text-[11px] text-emerald-400 hover:text-emerald-300 font-semibold flex items-center gap-1 transition-colors cursor-pointer"
              >
                <MessageSquare className="w-3 h-3" />
                <span>Ask AI</span>
              </button>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
};
