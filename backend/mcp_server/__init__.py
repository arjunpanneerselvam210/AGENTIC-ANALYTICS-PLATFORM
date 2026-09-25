"""
FreshMart MCP Database Server Package
Provides Model Context Protocol tools for controlled, safe, read-only
database introspection and analytics query execution over FreshMart MySQL.
"""

from mcp_server.server import (
    mcp_server,
    list_tables_tool,
    describe_table_tool,
    execute_read_only_sql_tool,
    execute_tool_directly
)

__all__ = [
    "mcp_server",
    "list_tables_tool",
    "describe_table_tool",
    "execute_read_only_sql_tool",
    "execute_tool_directly"
]
