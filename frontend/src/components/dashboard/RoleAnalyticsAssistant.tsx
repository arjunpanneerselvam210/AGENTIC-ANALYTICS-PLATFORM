import React, { useState } from 'react';
import {
  Sparkles,
  ChevronDown,
  ChevronUp,
  History,
  RotateCcw,
  Database,
  ArrowRight,
  Calendar,
  MessageSquare,
  Trash2,
} from 'lucide-react';
import { useChat, type HistoryItem } from '../../context/ChatContext';
import { QueryInput } from '../analytics/QueryInput';
import { QueryResult } from '../analytics/QueryResult';
import { QueryLoadingState } from '../analytics/QueryLoadingState';


const ROLE_PROMPTS: Record<string, string[]> = {
  ceo: [
    'Show monthly sales trend for the last 12 months',
    'Why did profit decrease in August?',
    'Which products generated the highest revenue and are currently low in stock?',
    'Show lead status distribution',
    'Show average salary by department',
  ],
  sales: [
    'Show monthly sales trend for the last 12 months',
    'Which products generated the highest revenue?',
    'Which products generated the highest revenue and are currently low in stock?',
    'Show lead status distribution',
    'Show customer count by city',
  ],
  finance: [
    'Why did profit decrease in August?',
    'Show monthly sales and revenue trend for the last 12 months',
    'Show total operating expenses by month',
    'Show gross profit margin trend',
  ],
  hr: [
    'Show average salary by department',
    'Show employee count by department',
    'Show employee distribution by job title',
  ],
  inventory: [
    'Which products are currently low in stock?',
    'Which products generated the highest revenue and are currently low in stock?',
    'Show top suppliers by purchase volume',
    'Show stock levels across product categories',
  ],
  erp: [
    'Which products generated the highest revenue and are currently low in stock?',
    'Show top suppliers by purchase orders',
    'Show monthly sales trend for the last 12 months',
    'Show warehouse stock balance',
  ],
};

interface RoleAnalyticsAssistantProps {
  roleSlug: string;
}

