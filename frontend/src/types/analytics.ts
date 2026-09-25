export interface VisualizationHintObject {
  type: 'line' | 'bar' | 'area' | 'pie' | 'donut' | 'table' | 'kpi' | 'line_chart' | 'bar_chart' | 'pie_chart' | 'metric_card';
  x_axis?: string;
  y_axis?: string;
  series?: string[];
  title?: string;
}

export type VisualizationHint =
  | 'line_chart'
  | 'bar_chart'
  | 'pie_chart'
  | 'metric_card'
  | 'table'
  | 'line'
  | 'bar'
  | 'area'
  | 'pie'
  | 'donut'
  | 'kpi'
  | VisualizationHintObject;

export interface AnalyticsDataPayload {
  columns: string[];
  rows: Record<string, any>[];
  row_count: number;
  truncated: boolean;
}

export interface DataSource {
  table: string;
  columns?: string[];
}

export interface AnalyticsIntentPayload {
  domain?: string;
  operation?: string;
  metric?: string;
  dimension?: string;
  time_range?: string;
  confidence?: number;
}

export interface InvestigationPlan {
  goal: string;
  steps: string[];
  focus_metrics?: string[];
}

export interface RootCauseFactor {
  factor: string;
  previous_value?: number;
  current_value?: number;
  change?: number;
  change_pct?: number;
  impact: string;
  confidence: string;
  source?: string[];
}

export interface RootCauseAnalysis {
  analysis_type: string;
  summary: string;
  period: { current: string; previous: string };
  metrics: Record<string, number>;
  factors: RootCauseFactor[];
  confidence: string;
  sources?: any[];
}

export interface ComparisonMetric {
  dimension: string;
  current_period: string;
  previous_period: string;
  current_value: number;
  previous_value: number;
  absolute_change: number;
  percentage_change: number;
}

export interface TrendSummary {
  direction: string;
  highest_period?: { period: string; value: number };
  lowest_period?: { period: string; value: number };
  avg_growth_pct?: number;
  summary: string;
}

export interface AnomalyItem {
  metric: string;
  period: string;
  value: number;
  baseline: number;
  change_percent: number;
  anomaly: boolean;
  severity: string;
}

export interface BusinessInsightItem {
  id: string;
  title: string;
  summary: string;
  domain: string;
  impact: string;
  evidence_metric?: string;
  recommendation?: string;
}

export interface ActionableRecommendation {
  title: string;
  reason: string;
  priority: string;
  related_domain: string;
  suggested_action: string;
}

export interface AnalyticsResponse {
  success: boolean;
  question: string;
  answer: string;
  data?: AnalyticsDataPayload | Record<string, any>[];
  intent?: AnalyticsIntentPayload | string;
  sources?: (string | DataSource)[];
  columns_used?: string[];
  visualization_hint?: VisualizationHint;
  error?: string | null;
  user_role?: string;
  user_name?: string;
  timestamp?: string;
  investigation_plan?: InvestigationPlan;
  root_cause_analysis?: RootCauseAnalysis;
  comparisons?: ComparisonMetric[];
  trends?: TrendSummary;
  anomalies?: AnomalyItem[];
  insights?: BusinessInsightItem[];
  recommendations?: ActionableRecommendation[];
  confidence?: string;
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  content: string;
  response?: AnalyticsResponse;
  timestamp: Date;
  status: 'pending' | 'success' | 'error';
  error?: string;
}
