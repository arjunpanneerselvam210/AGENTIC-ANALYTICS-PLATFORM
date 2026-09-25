import React, { createContext, useContext, useState, useEffect, useRef, useCallback } from 'react';
import { useAuth } from './AuthContext';
import { runAnalyticsQuery } from '../services/analyticsApi';
import { chatApi, type ChatSessionPayload } from '../services/chatApi';
import type { AnalyticsResponse } from '../types/analytics';
import { formatISTTime, formatISTDateTime } from '../utils/dateUtils';




export interface HistoryItem {
  id: string;
  question: string;
  timestamp: string;
  response: AnalyticsResponse;
}

export interface SessionArchiveItem {
  id: string;
  startedAt: string;
  title: string;
  queriesCount: number;
  items: HistoryItem[];
}

interface ActiveSessionData {
  conversationId: string;
  question: string;
  currentResult: AnalyticsResponse | null;
  history: HistoryItem[];
  lastUpdated: string;
}

interface ChatContextType {
  question: string;
  setQuestion: (q: string) => void;
  isLoading: boolean;
  historyTab: 'current' | 'previous';
  setHistoryTab: (tab: 'current' | 'previous') => void;
  currentResult: AnalyticsResponse | null;
  setCurrentResult: (res: AnalyticsResponse | null) => void;
  history: HistoryItem[];
  archivedSessions: SessionArchiveItem[];
  conversationId: string;
  executeQuery: (queryToRun: string) => Promise<void>;
  resetSession: () => void;
  restoreArchivedSession: (session: SessionArchiveItem) => void;
  deleteArchivedSession: (sessionId: string) => void;
  clearHistory: () => void;
  archiveActiveSession: () => void;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const ChatProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user } = useAuth();
  const userKey = user?.username || user?.role || 'freshmart_user';

  // Read initial active session safely
  const initialActive = (() => {
    try {
      const raw = localStorage.getItem(`freshmart_active_session_${userKey}`);
      if (raw) {
        const parsed: ActiveSessionData = JSON.parse(raw);
        return parsed;
      }
    } catch (e) {
      console.warn('Failed parsing active session on init', e);
    }
    return null;
  })();

  const initialArchive = (() => {
    try {
      const raw = localStorage.getItem(`freshmart_session_history_${userKey}`);
      if (raw) {
        const parsed: SessionArchiveItem[] = JSON.parse(raw);
        return Array.isArray(parsed) ? parsed : [];
      }
    } catch (e) {
      console.warn('Failed parsing session history on init', e);
    }
    return [];
  })();

  const [question, setQuestion] = useState<string>(initialActive?.question || '');
  const [isLoading, setIsLoading] = useState(false);
  const [historyTab, setHistoryTab] = useState<'current' | 'previous'>('current');
  const [currentResult, setCurrentResult] = useState<AnalyticsResponse | null>(initialActive?.currentResult || null);
  const [history, setHistory] = useState<HistoryItem[]>(initialActive?.history || []);
  const [conversationId, setConversationId] = useState<string>(initialActive?.conversationId || `conv-${Date.now()}`);
  const [archivedSessions, setArchivedSessions] = useState<SessionArchiveItem[]>(initialArchive);

  // Guard ref to prevent hydration from triggering persist effects with default/stale state
  const isHydratingRef = useRef(false);
  const prevUserKeyRef = useRef(userKey);

  // Helper: Archive active session synchronously to localStorage and backend
  const archiveActiveSession = useCallback(() => {
    if (history.length === 0) return;

    const currentKey = userKey;
    const sessionToArchive: SessionArchiveItem = {
      id: conversationId,
      startedAt: formatISTDateTime(new Date()),
      title: history[history.length - 1]?.question || history[0]?.question || 'Analytics Investigation',
      queriesCount: history.length,
      items: [...history],
    };


    try {
      const existingRaw = localStorage.getItem(`freshmart_session_history_${currentKey}`);
      const existing: SessionArchiveItem[] = existingRaw ? JSON.parse(existingRaw) : [];
      const updated = [sessionToArchive, ...existing.filter((s) => s.id !== conversationId).slice(0, 29)];
      localStorage.setItem(`freshmart_session_history_${currentKey}`, JSON.stringify(updated));
      setArchivedSessions(updated);

      // Async sync to server
      chatApi.saveSession({
        id: sessionToArchive.id,
        title: sessionToArchive.title,
        started_at: sessionToArchive.startedAt,
        queries_count: sessionToArchive.queriesCount,
        items: sessionToArchive.items,
      });
    } catch (e) {
      console.warn('Failed archiving active session:', e);
    }
  }, [userKey, conversationId, history]);

  // Handle user login, logout, or account switch
  useEffect(() => {
    if (prevUserKeyRef.current !== userKey) {
      const prevKey = prevUserKeyRef.current;

      // 1. Archive previous user's active session if it had queries
      if (prevKey && history.length > 0) {
        try {
          const oldArchRaw = localStorage.getItem(`freshmart_session_history_${prevKey}`);
          const oldArch: SessionArchiveItem[] = oldArchRaw ? JSON.parse(oldArchRaw) : [];
          const sessionToSave: SessionArchiveItem = {
            id: conversationId,
            startedAt: formatISTDateTime(new Date()),
            title: history[history.length - 1]?.question || history[0]?.question || 'Analytics Investigation',
            queriesCount: history.length,
            items: [...history],
          };
          const updated = [sessionToSave, ...oldArch.filter((s) => s.id !== conversationId).slice(0, 29)];
          localStorage.setItem(`freshmart_session_history_${prevKey}`, JSON.stringify(updated));
        } catch (e) {
          console.warn('Failed auto-archiving previous user session', e);
        }
      }

      // 2. Start Hydrating new user's session data
      isHydratingRef.current = true;
      try {
        const rawActive = localStorage.getItem(`freshmart_active_session_${userKey}`);
        const rawHistory = localStorage.getItem(`freshmart_session_history_${userKey}`);

        let activeParsed: ActiveSessionData | null = null;
        if (rawActive) {
          try {
            activeParsed = JSON.parse(rawActive);
          } catch {}
        }

        let historyParsed: SessionArchiveItem[] = [];
        if (rawHistory) {
          try {
            const parsed = JSON.parse(rawHistory);
            if (Array.isArray(parsed)) historyParsed = parsed;
          } catch {}
        }

        setConversationId(activeParsed?.conversationId || `conv-${Date.now()}`);
        setQuestion(activeParsed?.question || '');
        setCurrentResult(activeParsed?.currentResult || null);
        setHistory(activeParsed?.history || []);
        setArchivedSessions(historyParsed);

        // Fetch backend sessions and merge seamlessly
        chatApi.getSessions().then((serverSessions: ChatSessionPayload[]) => {
          if (serverSessions && serverSessions.length > 0) {
            setArchivedSessions((localArch) => {
              const mergedMap = new Map<string, SessionArchiveItem>();
              // Put local first
              localArch.forEach((item) => mergedMap.set(item.id, item));
              // Merge server
              serverSessions.forEach((s) => {
                if (!mergedMap.has(s.id)) {
                  mergedMap.set(s.id, {
                    id: s.id,
                    title: s.title,
                    startedAt: s.started_at,
                    queriesCount: s.queries_count,
                    items: s.items || [],
                  });
                }
              });
              const mergedList = Array.from(mergedMap.values()).slice(0, 30);
              try {
                localStorage.setItem(`freshmart_session_history_${userKey}`, JSON.stringify(mergedList));
              } catch {}
              return mergedList;
            });
          }
        });
      } catch (e) {
        console.warn('Error hydrating user session', e);
      } finally {
        setTimeout(() => {
          isHydratingRef.current = false;
        }, 50);
      }

      prevUserKeyRef.current = userKey;
    }
  }, [userKey]);

  // Persist active session on changes (only when not hydrating)
  useEffect(() => {
    if (isHydratingRef.current) return;

    try {
      const activeData: ActiveSessionData = {
        conversationId,
        question,
        currentResult,
        history,
        lastUpdated: new Date().toISOString(),
      };
      localStorage.setItem(`freshmart_active_session_${userKey}`, JSON.stringify(activeData));
    } catch (e) {
      console.warn('Failed persisting active session', e);
    }
  }, [userKey, conversationId, question, currentResult, history]);

  // Persist archived sessions on changes (only when not hydrating)
  useEffect(() => {
    if (isHydratingRef.current) return;

    try {
      localStorage.setItem(`freshmart_session_history_${userKey}`, JSON.stringify(archivedSessions));
    } catch (e) {
      console.warn('Failed persisting archived sessions', e);
    }
  }, [userKey, archivedSessions]);

  // Execute analytics query
  const executeQuery = async (queryToRun: string) => {
    const trimmed = queryToRun.trim();
    if (!trimmed || isLoading) return;

    setIsLoading(true);
    setCurrentResult(null);

    try {
      const response: AnalyticsResponse = await runAnalyticsQuery(trimmed, conversationId);
      setCurrentResult(response);

      const newHistoryItem: HistoryItem = {
        id: Date.now().toString(),
        question: trimmed,
        timestamp: formatISTTime(new Date()),
        response,
      };

      setHistory((prev) => {
        const updated = [newHistoryItem, ...prev];
        // Automatically save session to backend in background
        const sessionPayload: ChatSessionPayload = {
          id: conversationId,
          title: updated[updated.length - 1]?.question || trimmed,
          started_at: formatISTDateTime(new Date()),
          queries_count: updated.length,
          items: updated,
        };
        chatApi.saveSession(sessionPayload);
        return updated;
      });
    } catch (err: unknown) {
      let errorMessage = 'Unable to analyze this question. Please try again.';
      let isForbidden = false;

      if (err && typeof err === 'object' && 'response' in err) {
        const axErr = err as { response?: { status?: number; data?: { detail?: string; error?: string } } };
        if (axErr.response?.status === 403) {
          isForbidden = true;
          errorMessage = axErr.response.data?.detail || 'Access Restricted: You do not have permission to view this type of business data.';
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
        timestamp: formatISTTime(new Date()),
        response: errorResponse,
      };
      setHistory((prev) => [newHistoryItem, ...prev]);
    } finally {
      setIsLoading(false);
    }
  };

  // Reset current session and cleanly archive active queries
  const resetSession = () => {
    if (history.length > 0) {
      const newArchiveItem: SessionArchiveItem = {
        id: conversationId,
        startedAt: formatISTDateTime(new Date()),
        title: history[history.length - 1]?.question || history[0]?.question || 'Analytics Investigation',
        queriesCount: history.length,
        items: [...history],
      };

      setArchivedSessions((prev) => [
        newArchiveItem,
        ...prev.filter((s) => s.id !== conversationId).slice(0, 29),
      ]);

      chatApi.saveSession({
        id: newArchiveItem.id,
        title: newArchiveItem.title,
        started_at: newArchiveItem.startedAt,
        queries_count: newArchiveItem.queriesCount,
        items: newArchiveItem.items,
      });
    }

    const newConvId = `conv-${Date.now()}`;
    setConversationId(newConvId);
    setCurrentResult(null);
    setHistory([]);
    setQuestion('');
  };

  // Restore a past archived session
  const restoreArchivedSession = (session: SessionArchiveItem) => {
    if (session.items && session.items.length > 0) {
      // If current session has items not yet archived, archive them first
      if (history.length > 0 && conversationId !== session.id) {
        const currentToArchive: SessionArchiveItem = {
          id: conversationId,
          startedAt: formatISTDateTime(new Date()),
          title: history[history.length - 1]?.question || history[0]?.question || 'Analytics Investigation',
          queriesCount: history.length,
          items: [...history],
        };

        setArchivedSessions((prev) => [
          currentToArchive,
          ...prev.filter((s) => s.id !== conversationId).slice(0, 29),
        ]);

        chatApi.saveSession({
          id: currentToArchive.id,
          title: currentToArchive.title,
          started_at: currentToArchive.startedAt,
          queries_count: currentToArchive.queriesCount,
          items: currentToArchive.items,
        });
      }

      setConversationId(session.id);
      setHistory(session.items);
      setCurrentResult(session.items[0]?.response || null);
      setQuestion(session.items[0]?.question || '');
      setHistoryTab('current');
    }
  };

  // Delete an archived session
  const deleteArchivedSession = (sessionId: string) => {
    setArchivedSessions((prev) => prev.filter((s) => s.id !== sessionId));
    chatApi.deleteSession(sessionId);
  };

  // Clear current history
  const clearHistory = () => {
    setHistory([]);
    setCurrentResult(null);
    setQuestion('');
  };

  return (
    <ChatContext.Provider
      value={{
        question,
        setQuestion,
        isLoading,
        historyTab,
        setHistoryTab,
        currentResult,
        setCurrentResult,
        history,
        archivedSessions,
        conversationId,
        executeQuery,
        resetSession,
        restoreArchivedSession,
        deleteArchivedSession,
        clearHistory,
        archiveActiveSession,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};
