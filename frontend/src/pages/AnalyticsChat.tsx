import React, { useEffect, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  Sparkles,
  History,
  Trash2,
  ArrowRight,
  Database,
  ShieldCheck,
  RotateCcw,
  Calendar,
  MessageSquare,
} from 'lucide-react';
import { QueryInput } from '../components/analytics/QueryInput';
import { QueryResult } from '../components/analytics/QueryResult';
import { QueryLoadingState } from '../components/analytics/QueryLoadingState';
import { useAuth } from '../context/AuthContext';
import { useChat, type HistoryItem } from '../context/ChatContext';

const ROLE_SUGGESTIONS: Record<string, string[]> = {
  CEO: [
    'Show monthly sales trend for the last 12 months',
    'Which products generated the highest revenue and are currently low in stock?',
    'Why did profit decrease in August?',
    'Show lead status distribution',
    'Show average salary by department',
  ],
  SALES_MANAGER: [
    'Show monthly sales trend for the last 12 months',
    'Which products generated the highest revenue?',
    'Which products generated the highest revenue and are currently low in stock?',
    'Show lead status distribution',
    'Show customer count by city',
  ],
  FINANCE_MANAGER: [
    'Why did profit decrease in August?',
    'Show monthly sales and revenue trend for the last 12 months',
    'Show total operating expenses by month',
    'Show gross profit margin trend',
  ],
  HR_MANAGER: [
    'Show average salary by department',
    'Show employee count by department',
    'Show employee distribution by job title',
  ],
  INVENTORY_MANAGER: [
    'Which products are currently low in stock?',
    'Which products generated the highest revenue and are currently low in stock?',
    'Show top suppliers by purchase volume',
    'Show stock levels across product categories',
  ],
  ERP_MANAGER: [
    'Which products generated the highest revenue and are currently low in stock?',
    'Show top suppliers by purchase orders',
    'Show monthly sales trend for the last 12 months',
    'Show warehouse stock balance',
  ],
};

