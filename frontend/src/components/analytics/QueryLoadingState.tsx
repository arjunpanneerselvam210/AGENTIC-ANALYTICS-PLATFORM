import React from 'react';
import { Card } from '../common/Card';

interface QueryLoadingStateProps {
  question?: string;
}

export const QueryLoadingState: React.FC<QueryLoadingStateProps> = ({ question = 'FreshMart Business Analytics Query' }) => {
  return (
    <Card className="animate-pulse border-emerald-500/30 bg-[#0B101D] p-5">
      <div className="flex items-start gap-4">
        <div className="w-9 h-9 rounded-xl bg-emerald-600/20 border border-emerald-500/40 flex items-center justify-center flex-shrink-0 mt-0.5">
          <div className="w-4 h-4 border-2 border-emerald-400 border-t-transparent rounded-full animate-spin"></div>
        </div>

        <div className="flex-1 space-y-3">
          <div>
            <span className="text-[10px] uppercase font-bold tracking-wider text-emerald-400 font-mono">Agentic Pipeline Active</span>
            <h4 className="text-sm font-semibold text-white mt-0.5">Analyzing FreshMart Data...</h4>
            <p className="text-xs text-slate-400 italic">"{question}"</p>
          </div>

          <div className="space-y-1.5 pt-2">
            <div className="flex items-center gap-2 text-xs text-slate-300">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
              <span>Introspecting schema via Model Context Protocol (MCP)...</span>
            </div>
            <div className="flex items-center gap-2 text-xs text-slate-400">
              <span className="w-1.5 h-1.5 rounded-full bg-slate-600"></span>
              <span>Generating & validating read-only analytical SQL via Qwen 2.5-Coder...</span>
            </div>
            <div className="flex items-center gap-2 text-xs text-slate-500">
              <span className="w-1.5 h-1.5 rounded-full bg-slate-700"></span>
              <span>Executing safe query against FreshMart MySQL replica...</span>
            </div>
            <div className="flex items-center gap-2 text-xs text-slate-500">
              <span className="w-1.5 h-1.5 rounded-full bg-slate-700"></span>
              <span>Formulating executive analysis and chart recommendations via Llama 3.1...</span>
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
};
