import React from 'react';
import { Sparkles, ArrowRight } from 'lucide-react';
import { Card } from '../common/Card';
import { Badge } from '../common/Badge';
import type { KeyInsightItem } from '../../types/dashboard';

interface InsightCardProps {
  insights: KeyInsightItem[];
  onViewAll?: () => void;
}

export const InsightCard: React.FC<InsightCardProps> = ({ insights, onViewAll }) => {
  const getBadgeVariant = (cat: string) => {
    switch (cat) {
      case 'Finance': return 'rose';
      case 'Sales': return 'emerald';
      case 'Inventory': return 'amber';
      case 'HR': return 'blue';
      default: return 'purple';
    }
  };

  return (
    <Card className="flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-emerald-500/20 text-emerald-400">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white">Key Automated Insights</h3>
            <p className="text-xs text-slate-400">Autonomous multi-agent findings across FreshMart</p>
          </div>
        </div>
        {onViewAll && (
          <button
            onClick={onViewAll}
            className="text-xs text-emerald-400 hover:text-emerald-300 font-medium flex items-center gap-1 transition-colors"
          >
            <span>View All</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        )}
      </div>

      <div className="space-y-3">
        {insights.slice(0, 4).map((ins) => (
          <div
            key={ins.id}
            className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800/80 hover:border-slate-700/80 transition-all"
          >
            <div className="flex items-center justify-between gap-2 mb-1.5">
              <span className="font-semibold text-xs text-white leading-snug">{ins.title}</span>
              <Badge variant={getBadgeVariant(ins.category) as any} size="sm">
                {ins.category}
              </Badge>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed mb-2">{ins.description}</p>
            <div className="flex items-center justify-between text-[11px] text-slate-500 pt-2 border-t border-slate-800/50">
              <span className="font-mono text-[10px]">Sources: {ins.source}</span>
              <span>{ins.date}</span>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
};
