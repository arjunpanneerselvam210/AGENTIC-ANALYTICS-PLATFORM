import { apiClient } from './api';

export interface ChatSessionPayload {
  id: string;
  title: string;
  started_at: string;
  queries_count: number;
  items: Array<{
    id: string;
    question: string;
    timestamp: string;
    response: any;
  }>;
}

export const chatApi = {
  /**
   * Fetch all archived conversation sessions for the authenticated user from PostgreSQL.
   */
  async getSessions(): Promise<ChatSessionPayload[]> {
    try {
      const response = await apiClient.get<{ sessions: ChatSessionPayload[]; total: number }>('/chat/sessions');
      return response.data?.sessions || [];
    } catch (err) {
      console.warn('Backend session fetch failed, falling back to local storage cache:', err);
      return [];
    }
  },

  /**
   * Save or archive a session in the database for persistent history.
   */
  async saveSession(session: ChatSessionPayload): Promise<ChatSessionPayload | null> {
    try {
      const response = await apiClient.post<ChatSessionPayload>('/chat/sessions', session);
      return response.data;
    } catch (err) {
      console.warn('Backend session save failed, retained in local storage:', err);
      return null;
    }
  },

  /**
   * Delete an archived session from database.
   */
  async deleteSession(sessionId: string): Promise<boolean> {
    try {
      await apiClient.delete(`/chat/sessions/${sessionId}`);
      return true;
    } catch (err) {
      console.warn('Backend session delete failed:', err);
      return false;
    }
  },
};
