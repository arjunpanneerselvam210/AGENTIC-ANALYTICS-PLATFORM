"""
Node: SQL Validator
Validates the generated SQL using the Phase 6 security validation layer.
Checks single statement, read-only SELECT type, and blocks all forbidden keywords.
"""

import logging
from app.agents.state import AnalyticsState
from mcp_server.utils.sql_validator import validate_sql_security

logger = logging.getLogger("agents.sql_validator")

def validate_sql_node(state: AnalyticsState) -> AnalyticsState:
    """
    Validates generated SQL against security rules.
    If valid, sets is_sql_valid = True and validated_sql = generated_sql.
    Otherwise sets is_sql_valid = False and records sql_error.
    """
    sql = (state.get("generated_sql") or "").strip()
    logger.info(f"Validating SQL: {sql[:100]}...")

    is_valid, error_msg = validate_sql_security(sql)
    if not is_valid:
        logger.warning(f"SQL security validation failed: {error_msg}")
        return {
            "is_sql_valid": False,
            "sql_error": error_msg,
            "last_error": error_msg
        }

    logger.info("SQL security validation passed.")
    return {
        "is_sql_valid": True,
        "validated_sql": sql,
        "sql_error": None
    }
