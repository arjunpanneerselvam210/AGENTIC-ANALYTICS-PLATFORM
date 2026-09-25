import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';
import { Card } from '../common/Card';
import type { KPICardData } from '../../types/dashboard';

interface KPICardProps {
  title?: string;
  value?: string;
  change?: string;
  isPositive?: boolean;
  periodText?: string;
  kpi?: KPICardData;
}

export const KPICard: React.FC<KPICardProps> = ({
  title,
  value,
  change,
  isPositive,
  periodText,
  kpi,
}) => {
  const displayTitle = title || kpi?.title || '';
  const displayValue = value || kpi?.value || '';
  const displayChange = change || kpi?.change || '';
  const displayPositive = isPositive !== undefined ? isPositive : (kpi?.isPositive ?? true);
  const displayPeriod = periodText || kpi?.periodText || 'vs previous period';

  return (
    <Card className="flex flex-col justify-between hover:border-slate-700/80 transition-all p-5">
      <div>
        <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">{displayTitle}</span>
        <div className="text-2xl sm:text-3xl font-bold text-white mt-1.5 tracking-tight font-mono">
          {displayValue}
        </div>
      </div>

      <div className="flex items-center justify-between mt-4 pt-3 border-t border-slate-800/60">
        <div className={`flex items-center gap-1 text-xs font-semibold ${displayPositive ? 'text-emerald-400' : 'text-rose-400'}`}>
          {displayPositive ? <TrendingUp className="w-3.5 h-3.5" /> : <TrendingDown className="w-3.5 h-3.5" />}
          <span>{displayChange}</span>
        </div>
        <span className="text-[11px] text-slate-500 font-medium">{displayPeriod}</span>
      </div>
    </Card>
  );
};
