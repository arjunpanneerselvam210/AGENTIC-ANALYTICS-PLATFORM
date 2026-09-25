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
    Validates generated SQL against security rules for the target database.
    If valid, sets is_sql_valid = True and validated_sql = generated_sql.
    Otherwise sets is_sql_valid = False and records sql_error.
    """
    sql = (state.get("generated_sql") or "").strip()
    target_db = state.get("target_database", "company_analytics")
    logger.info(f"Validating SQL for target DB '{target_db}': {sql[:100]}...")

    is_valid, error_msg = validate_sql_security(sql, target_database=target_db)
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
