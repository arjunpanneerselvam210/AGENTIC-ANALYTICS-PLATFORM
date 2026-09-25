"""
MCP SQL Execution Tool for FreshMart Database
Implements:
- execute_read_only_sql: Safely validates and executes read-only analytical SQL queries.
"""

import logging
from typing import Dict, Any, Optional
from mcp_server.utils.sql_validator import SQLValidator
from mcp_server.database import db_manager
from app.core.config import settings

logger = logging.getLogger("mcp_server.tools.sql")
validator = SQLValidator(max_sql_length=settings.MCP_MAX_SQL_LENGTH)

def execute_read_only_sql(sql: str, limit: Optional[int] = None) -> Dict[str, Any]:
    """
    Safely executes a read-only analytical SQL query against the FreshMart MySQL database.

    Security Rules:
    - Only SELECT, WITH ... SELECT, and EXPLAIN SELECT queries are permitted.
    - Any destructive or mutating SQL (INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE) is strictly rejected.
    - Batch chaining and multiple SQL statements separated by semicolons are strictly rejected.
    - File export/import operations (INTO OUTFILE) and locking clauses (FOR UPDATE) are forbidden.

    Args:
        sql: The SQL query to execute.
        limit: Optional maximum number of rows to return (capped by MCP_MAX_RESULT_ROWS).

    Returns:
        Structured JSON object:
        {
            "success": True,
            "columns": ["dept_name", "employee_count"],
            "rows": [{"dept_name": "Sales", "employee_count": 86}, ...],
            "row_count": 10,
            "truncated": False
        }
        Or on validation or execution failure:
        {
            "success": False,
            "error": "Error message describing why the query could not be executed"
        }
    """
    if not sql or not isinstance(sql, str):
        return {
            "success": False,
            "error": "Input 'sql' must be a non-empty string."
        }

    # 1. Server-side security validation
    validation = validator.validate_sql(sql)
    if not validation.is_valid:
        logger.warning(f"SQL query rejected by security validator: {validation.error} | SQL snippet: {sql[:120]}...")
        return {
            "success": False,
            "error": validation.error
        }

    # 2. Execute validated read-only SQL
    sanitized_sql = validation.sanitized_sql
    logger.info(f"Executing read-only SQL ({validation.statement_type}): {sanitized_sql[:100]}...")

    result = db_manager.execute_read_only_query(sanitized_sql, limit=limit)
    if result.get("success"):
        logger.info(f"Query succeeded: returned {result['row_count']} rows (truncated={result['truncated']})")
    else:
        logger.warning(f"Query execution failed: {result.get('error')}")

    return result
