"""
FreshMart MCP Database Server
Exposes standardized Model Context Protocol tools for AI agents:
1. list_tables: Discover available business tables dynamically.
2. describe_table: Inspect columns, data types, primary keys, and foreign keys.
3. execute_read_only_sql: Safely validate and run analytical read-only SQL queries.
"""

import sys
import os
import asyncio
import logging
from typing import Dict, Any, Optional

# Ensure backend root is on sys.path
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from mcp.server.mcpserver import MCPServer
from app.core.config import settings
from mcp_server.tools.schema_tools import list_tables as _list_tables_impl
from mcp_server.tools.schema_tools import describe_table as _describe_table_impl
from mcp_server.tools.sql_tools import execute_read_only_sql as _execute_read_only_sql_impl

# Setup logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("mcp_server")

# Instantiate official MCP Server
mcp_server = MCPServer(name=settings.MCP_SERVER_NAME)

# ------------------------------------------------------------------------------
# Tool 1: list_tables
# ------------------------------------------------------------------------------
@mcp_server.tool(
    name="list_tables",
    description="Returns a list of all accessible business tables and views in the FreshMart database."
)
def list_tables_tool() -> Dict[str, Any]:
    """
    Discovers all available FreshMart tables.
    Returns:
        JSON object containing the list of accessible tables and count.
    """
    return _list_tables_impl()

# ------------------------------------------------------------------------------
# Tool 2: describe_table
# ------------------------------------------------------------------------------
@mcp_server.tool(
    name="describe_table",
    description="Returns detailed column specifications, data types, primary keys, and foreign keys for a specified FreshMart table."
)
def describe_table_tool(table_name: str) -> Dict[str, Any]:
    """
    Introspects table schema and relationships.
    Args:
        table_name: Name of the table to describe (e.g., 'employees', 'products', 'sales_orders').
    Returns:
        JSON object containing column definitions and foreign key constraints.
    """
    return _describe_table_impl(table_name)

# ------------------------------------------------------------------------------
# Tool 3: execute_read_only_sql
# ------------------------------------------------------------------------------
@mcp_server.tool(
    name="execute_read_only_sql",
    description="Safely executes a read-only analytical SQL query (SELECT or WITH ... SELECT) against FreshMart MySQL database."
)
def execute_read_only_sql_tool(sql: str, limit: Optional[int] = None) -> Dict[str, Any]:
    """
    Executes a safe read-only SQL query with security validation and row limits.
    Args:
        sql: The SQL query to execute. Only SELECT queries are permitted.
        limit: Optional maximum number of rows to return (capped by MCP_MAX_RESULT_ROWS).
    Returns:
        JSON object containing columns, rows, row count, and truncation indicator.
    """
    return _execute_read_only_sql_impl(sql, limit=limit)

# ------------------------------------------------------------------------------
# Direct In-Process Dispatcher for LangGraph Agents & Testing
# ------------------------------------------------------------------------------
def execute_tool_directly(tool_name: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Allows in-process execution of MCP tools without spawning an external subprocess.
    Directly used by LangGraph multi-agent nodes and automated unit tests.
    """
    args = arguments or {}
    if tool_name == "list_tables":
        return list_tables_tool()
    elif tool_name == "describe_table":
        table_name = args.get("table_name", "")
        return describe_table_tool(table_name)
    elif tool_name == "execute_read_only_sql":
        sql = args.get("sql", "")
        limit = args.get("limit")
        return execute_read_only_sql_tool(sql, limit=limit)
    else:
        return {
            "success": False,
            "error": f"Unknown MCP tool '{tool_name}'. Available tools: list_tables, describe_table, execute_read_only_sql"
        }

# ------------------------------------------------------------------------------
# Entrypoint for Standard MCP Stdio Transport
# ------------------------------------------------------------------------------
async def run_server():
    logger.info(f"Starting FreshMart MCP Database Server '{settings.MCP_SERVER_NAME}' on stdio transport...")
    await mcp_server.run_stdio_async()

if __name__ == "__main__":
    asyncio.run(run_server())