export const RoleAnalyticsAssistant: React.FC<RoleAnalyticsAssistantProps> = ({ roleSlug }) => {
  const {

    question,
    setQuestion,
    isLoading,
    currentResult,
    setCurrentResult,
    history,
    archivedSessions,
    historyTab,
    setHistoryTab,
    executeQuery,
    resetSession,
    restoreArchivedSession,
    deleteArchivedSession,
    clearHistory,
  } = useChat();

  const [isOpen, setIsOpen] = useState(true);
  const [showHistoryPanel, setShowHistoryPanel] = useState(false);

  const prompts = ROLE_PROMPTS[roleSlug.toLowerCase()] || ROLE_PROMPTS.ceo;

  const handlePromptClick = (prompt: string) => {
    setQuestion(prompt);
    executeQuery(prompt);
  };

  const handleSelectHistoryItem = (item: HistoryItem) => {
    setQuestion(item.question);
    setCurrentResult(item.response);
  };

  return (
    <div className="bg-gradient-to-b from-[#0F1626] to-[#0A0E1A] border border-slate-800 rounded-2xl shadow-xl overflow-hidden">
      {/* Header Bar */}
      <div className="p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800/80">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-emerald-500/20 to-teal-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 shrink-0">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <h2 className="text-base font-bold text-white tracking-tight">
                Role-Scoped AI Analytics Assistant
              </h2>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/25">
                {roleSlug.toUpperCase()} SCOPE
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700 flex items-center gap-1">
                <Database className="w-3 h-3 text-cyan-400" />
                <span>MySQL MCP Guard</span>
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Ask natural-language inquiries with real-time multi-agent charts and root-cause analysis
            </p>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2 self-end sm:self-auto">
          {history.length > 0 && (
            <button
              onClick={resetSession}
              className="text-xs text-slate-400 hover:text-emerald-300 flex items-center gap-1.5 transition-colors px-2.5 py-1.5 rounded-xl bg-slate-800/50 hover:bg-slate-800 border border-slate-700/50 cursor-pointer"
              title="Archive current conversation and start new one"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">New Session</span>
            </button>
          )}

          <button
            onClick={() => setShowHistoryPanel((prev) => !prev)}
            className={`text-xs flex items-center gap-1.5 transition-colors px-2.5 py-1.5 rounded-xl border cursor-pointer ${
              showHistoryPanel
                ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                : 'text-slate-300 bg-slate-800/50 hover:bg-slate-800 border-slate-700/50'
            }`}
            title="Toggle session history"
          >
            <History className="w-3.5 h-3.5 text-emerald-400" />
            <span>History ({history.length + archivedSessions.length})</span>
          </button>

          <button
            onClick={() => setIsOpen((prev) => !prev)}
            className="p-1.5 text-slate-400 hover:text-white rounded-xl hover:bg-slate-800/60 transition-colors cursor-pointer"
            title={isOpen ? 'Collapse Assistant' : 'Expand Assistant'}
          >
            {isOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      {isOpen && (
        <div className="p-4 sm:p-5 space-y-4">
          {/* Query Bar */}
          <QueryInput
            value={question}
            onChange={setQuestion}
            onSubmit={() => executeQuery(question)}
            isLoading={isLoading}
            placeholder={`Ask ${roleSlug.toUpperCase()} analytics... (e.g. "${prompts[0]}")`}
          />

          {/* Role-Scoped Quick Prompts */}
          <div className="flex flex-wrap items-center gap-2 pt-1">
            <span className="text-[11px] font-semibold text-slate-400 flex items-center gap-1">
              <Sparkles className="w-3 h-3 text-emerald-400" />
              <span>Recommended:</span>
            </span>
            {prompts.map((p, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => handlePromptClick(p)}
                disabled={isLoading}
                className="text-xs bg-slate-800/80 hover:bg-slate-700 text-slate-300 hover:text-white px-2.5 py-1 rounded-lg border border-slate-700/60 hover:border-emerald-500/40 transition-all flex items-center gap-1 text-left disabled:opacity-50 cursor-pointer"
              >
                <span>{p}</span>
                <ArrowRight className="w-2.5 h-2.5 text-slate-500" />
              </button>
            ))}
          </div>

          {/* Session History Drawer (When Toggled) */}
          {showHistoryPanel && (
            <div className="p-4 rounded-xl bg-[#080C14] border border-slate-800/80 space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                <div className="flex items-center gap-2">
                  <History className="w-4 h-4 text-emerald-400" />
                  <span className="text-xs font-bold text-white">Conversation & Session History</span>
                </div>
                {history.length > 0 && historyTab === 'current' && (
                  <button
                    onClick={clearHistory}
                    className="text-[11px] text-slate-400 hover:text-rose-400 transition-colors flex items-center gap-1 cursor-pointer"
                    title="Clear active conversation queries"
                  >
                    <Trash2 className="w-3 h-3" />
                    <span>Clear Active</span>
                  </button>
                )}
              </div>

              {/* Tabs: Current vs Previous */}
              <div className="flex items-center gap-1 p-1 bg-slate-900/60 border border-slate-800/80 rounded-xl text-xs">
                <button
                  type="button"
                  onClick={() => setHistoryTab('current')}
                  className={`flex-1 py-1 px-2 rounded-lg font-medium text-center transition-colors cursor-pointer ${
                    historyTab === 'current'
                      ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  Active Conversation ({history.length})
                </button>
                <button
                  type="button"
                  onClick={() => setHistoryTab('previous')}
                  className={`flex-1 py-1 px-2 rounded-lg font-medium text-center transition-colors cursor-pointer ${
                    historyTab === 'previous'
                      ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  Previous Sessions ({archivedSessions.length})
                </button>
              </div>

              {/* History Items List */}
              <div className="max-h-56 overflow-y-auto space-y-2 pr-1">
                {historyTab === 'current' ? (
                  history.length === 0 ? (
                    <div className="text-center py-4 text-xs text-slate-500">
                      No queries run in this active conversation yet.
                    </div>
                  ) : (
                    history.map((item) => (
                      <button
                        key={item.id}
                        onClick={() => handleSelectHistoryItem(item)}
                        className="w-full text-left p-2.5 rounded-lg bg-slate-800/40 hover:bg-slate-800/80 border border-slate-700/40 hover:border-slate-600 transition-all text-xs group cursor-pointer"
                      >
                        <div className="flex items-center justify-between text-slate-400 text-[10px] mb-1">
                          <span>{item.timestamp}</span>
                          <span className={item.response.success ? 'text-emerald-400 font-mono' : 'text-rose-400 font-mono'}>
                            {item.response.success ? '200 OK' : 'Blocked / Error'}
                          </span>
                        </div>
                        <p className="text-slate-300 font-medium line-clamp-1 group-hover:text-emerald-300">
                          {item.question}
                        </p>
                      </button>
                    ))
                  )
                ) : archivedSessions.length === 0 ? (
                  <div className="text-center py-4 text-xs text-slate-500">
                    No past sessions archived yet. Click "New Session" to save your current work.
                  </div>
                ) : (
                  archivedSessions.map((arch) => (
                    <div
                      key={arch.id}
                      className="p-2.5 rounded-lg bg-slate-800/40 border border-slate-800 flex items-center justify-between gap-3 text-xs"
                    >
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-2 text-[10px] text-slate-400 mb-0.5">
                          <span className="flex items-center gap-1 font-mono">
                            <Calendar className="w-2.5 h-2.5 text-slate-500" />
                            <span>{arch.startedAt}</span>
                          </span>
                          <span className="bg-slate-800 text-slate-300 px-1 py-0.2 rounded font-mono">
                            {arch.queriesCount} queries
                          </span>
                        </div>
                        <p className="text-slate-200 font-medium truncate">{arch.title}</p>
                      </div>

                      <div className="flex items-center gap-1 shrink-0">
                        <button
                          type="button"
                          onClick={() => restoreArchivedSession(arch)}
                          className="px-2.5 py-1 rounded-md bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-400 border border-emerald-500/30 text-[11px] font-semibold flex items-center gap-1 cursor-pointer transition-colors"
                        >
                          <MessageSquare className="w-3 h-3" />
                          <span>Resume</span>
                        </button>
                        <button
                          type="button"
                          onClick={() => deleteArchivedSession(arch.id)}
                          className="p-1 text-slate-500 hover:text-rose-400 transition-colors cursor-pointer"
                          title="Delete session"
                        >
                          <Trash2 className="w-3 h-3" />
                        </button>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}

          {/* Query Results / Loading State */}
          {isLoading && <QueryLoadingState question={question} />}

          {!isLoading && currentResult && (
            <div className="mt-3">
              <QueryResult response={currentResult} />
            </div>
          )}
        </div>
      )}
    </div>
  );
};
