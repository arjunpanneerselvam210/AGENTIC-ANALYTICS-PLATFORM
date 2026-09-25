from typing import TypedDict, List, Dict, Any, Optional, Union

class AnalyticsState(TypedDict, total=False):
    """
    Shared typed state for the FreshMart LangGraph multi-agent analytics pipeline.
    Maintains user identity, RBAC context, schema discovery, generated SQL,
    execution metrics, and analysis reasoning across all graph nodes.
    """
    # 1. User & Authorization Context
    user_id: int
    user_name: str
    role: str
    permissions: List[str]

    # 2. Input & Request Validation
    original_question: str
    conversation_history: List[Dict[str, str]]
    is_valid_request: bool
    validation_error: Optional[str]

    # 3. Intent & Planning
    intent: Dict[str, Any]  # domain, metric, dimension, time_range, operation, filters
    required_domains: List[str]
    required_tables: List[str]
    
    # 4. RBAC Permission Decision
    permission_granted: bool
    missing_permissions: List[str]

    # 5. MCP Schema Discovery
    available_tables: List[str]
    schema_context: Dict[str, Any]  # Table definitions, columns, data types, keys

    # 6. SQL Generation & Validation
    generated_sql: str
    validated_sql: str
    is_sql_valid: bool
    sql_error: Optional[str]

    # 7. MCP Execution & Results
    query_result: Dict[str, Any]  # columns, rows, row_count, truncated
    result_valid: bool
    
    # 8. Retry & Error Tracking
    retry_count: int
    max_retries: int
    last_error: Optional[str]
    error: Optional[str]

    # 9. Analysis & Final Synthesis
    analysis: str
    final_answer: str
    sources: List[Any]  # Discovered/queried tables and structured citations
    columns_used: List[str]
    visualization_hint: Union[str, Dict[str, Any]]  # line_chart, bar_chart, pie_chart, metric_card, table
    success: bool

    # 10. Phase 10: Advanced Agentic Analytics & Evidence Grounding
    investigation_plan: Dict[str, Any]
    metrics: Dict[str, Any]
    comparisons: List[Dict[str, Any]]
    trends: Dict[str, Any]
    anomalies: List[Dict[str, Any]]
    root_cause_analysis: Dict[str, Any]
    insights: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    confidence: str

