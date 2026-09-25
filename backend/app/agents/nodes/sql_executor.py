"""
Node: MCP SQL Executor
Executes validated SQL strictly through Model Context Protocol `execute_read_only_sql` tool.
Does NOT create any direct database connections from LangGraph.
"""

import logging
from app.agents.state import AnalyticsState
from app.agents.mcp_client import mcp_client

logger = logging.getLogger("agents.sql_executor")

def execute_sql_node(state: AnalyticsState) -> AnalyticsState:
    """
    Calls MCP tool `execute_read_only_sql` with validated SQL.
    Records structured query results or execution error.
    """
    sql = state.get("validated_sql", "")
    logger.info(f"Executing SQL via MCP: {sql[:100]}...")

    res = mcp_client.execute_read_only_sql(sql)
    if not res.get("success"):
        err_msg = res.get("error", "MCP query execution failed.")
        logger.warning(f"MCP execution returned error: {err_msg}")
        return {
            "query_result": {},
            "result_valid": False,
            "sql_error": err_msg,
            "last_error": err_msg
        }

    logger.info(f"MCP query execution succeeded. Returned {res.get('row_count', 0)} rows.")
    return {
        "query_result": res,
        "result_valid": True,
        "sql_error": None
    }