export const AnalyticsChat: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const { user } = useAuth();
  const {
    question,
    setQuestion,
    isLoading,
    historyTab,
    setHistoryTab,
    currentResult,
    setCurrentResult,
    history,
    archivedSessions,
    executeQuery,
    resetSession,
    restoreArchivedSession,
    deleteArchivedSession,
    clearHistory,
  } = useChat();

  const resultsEndRef = useRef<HTMLDivElement>(null);

  const benchmarkSuggestions = (user?.role && ROLE_SUGGESTIONS[user.role])
    ? ROLE_SUGGESTIONS[user.role]
    : ROLE_SUGGESTIONS.CEO;

  // Auto-run if 'q' search param is present in URL
  useEffect(() => {
    const qParam = searchParams.get('q');
    if (qParam && qParam.trim()) {
      setQuestion(qParam);
      executeQuery(qParam);
      setSearchParams({}, { replace: true });
    }
  }, [searchParams]);

  const handleSelectSuggested = (suggested: string) => {
    setQuestion(suggested);
    executeQuery(suggested);
  };

  const handleSelectHistory = (item: HistoryItem) => {
    setQuestion(item.question);
    setCurrentResult(item.response);
  };

  return (
    <div className="space-y-6">
      {/* Page Title & Context */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/60 p-5 rounded-2xl border border-slate-800 shadow-sm">
        <div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
              <Sparkles className="w-4 h-4" />
            </div>
            <h1 className="text-xl font-bold text-white tracking-tight">Analytics Assistant</h1>
          </div>
          <p className="text-slate-400 text-xs sm:text-sm mt-1">
            Autonomous multi-agent analytics across FreshMart's unified ERP, CRM, HRMS, and Inventory databases.
          </p>
        </div>

        {/* User Context & Architecture Telemetry */}
        <div className="flex flex-wrap items-center gap-2">
          <div className="px-3 py-1.5 rounded-xl bg-slate-800/80 border border-slate-700/60 text-xs text-slate-300 flex items-center gap-1.5">
            <Database className="w-3.5 h-3.5 text-blue-400" />
            <span>Target: <strong className="text-slate-200">FreshMart MySQL</strong></span>
          </div>
          <div className="px-3 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-xs text-emerald-400 font-medium flex items-center gap-1.5 font-mono">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Role: {user?.role || 'CEO'}</span>
          </div>
        </div>
      </div>

      {/* Main Query Bar */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-5 shadow-xl">
        <QueryInput
          value={question}
          onChange={setQuestion}
          onSubmit={() => executeQuery(question)}
          isLoading={isLoading}
          placeholder="Ask FreshMart... (e.g. 'Show monthly sales trend' or 'Why did profit decrease in August?')"
        />

        {/* Suggested Queries */}
        <div className="mt-4 pt-4 border-t border-slate-800/60">
          <div className="flex items-center justify-between mb-2">
            <p className="text-xs font-semibold text-slate-400 flex items-center gap-1.5">
              <Sparkles className="w-3 h-3 text-emerald-400" />
              <span>Suggested Analytical Prompts:</span>
            </p>
            {currentResult && (
              <button
                onClick={resetSession}
                className="text-xs text-slate-400 hover:text-emerald-300 flex items-center gap-1 transition-colors px-2 py-0.5 rounded-lg hover:bg-slate-800/50"
              >
                <RotateCcw className="w-3 h-3" />
                <span>New Conversation</span>
              </button>
            )}
          </div>
          <div className="flex flex-wrap gap-2">
            {benchmarkSuggestions.map((sug, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => handleSelectSuggested(sug)}
                disabled={isLoading}
                className="text-xs bg-slate-800/80 hover:bg-slate-700/90 text-slate-300 hover:text-white px-3 py-1.5 rounded-lg border border-slate-700/50 hover:border-emerald-500/40 transition-all flex items-center gap-1.5 text-left disabled:opacity-50"
              >
                <span>{sug}</span>
                <ArrowRight className="w-3 h-3 text-slate-500 group-hover:text-emerald-400" />
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Results / Loading / History Section */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Main Content Area (3 cols) */}
        <div className="lg:col-span-3 space-y-6">
          {isLoading && <QueryLoadingState question={question} />}

          {!isLoading && currentResult && (
            <QueryResult response={currentResult} />
          )}

          {!isLoading && !currentResult && (
            <div className="p-12 text-center bg-slate-900/40 border border-slate-800/60 rounded-2xl">
              <div className="w-12 h-12 rounded-2xl bg-slate-800/80 border border-slate-700/60 flex items-center justify-center text-slate-400 mx-auto mb-3">
                <Sparkles className="w-6 h-6 text-emerald-400" />
              </div>
              <h3 className="text-base font-semibold text-slate-200">Ask FreshMart Analytics</h3>
              <p className="text-xs text-slate-400 max-w-md mx-auto mt-1 leading-relaxed">
                Explore sales velocity, product margins, inventory deficits, CRM pipelines, and workforce allocation
                using natural language backed by LangGraph and MCP.
              </p>
            </div>
          )}

          <div ref={resultsEndRef} />
        </div>

        {/* Query History Sidebar (1 col) */}
        <div className="lg:col-span-1">
          <div className="bg-slate-900/70 border border-slate-800 rounded-2xl p-4 sticky top-20 shadow-sm">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <History className="w-4 h-4 text-emerald-400" />
                <h3 className="text-sm font-semibold text-slate-200">Session History</h3>
              </div>
              {history.length > 0 && historyTab === 'current' && (
                <button
                  onClick={clearHistory}
                  className="text-slate-500 hover:text-rose-400 transition-colors p-1"
                  title="Clear active conversation queries"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              )}
            </div>

            {/* Session Tabs: Current vs Previous */}
            <div className="flex items-center gap-1 my-3 p-1 bg-slate-950/60 border border-slate-800/80 rounded-xl text-xs">
              <button
                type="button"
                onClick={() => setHistoryTab('current')}
                className={`flex-1 py-1.5 px-2 rounded-lg font-medium text-center transition-colors cursor-pointer ${
                  historyTab === 'current'
                    ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Current ({history.length})
              </button>
              <button
                type="button"
                onClick={() => setHistoryTab('previous')}
                className={`flex-1 py-1.5 px-2 rounded-lg font-medium text-center transition-colors cursor-pointer ${
                  historyTab === 'previous'
                    ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                Past ({archivedSessions.length})
              </button>
            </div>

            {/* Active Tab Content */}
            <div className="space-y-2 max-h-[500px] overflow-y-auto pr-1">
              {historyTab === 'current' ? (
                history.length === 0 ? (
                  <div className="text-center py-8 px-2 space-y-1">
                    <p className="text-xs text-slate-400 font-medium">No queries yet in this session</p>
                    <p className="text-[11px] text-slate-500">
                      Submit a question above to see live analysis and chart responses.
                    </p>
                  </div>
                ) : (
                  history.map((item) => (
                    <button
                      key={item.id}
                      onClick={() => handleSelectHistory(item)}
                      className="w-full text-left p-2.5 rounded-xl bg-slate-800/50 hover:bg-slate-800 border border-slate-700/40 hover:border-slate-600 transition-all text-xs group cursor-pointer"
                    >
                      <div className="flex items-center justify-between text-slate-400 text-[10px] mb-1">
                        <span>{item.timestamp}</span>
                        <span className={item.response.success ? 'text-emerald-400 font-mono' : 'text-rose-400 font-mono'}>
                          {item.response.success ? '200 OK' : 'Blocked / Error'}
                        </span>
                      </div>
                      <p className="text-slate-300 font-medium line-clamp-2 group-hover:text-emerald-300">
                        {item.question}
                      </p>
                    </button>
                  ))
                )
              ) : (
                /* Previous Archived Sessions */
                archivedSessions.length === 0 ? (
                  <div className="text-center py-8 px-2 space-y-1">
                    <p className="text-xs text-slate-400 font-medium">No previous sessions saved</p>
                    <p className="text-[11px] text-slate-500 leading-relaxed">
                      When you click "New Conversation" or log out, your sessions are archived here so you can revisit them anytime.
                    </p>
                  </div>
                ) : (
                  archivedSessions.map((arch) => (
                    <div
                      key={arch.id}
                      className="p-3 rounded-xl bg-slate-800/40 border border-slate-800 hover:border-slate-700 transition-all text-xs space-y-2"
                    >
                      <div className="flex items-center justify-between text-[10px] text-slate-400">
                        <span className="flex items-center gap-1 font-mono">
                          <Calendar className="w-3 h-3 text-slate-500" />
                          <span>{arch.startedAt}</span>
                        </span>
                        <div className="flex items-center gap-1">
                          <span className="bg-slate-800 text-slate-300 px-1.5 py-0.5 rounded font-mono">
                            {arch.queriesCount} queries
                          </span>
                          <button
                            type="button"
                            onClick={(e) => {
                              e.stopPropagation();
                              deleteArchivedSession(arch.id);
                            }}
                            className="text-slate-500 hover:text-rose-400 transition-colors p-0.5"
                            title="Delete this archived session"
                          >
                            <Trash2 className="w-3 h-3" />
                          </button>
                        </div>
                      </div>
                      <p className="text-slate-200 font-medium line-clamp-2">
                        {arch.title}
                      </p>
                      <button
                        type="button"
                        onClick={() => restoreArchivedSession(arch)}
                        className="w-full text-center py-1 rounded-lg bg-emerald-600/15 hover:bg-emerald-600/25 border border-emerald-500/30 text-emerald-400 text-[11px] font-semibold flex items-center justify-center gap-1.5 transition-colors cursor-pointer"
                      >
                        <MessageSquare className="w-3 h-3" />
                        <span>Resume Session ({arch.queriesCount} Qs)</span>
                      </button>
                    </div>
                  ))
                )
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
