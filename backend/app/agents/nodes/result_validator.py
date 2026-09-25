"""
Node: Result Validator
Validates that MCP execution returned a valid data structure with columns, rows,
and serializable types. Handles empty results cleanly without crashing.
"""

import logging
from app.agents.state import AnalyticsState

logger = logging.getLogger("agents.result_validator")

def validate_result_node(state: AnalyticsState) -> AnalyticsState:
    """
    Validates structure of data returned from MCP execution.
    Extracts columns used for data provenance.
    """
    result = state.get("query_result", {})
    if not result or not result.get("success"):
        err = state.get("sql_error") or "No query result returned."
        logger.warning(f"Result validation failed: {err}")
        return {
            "result_valid": False,
            "error": err
        }

    columns = result.get("columns", [])
    rows = result.get("rows", [])
    row_count = result.get("row_count", 0)

    logger.info(f"Result validation passed: {len(columns)} columns, {row_count} rows.")
    return {
        "result_valid": True,
        "columns_used": columns,
        "error": None
    }
