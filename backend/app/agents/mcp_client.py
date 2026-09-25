"""
FreshMart MCP Client for LangGraph Agents.
Invokes Model Context Protocol tools without direct database access:
- list_tables
- describe_table
- execute_read_only_sql
"""

import logging
from typing import Dict, Any, List, Optional
from mcp_server.server import execute_tool_directly

logger = logging.getLogger("agents.mcp_client")

class MCPDatabaseClient:
    """
    Standardized client for LangGraph agents to interact with FreshMart MySQL
    strictly via Model Context Protocol tools.
    """

    @staticmethod
    def list_tables() -> List[str]:
        """
        Discovers all available business tables via MCP `list_tables` tool.
        """
        try:
            logger.info("Calling MCP tool: list_tables")
            res = execute_tool_directly("list_tables")
            if res.get("success"):
                return res.get("tables", [])
            logger.warning(f"MCP list_tables failed: {res.get('error')}")
            return []
        except Exception as e:
            logger.error(f"Error calling MCP list_tables: {e}")
            return []

    @staticmethod
    def describe_table(table_name: str) -> Dict[str, Any]:
        """
        Introspects table schema and relationships via MCP `describe_table` tool.
        """
        try:
            logger.info(f"Calling MCP tool: describe_table for '{table_name}'")
            res = execute_tool_directly("describe_table", {"table_name": table_name})
            return res
        except Exception as e:
            logger.error(f"Error calling MCP describe_table for {table_name}: {e}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def execute_read_only_sql(sql: str, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Executes a validated read-only analytical SQL query via MCP `execute_read_only_sql` tool.
        """
        try:
            logger.info(f"Calling MCP tool: execute_read_only_sql (length: {len(sql)})")
            res = execute_tool_directly("execute_read_only_sql", {"sql": sql, "limit": limit})
            return res
        except Exception as e:
            logger.error(f"Error calling MCP execute_read_only_sql: {e}")
            return {"success": False, "error": f"MCP execution failure: {str(e)}"}

mcp_client = MCPDatabaseClient()
