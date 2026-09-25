"""
Pydantic Schemas for FreshMart Analytics API.
Provides typed, validated models for natural-language queries, executive dashboards,
enterprise insights, root-cause decomposition, and data provenance.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, ConfigDict, Field
from app.core.time_utils import get_current_ist

class AnalyticsQueryRequest(BaseModel):
    """Natural-language business question submitted to the multi-agent analytics pipeline."""
    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Natural-language business analytics question.",
        example="Show monthly sales trend for the last 12 months."
    )
    conversation_id: Optional[str] = Field(
        default=None,
        description="Optional conversation session ID for contextual conversational memory across turns.",
        example="session-marketing-01"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "question": "Show monthly sales trend for the last 12 months."
                },
                {
                    "question": "Which products are currently low in stock?"
                },
                {
                    "question": "Which products generated the highest revenue and are currently low in stock?"
                },
                {
                    "question": "Why did profit decrease in August?"
                },
                {
                    "question": "Show average employee salary by department."
                }
            ]
        }
    )

class AnalyticsDataPayload(BaseModel):
    """Tabular database query result payload."""
    columns: List[str] = Field(default_factory=list, description="List of column names returned by query", example=["month", "revenue", "orders"])
    rows: List[Dict[str, Any]] = Field(default_factory=list, description="List of row objects mapping column name to value")
    row_count: int = Field(0, description="Total number of records returned", example=12)
    truncated: bool = Field(False, description="Flag indicating if results were capped by safety limit", example=False)

class VisualizationHintModel(BaseModel):
    """Frontend charting and visualization recommendation."""
    type: str = Field("table", description="Chart type: line, bar, area, pie, donut, table, kpi", example="line")
    x_axis: Optional[str] = Field(None, description="Field name for horizontal X-axis", example="month")
    y_axis: Optional[str] = Field(None, description="Field name for vertical Y-axis", example="revenue")
    series: Optional[List[str]] = Field(None, description="Series field names for multi-dimensional comparisons")
    title: Optional[str] = Field(None, description="Recommended chart title for dashboard display", example="12-Month Sales Velocity")

class InvestigationPlan(BaseModel):
    """Diagnostic multi-step plan formulated by the Investigation Planner agent."""
    goal: str = Field(..., description="High-level analytical investigation objective", example="Diagnose August 2026 profit contraction")
    steps: List[str] = Field(default_factory=list, description="Sequential diagnostic investigation steps")
    focus_metrics: List[str] = Field(default_factory=list, description="Target metrics examined during investigation", example=["revenue", "cogs", "expenses", "net_profit"])

class RootCauseFactor(BaseModel):
    """Specific variance factor identified during root-cause analysis."""
    factor: str = Field(..., description="Description of the contributing variance driver", example="Emergency Freight Surge")
    previous_value: Optional[float] = Field(None, description="Baseline period metric value", example=89326.0)
    current_value: Optional[float] = Field(None, description="Current period metric value", example=430000.0)
    change: Optional[float] = Field(None, description="Absolute variance delta", example=340674.0)
    change_pct: Optional[float] = Field(None, description="Percentage variance delta", example=381.4)
    impact: str = Field("negative", description="Impact orientation (negative or positive)", example="negative")
    confidence: str = Field("HIGH", description="Confidence assessment (HIGH, MEDIUM, LOW)", example="HIGH")
    source: List[str] = Field(default_factory=list, description="Database tables backing this finding", example=["expenses"])

class RootCauseAnalysis(BaseModel):
    """Structured root-cause decomposition for margin, profit, or cost variances."""
    analysis_type: str = Field("ROOT_CAUSE", description="Analysis classification type", example="ROOT_CAUSE")
    summary: str = Field(..., description="Executive summary explaining root cause findings")
    period: Dict[str, str] = Field(default_factory=lambda: {"current": "August 2026", "previous": "July 2026"}, description="Comparative time periods")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="Comparative summary metrics")
    factors: List[RootCauseFactor] = Field(default_factory=list, description="Ranked contributing causal factors")
    confidence: str = Field("HIGH", description="Synthesis confidence rating", example="HIGH")
    sources: List[Dict[str, Any]] = Field(default_factory=list, description="Underlying telemetry sources")

class ComparisonMetric(BaseModel):
    """Comparative period-over-period or dimension-over-dimension metric variance."""
    dimension: str = Field(..., description="Business dimension or segment", example="Fresh Produce")
    current_period: str = Field(..., description="Current evaluation period", example="August 2026")
    previous_period: str = Field(..., description="Baseline reference period", example="July 2026")
    current_value: float = Field(..., description="Current value", example=600000.0)
    previous_value: float = Field(..., description="Previous baseline value", example=1200000.0)
    absolute_change: float = Field(..., description="Absolute variance delta", example=-600000.0)
    percentage_change: float = Field(..., description="Percentage variance delta", example=-50.0)

class TrendSummary(BaseModel):
    """Time-series directional trend analysis."""
    direction: str = Field("UPWARD", description="Directional trend velocity: UPWARD, DOWNWARD, STABLE", example="UPWARD")
    highest_period: Optional[Dict[str, Any]] = Field(None, description="Peak performing period data point")
    lowest_period: Optional[Dict[str, Any]] = Field(None, description="Lowest performing period data point")
    avg_growth_pct: Optional[float] = Field(None, description="Average period growth rate", example=4.2)
    summary: str = Field("", description="Narrative trend explanation")

class AnomalyItem(BaseModel):
    """Statistical business anomaly or threshold breach detected in ledger data."""
    metric: str = Field(..., description="Anomalous business metric", example="Emergency Shipping")
    period: str = Field(..., description="Period of anomalous occurrence", example="August 2026")
    value: float = Field(..., description="Observed anomalous metric value", example=430000.0)
    baseline: float = Field(..., description="Benchmark expected value", example=89326.0)
    change_percent: float = Field(..., description="Percentage departure from baseline", example=381.4)
    anomaly: bool = Field(True, description="Flag confirming anomaly detection", example=True)
    severity: str = Field("HIGH", description="Severity classification: HIGH, MEDIUM, LOW", example="HIGH")

class BusinessInsightItem(BaseModel):
    """Grounded business insight synthesized from enterprise telemetry."""
    id: str = Field(..., description="Unique insight tracking code", example="INS-01")
    title: str = Field(..., description="Headline insight summary", example="August Operating Margin Contraction")
    summary: str = Field(..., description="Comprehensive insight description grounded in data")
    domain: str = Field(..., description="Business domain (Finance, Sales, Inventory, HR, CRM)", example="Finance")
    impact: str = Field("MEDIUM", description="Assessed business impact rating", example="HIGH")
    evidence_metric: Optional[str] = Field(None, description="Supporting mathematical metric proof", example="Net Profit dropped by 50%")
    recommendation: Optional[str] = Field(None, description="Actionable recommendation to address insight")

class ActionableRecommendation(BaseModel):
    """Targeted actionable recommendation synthesized by business agents."""
    title: str = Field(..., description="Recommendation action title", example="Emergency Freight Cost Controls")
    reason: str = Field(..., description="Underlying business justification grounded in telemetry")
    priority: str = Field("HIGH", description="Execution priority: HIGH, MEDIUM, LOW", example="HIGH")
    related_domain: str = Field(..., description="Business operational domain", example="Finance")
    suggested_action: str = Field(..., description="Specific operational action recommended for leadership")

class DataSourceCitation(BaseModel):
    """Data provenance citation identifying tables and columns used to generate answer."""
    table: str = Field(..., description="Database table consulted via read-only MCP access", example="company_financials")
    columns: List[str] = Field(default_factory=list, description="Table columns queried", example=["month_name", "net_profit", "cogs", "operating_expenses"])
    purpose: Optional[str] = Field(None, description="Analytical purpose of consulting this table", example="Compute monthly net profit and margin changes")

class AnalyticsQueryResponse(BaseModel):
    """Comprehensive analytics response returned by the LangGraph multi-agent pipeline."""
    success: bool = Field(..., description="Indicates whether query completed successfully without errors", example=True)
    question: str = Field(..., description="The original natural-language question processed", example="Why did profit decrease in August?")
    answer: str = Field(..., description="Grounded executive answer synthesized from database query results")
    data: AnalyticsDataPayload = Field(..., description="Structured tabular result payload returned from read-only MCP database tool")
    intent: Dict[str, Any] = Field(default_factory=dict, description="Classified intent, domains, and analytical requirements")
    sources: List[Union[DataSourceCitation, Dict[str, Any], str]] = Field(default_factory=list, description="Provenance citations for tables consulted")
    columns_used: List[str] = Field(default_factory=list, description="Columns referenced in SQL execution", example=["net_profit", "cogs", "expenses"])
    visualization_hint: Union[VisualizationHintModel, Dict[str, Any], str] = Field(default="table", description="Frontend charting hint (chart type, axes, title)")
    error: Optional[str] = Field(None, description="Error explanation if execution failed or access was denied", example=None)
    user_role: str = Field(..., description="Role of the authenticated requesting user", example="CEO")
    user_name: str = Field(..., description="Full display name of the requesting user", example="Vikram Malhotra")
    timestamp: datetime = Field(default_factory=get_current_ist, description="IST timestamp of response generation")
    # Advanced Agentic Intelligence
    investigation_plan: Optional[InvestigationPlan] = Field(None, description="Investigation plan formulated by multi-agent planner")
    root_cause_analysis: Optional[RootCauseAnalysis] = Field(None, description="Detailed causal decomposition for profit, margin, or cost variance inquiries")
    comparisons: Optional[List[ComparisonMetric]] = Field(None, description="Period-over-period variance metrics")
    trends: Optional[TrendSummary] = Field(None, description="Directional trend analysis")
    anomalies: Optional[List[AnomalyItem]] = Field(None, description="Detected statistical anomalies")
    insights: Optional[List[BusinessInsightItem]] = Field(default_factory=list, description="Grounded business insights")
    recommendations: Optional[List[ActionableRecommendation]] = Field(default_factory=list, description="Actionable business recommendations")
    confidence: Optional[str] = Field("HIGH", description="Confidence level of generated response (HIGH, MEDIUM, LOW)", example="HIGH")

class DashboardKPICard(BaseModel):
    """Executive KPI card summary data."""
    title: str = Field(..., description="Metric card title", example="Total Revenue")
    value: str = Field(..., description="Formatted metric value", example="₹14.82Cr")
    change: str = Field(..., description="Period-over-period percentage growth", example="+12.4%")
    isPositive: bool = Field(..., description="Flag indicating if change direction is favorable", example=True)
    periodText: str = Field(..., description="Comparison period context label", example="vs previous period")

class SalesTrendPoint(BaseModel):
    """Monthly historical sales velocity data point."""
    month: str = Field(..., description="Month and year label", example="Aug 26")
    revenue: float = Field(..., description="Total monthly gross sales revenue", example=12450000.0)
    orders: int = Field(..., description="Total number of completed sales orders", example=1420)

class CategoryPoint(BaseModel):
    """Product category sales distribution point."""
    name: str = Field(..., description="Product category name", example="Fresh Produce")
    value: float = Field(..., description="Gross category revenue", example=4820000.0)
    color: str = Field(..., description="Hex color code for dashboard chart palette", example="#10B981")

class TopProductPoint(BaseModel):
    """Top-selling product performance and warehouse inventory balance."""
    id: str = Field(..., description="Product SKU code", example="P001")
    name: str = Field(..., description="Product display name", example="Organic Alphonso Mangoes")
    category: str = Field(..., description="Product category", example="Fresh Produce")
    revenue: float = Field(..., description="Total product gross revenue", example=1850000.0)
    orders: int = Field(..., description="Quantity ordered", example=450)
    growth: str = Field(..., description="Period revenue growth rate", example="+18.4%")
    stock: int = Field(..., description="Current warehouse quantity on hand", example=42)

class DashboardInsight(BaseModel):
    """Telemetry-grounded insight displayed on executive dashboard."""
    id: str = Field(..., description="Unique insight identifier", example="INS-01")
    title: str = Field(..., description="Executive summary title", example="Consistent Sales Velocity")
    description: str = Field(..., description="Detailed description of the observation")
    category: str = Field(..., description="Business category domain", example="Sales")
    impact: str = Field(..., description="Assessed impact (high, medium, low)", example="high")
    date: str = Field(..., description="Telemetry source or audit tag", example="Live Telemetry")
    source: str = Field(..., description="Underlying database tables", example="sales_orders, sales_order_items")

class DashboardResponse(BaseModel):
    """Deterministic executive dashboard payload queried directly from FreshMart MySQL."""
    range: str = Field("12m", description="Date range filter applied (today, 7d, 30d, 90d, 12m)", example="12m")
    kpis: List[DashboardKPICard] = Field(..., description="Executive top-line KPI cards")
    sales_trend: List[SalesTrendPoint] = Field(..., description="Historical sales revenue and order counts trend")
    category_distribution: List[CategoryPoint] = Field(..., description="Product category sales revenue distribution")
    top_products: List[TopProductPoint] = Field(..., description="Top performing SKUs with inventory stock balances")
    insights: List[DashboardInsight] = Field(..., description="Live grounded executive insights and alerts")

class RoleDashboardResponse(BaseModel):
    """Role-scoped enterprise dashboard payload queried directly from FreshMart MySQL with server-side RBAC."""
    role: str = Field(..., description="Role of the authenticated dashboard", example="SALES_MANAGER")
    role_title: str = Field(..., description="Human-readable title of role", example="Sales & Commercial Operations")
    scope_badge: str = Field(..., description="Scope descriptor badge", example="Sales & CRM Scope")
    range: str = Field("12m", description="Date range filter applied", example="12m")
    kpis: List[DashboardKPICard] = Field(default_factory=list, description="Top-line KPI cards for this role")
    sales_trend: Optional[List[SalesTrendPoint]] = Field(default=None, description="Sales velocity trend")
    financial_trend: Optional[List[Dict[str, Any]]] = Field(default=None, description="Monthly P&L trend (revenue, expenses, profit)")
    category_distribution: Optional[List[CategoryPoint]] = Field(default=None, description="Category distribution")
    top_products: Optional[List[TopProductPoint]] = Field(default=None, description="Top selling products")
    top_customers: Optional[List[Dict[str, Any]]] = Field(default=None, description="Top B2B customers by spend")
    crm_pipeline: Optional[List[Dict[str, Any]]] = Field(default=None, description="CRM lead status pipeline distribution")
    department_summary: Optional[List[Dict[str, Any]]] = Field(default=None, description="HR Department headcounts and compensation averages")
    low_stock_items: Optional[List[Dict[str, Any]]] = Field(default=None, description="Inventory low-stock critical items")
    top_suppliers: Optional[List[Dict[str, Any]]] = Field(default=None, description="Suppliers ranked by PO order spend")
    expense_breakdown: Optional[List[Dict[str, Any]]] = Field(default=None, description="Operating expense breakdown")
    root_cause_highlight: Optional[Dict[str, Any]] = Field(default=None, description="August profit drop root-cause highlight")
    insights: List[DashboardInsight] = Field(default_factory=list, description="Domain-specific grounded insights")


class EnterpriseInsightCard(BaseModel):
    """Card representing an enterprise insight on the insights dashboard."""
    id: str = Field(..., description="Unique insight tracking identifier", example="INS-FIN-01")
    category: str = Field(..., description="Business category domain", example="Financial Insights")
    title: str = Field(..., description="Executive headline", example="August 2026 Margin Contraction")
    summary: str = Field(..., description="Detailed narrative explanation grounded in ledger telemetry")
    metric: str = Field(..., description="Primary headline metric", example="Net Profit: ₹600,000")
    change: str = Field(..., description="Period-over-period percentage or absolute delta", example="-50.0%")
    impact: str = Field("MEDIUM", description="Business impact level (HIGH, MEDIUM, LOW)", example="HIGH")
    evidence: str = Field(..., description="Source database tables or columns proving this insight", example="company_financials")
    recommendation: str = Field(..., description="Strategic or operational recommendation to address the finding")

class EnterpriseAnomalyCard(BaseModel):
    """Statistical anomaly card detected across business metrics."""
    metric: str = Field(..., description="Name of the anomalous metric", example="Emergency Shipping Expense")
    period: str = Field(..., description="Time period where anomaly occurred", example="August 2026")
    value: float = Field(..., description="Observed anomalous metric value", example=430000.0)
    baseline: float = Field(..., description="Normal baseline benchmark value", example=89326.0)
    change_percent: float = Field(..., description="Percentage departure from baseline", example=381.4)
    anomaly: bool = Field(True, description="Boolean flag confirming anomalous deviation", example=True)
    severity: str = Field("HIGH", description="Anomaly severity rating (HIGH, MEDIUM, LOW)", example="HIGH")

class EnterpriseInsightsResponse(BaseModel):
    """Structured enterprise insights, anomalies, and recommendations grounded in MySQL ledger data."""
    success: bool = Field(True, description="Query execution status", example=True)
    insights: List[EnterpriseInsightCard] = Field(..., description="List of synthesized enterprise insights")
    anomalies: List[EnterpriseAnomalyCard] = Field(default_factory=list, description="List of detected business anomalies")
    timestamp: datetime = Field(default_factory=get_current_ist, description="IST timestamp of telemetry calculation")
