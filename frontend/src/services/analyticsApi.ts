import { apiClient } from './api';
import type { AnalyticsResponse } from '../types/analytics';
import type { DashboardResponse, DateRangeOption } from '../types/dashboard';

export const analyticsApi = {
  /**
   * Submit natural language analytics question to the LangGraph pipeline via FastAPI.
   * Authenticated automatically via Axios JWT request interceptor.
   */
  async askAnalyticsQuestion(question: string, conversation_id?: string): Promise<AnalyticsResponse> {
    const response = await apiClient.post<AnalyticsResponse>('/analytics/query', {
      question,
      conversation_id,
    });
    return response.data;
  },

  /**
   * Alias for askAnalyticsQuestion matching Phase 9 specification.
   */
  async runAnalyticsQuery(question: string, conversation_id?: string): Promise<AnalyticsResponse> {
    return this.askAnalyticsQuestion(question, conversation_id);
  },

  /**
   * Fetches real deterministic executive dashboard metrics from FreshMart MySQL.
   */
  async getDashboardMetrics(range: DateRangeOption = '12m'): Promise<DashboardResponse> {
    const response = await apiClient.get<DashboardResponse>('/analytics/dashboard', {
      params: { range },
    });
    return response.data;
  },

  /**
   * Fetches real role-specific dashboard metrics with server-side RBAC enforcement.
   */
  async getRoleDashboard(roleSlug: string, range: DateRangeOption = '12m'): Promise<any> {
    const response = await apiClient.get<any>(`/analytics/dashboard/${roleSlug}`, {
      params: { range },
    });
    return response.data;
  },

  /**
   * Fetches live grounded enterprise business insights, anomalies, and recommendations.
   */
  async getEnterpriseInsights(): Promise<any> {
    const response = await apiClient.get<any>('/analytics/insights');
    return response.data;
  },
};

export const getRoleDashboard = (roleSlug: string, range: DateRangeOption = '12m') =>
  analyticsApi.getRoleDashboard(roleSlug, range);


export const askAnalyticsQuestion = (question: string, conversation_id?: string) =>
  analyticsApi.askAnalyticsQuestion(question, conversation_id);

export const runAnalyticsQuery = (question: string, conversation_id?: string) =>
  analyticsApi.runAnalyticsQuery(question, conversation_id);

export const getDashboardMetrics = (range: DateRangeOption = '12m') =>
  analyticsApi.getDashboardMetrics(range);

export const getEnterpriseInsights = () =>
  analyticsApi.getEnterpriseInsights();

