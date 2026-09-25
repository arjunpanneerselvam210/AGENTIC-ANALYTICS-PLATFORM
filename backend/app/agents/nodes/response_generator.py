"""
Node: Final Response Generator
Synthesizes the final structured analytics answer, including:
- Direct business answer
- Clean tabular data payload (columns + rows)
- Data provenance citations (tables and columns used)
- Recommended visualization hint
- Comprehensive error handling for access denied or invalid inputs
"""

import logging
from typing import List
from app.agents.state import AnalyticsState

logger = logging.getLogger("agents.response_generator")

def determine_viz_hint(columns: List[str], row_count: int, explicit_hint: str) -> str:
    """
    Infers the optimal frontend chart hint based on data cardinality and dimensions.
    """
    if explicit_hint and explicit_hint not in ["table", ""]:
        return explicit_hint

    if row_count == 1 and len(columns) <= 2:
        return "metric_card"

    col_names_lower = [c.lower() for c in columns]
    if any(k in col_names_lower for k in ["month", "date", "year", "order_date"]):
        return "line_chart"

    if any(k in col_names_lower for k in ["status", "category", "region"]):
        if row_count <= 6:
            return "pie_chart"
        return "bar_chart"

    if any(k in col_names_lower for k in ["department", "dept_name", "product_name", "supplier_name"]):
        return "bar_chart"

    return "table"

def generate_response_node(state: AnalyticsState) -> AnalyticsState:
    """
    Finalizes the state with answer text, structured data, citations, and visualization hint.
    """
    # 1. Check for Pre-Execution Failures (Validation or RBAC)
    if not state.get("is_valid_request", True):
        err = state.get("validation_error") or state.get("error") or "Invalid analytics request."
        logger.info(f"Generating validation error response: {err}")
        return {
            "success": False,
            "final_answer": err,
            "error": err,
            "sources": [],
            "visualization_hint": "table"
        }

    if not state.get("permission_granted", True):
        err = state.get("error") or "Access denied by enterprise RBAC security policy."
        logger.info(f"Generating access-denied response: {err}")
        return {
            "success": False,
            "final_answer": err,
            "error": err,
            "sources": [],
            "visualization_hint": "table"
        }

    # 2. Check for Execution Failures (SQL Syntax, Security, MCP Engine)
    if state.get("sql_error") or not state.get("result_valid", True):
        err = state.get("sql_error") or state.get("error") or "Failed to execute analytical query."
        logger.warning(f"Generating SQL failure response: {err}")
        return {
            "success": False,
            "final_answer": f"Unable to process query: {err}",
            "error": err,
            "sources": state.get("required_tables", []),
            "visualization_hint": "table"
        }

    # 3. Successful Analytics Answer Synthesis
    analysis_text = state.get("analysis", "")
    sources = state.get("required_tables", [])
    query_result = state.get("query_result", {})
    columns = query_result.get("columns", [])
    row_count = query_result.get("row_count", 0)
    raw_hint = state.get("visualization_hint", "")
    viz_hint = determine_viz_hint(columns, row_count, raw_hint)

    # If root-cause analysis was conducted, recommend waterfall/comparison bar visualization
    root_cause = state.get("root_cause_analysis")
    if root_cause and root_cause.get("factors"):
        viz_hint = "bar_chart"

    # Format authoritative answer with provenance citation
    final_answer = analysis_text
    if sources:
        citations = ", ".join(sources)
        if "Data Sources:" not in final_answer:
            final_answer += f"\n\nData Sources: {citations}"

    logger.info("Successfully generated structured analytics response with Phase 10 agentic metadata.")
    return {
        "success": True,
        "final_answer": final_answer,
        "sources": sources,
        "visualization_hint": viz_hint,
        "investigation_plan": state.get("investigation_plan"),
        "root_cause_analysis": root_cause,
        "comparisons": state.get("comparisons"),
        "trends": state.get("trends"),
        "anomalies": state.get("anomalies"),
        "insights": state.get("insights", []),
        "recommendations": state.get("recommendations", []),
        "confidence": state.get("confidence", "HIGH"),
        "error": None
    }

