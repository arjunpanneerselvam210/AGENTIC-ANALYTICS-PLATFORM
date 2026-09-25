import React, { useState, useEffect, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  Sparkles,
  History,
  Trash2,
  ArrowRight,
  Database,
  ShieldCheck,
  RotateCcw
} from 'lucide-react';
import { QueryInput } from '../components/analytics/QueryInput';
import { QueryResult } from '../components/analytics/QueryResult';
import { QueryLoadingState } from '../components/analytics/QueryLoadingState';
import { runAnalyticsQuery } from '../services/analyticsApi';
import type { AnalyticsResponse } from '../types/analytics';
import { useAuth } from '../context/AuthContext';

interface HistoryItem {
  id: string;
  question: string;
  timestamp: string;
  response: AnalyticsResponse;
}

const BENCHMARK_SUGGESTIONS = [
  'Show monthly sales trend for the last 12 months',
  'Which products generated the highest revenue?',
  'Which products generated the highest revenue and are currently low in stock?',
  'Why did profit decrease in August?',
  'Show lead status distribution',
  'Show average salary by department',
  'Show employee salaries', // Tests RBAC 403 Access Restricted
];

export const AnalyticsChat: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const { user } = useAuth();

  const [question, setQuestion] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentResult, setCurrentResult] = useState<AnalyticsResponse | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [conversationId, setConversationId] = useState<string>(`conv-${Date.now()}`);
  const resultsEndRef = useRef<HTMLDivElement>(null);

  // Auto-run if 'q' search param is present in URL
  useEffect(() => {
    const qParam = searchParams.get('q');
    if (qParam && qParam.trim()) {
      setQuestion(qParam);
      handleExecuteQuery(qParam);
      setSearchParams({}, { replace: true });
    }
  }, [searchParams]);

  const handleExecuteQuery = async (queryToRun: string) => {
    const trimmed = queryToRun.trim();
    if (!trimmed || isLoading) return;

    setIsLoading(true);
    setCurrentResult(null);

    try {
      // Submits real query to FastAPI -> LangGraph -> MCP -> MySQL
      const response: AnalyticsResponse = await runAnalyticsQuery(trimmed, conversationId);
      setCurrentResult(response);

      const newHistoryItem: HistoryItem = {
        id: Date.now().toString(),
        question: trimmed,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        response,
      };
      setHistory((prev) => [newHistoryItem, ...prev]);
    } catch (err: unknown) {
      // Handle real HTTP errors from FastAPI without fabricating fake success
      let errorMessage = 'Unable to analyze this question. Please try again.';
      let isForbidden = false;

      if (err && typeof err === 'object' && 'response' in err) {
        const axErr = err as { response?: { status?: number; data?: { detail?: string; error?: string } } };
        if (axErr.response?.status === 403) {
          isForbidden = true;
          errorMessage = axErr.response.data?.detail || "Access Restricted: You do not have permission to view this type of business data.";
        } else if (axErr.response?.status === 401) {
          errorMessage = 'Your session has expired. Please sign in again.';
        } else if (axErr.response?.status === 422) {
          errorMessage = "We couldn't understand that analytics request. Try asking in a different way.";
        } else if (axErr.response?.data?.detail) {
          errorMessage = axErr.response.data.detail;
        }
      } else if (err instanceof Error) {
        errorMessage = err.message;
      }

      const errorResponse: AnalyticsResponse = {
        success: false,
        question: trimmed,
        answer: errorMessage,
        error: errorMessage,
        intent: {
          domain: isForbidden ? 'SECURITY_RBAC' : 'ERROR',
          operation: isForbidden ? 'access_denied' : 'query_error',
        },
        sources: [],
        timestamp: new Date().toISOString(),
      };

      setCurrentResult(errorResponse);

      const newHistoryItem: HistoryItem = {
        id: Date.now().toString(),
        question: trimmed,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        response: errorResponse,
      };
      setHistory((prev) => [newHistoryItem, ...prev]);
    } finally {
      setIsLoading(false);
      setTimeout(() => {
        resultsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    }
  };

  const handleSelectSuggested = (suggested: string) => {
    setQuestion(suggested);
    handleExecuteQuery(suggested);
  };

  const handleSelectHistory = (item: HistoryItem) => {
    setQuestion(item.question);
    setCurrentResult(item.response);
  };

  const handleClearHistory = () => {
    setHistory([]);
  };

  const handleResetSession = () => {
    setConversationId(`conv-${Date.now()}`);
    setCurrentResult(null);
    setQuestion('');
  };

  return (
    <div className="space-y-6">
      {/* Page Title & Context */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/60 p-5 rounded-xl border border-slate-800 shadow-sm">
        <div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
              <Sparkles className="w-4 h-4" />
            </div>
            <h1 className="text-xl font-bold text-white tracking-tight">Analytics Assistant</h1>
          </div>
          <p className="text-slate-400 text-sm mt-1">
            Autonomous multi-agent analytics across FreshMart's unified ERP, CRM, HRMS, and Inventory databases.
          </p>
        </div>

        {/* User Context & Architecture Telemetry */}
        <div className="flex flex-wrap items-center gap-2">
          <div className="px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700/60 text-xs text-slate-300 flex items-center gap-1.5">
            <Database className="w-3.5 h-3.5 text-blue-400" />
            <span>Target: <strong className="text-slate-200">FreshMart MySQL</strong></span>
          </div>
          <div className="px-3 py-1.5 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-xs text-emerald-400 font-medium flex items-center gap-1.5">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Role: {user?.role || 'CEO'}</span>
          </div>
        </div>
      </div>

      {/* Main Query Bar (NO MICROPHONE BUTTON) */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-5 shadow-xl">
        <QueryInput
          value={question}
          onChange={setQuestion}
          onSubmit={() => handleExecuteQuery(question)}
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
                onClick={handleResetSession}
                className="text-[11px] text-slate-500 hover:text-slate-300 flex items-center gap-1 transition-colors"
              >
                <RotateCcw className="w-3 h-3" />
                <span>New Conversation</span>
              </button>
            )}
          </div>
          <div className="flex flex-wrap gap-2">
            {BENCHMARK_SUGGESTIONS.map((sug, idx) => (
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
            <div className="p-12 text-center bg-slate-900/40 border border-slate-800/60 rounded-xl">
              <div className="w-12 h-12 rounded-xl bg-slate-800/80 border border-slate-700/60 flex items-center justify-center text-slate-400 mx-auto mb-3">
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
          <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-4 sticky top-20 shadow-sm">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <History className="w-4 h-4 text-emerald-400" />
                <h3 className="text-sm font-semibold text-slate-200">Session History</h3>
              </div>
              {history.length > 0 && (
                <button
                  onClick={handleClearHistory}
                  className="text-slate-500 hover:text-red-400 transition-colors p-1"
                  title="Clear query history"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              )}
            </div>

            <div className="mt-3 space-y-2 max-h-[500px] overflow-y-auto pr-1">
              {history.length === 0 ? (
                <p className="text-xs text-slate-500 text-center py-6">
                  No questions asked yet in this session.
                </p>
              ) : (
                history.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => handleSelectHistory(item)}
                    className="w-full text-left p-2.5 rounded-lg bg-slate-800/50 hover:bg-slate-800 border border-slate-700/40 hover:border-slate-600 transition-all text-xs group"
                  >
                    <div className="flex items-center justify-between text-slate-400 text-[10px] mb-1">
                      <span>{item.timestamp}</span>
                      <span className={item.response.success ? 'text-emerald-400' : 'text-red-400'}>
                        {item.response.success ? '200 OK' : 'Blocked / Error'}
                      </span>
                    </div>
                    <p className="text-slate-300 font-medium line-clamp-2 group-hover:text-emerald-300">
                      {item.question}
                    </p>
                  </button>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
