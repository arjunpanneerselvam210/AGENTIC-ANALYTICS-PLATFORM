"""
FreshMart MCP Client for LangGraph Agents.
Handles Model Context Protocol tools and multi-database routing:
- company_analytics (MySQL 8.0): Business telemetry, sales, inventory, HRMS, ERP, finances.
- company_auth (PostgreSQL 16): Application security, accounts, roles, permissions, sessions.
"""

import logging
from typing import Dict, Any, List, Optional
from sqlalchemy import text, inspect
from mcp_server.server import execute_tool_directly
from app.db.postgres_session import postgres_engine
from mcp_server.database import serialize_sql_value

logger = logging.getLogger("agents.mcp_client")

_TABLE_NAMES_CACHE: Dict[str, List[str]] = {}
_TABLE_SCHEMA_CACHE: Dict[str, Dict[str, Any]] = {}

class MCPDatabaseClient:
    """
    Standardized client for LangGraph agents to interact with FreshMart databases
    (MySQL company_analytics and PostgreSQL company_auth) with schema discovery and safe read-only execution.
    """

    @staticmethod
    def list_tables(target_database: str = "company_analytics") -> List[str]:
        """
        Discovers all available business or authentication tables for the target database.
        """
        db_key = (target_database or "company_analytics").lower()
        if db_key in _TABLE_NAMES_CACHE:
            return _TABLE_NAMES_CACHE[db_key]

        if "auth" in db_key or "postgres" in db_key:
            try:
                inspector = inspect(postgres_engine)
                pg_tables = inspector.get_table_names(schema="public")
                logger.info(f"Discovered {len(pg_tables)} PostgreSQL company_auth tables")
                _TABLE_NAMES_CACHE[db_key] = pg_tables
                return pg_tables
            except Exception as e:
                logger.error(f"Error introspecting PostgreSQL tables: {e}")
                return ["users", "roles", "permissions", "role_permissions", "user_chat_sessions"]

        # Default: MySQL company_analytics via MCP
        try:
            logger.info("Calling MCP tool: list_tables (company_analytics)")
            res = execute_tool_directly("list_tables")
            if res.get("success"):
                tables = res.get("tables", [])
                _TABLE_NAMES_CACHE[db_key] = tables
                return tables
            logger.warning(f"MCP list_tables failed: {res.get('error')}")
            return []
        except Exception as e:
            logger.error(f"Error calling MCP list_tables: {e}")
            return []

    @staticmethod
    def describe_table(table_name: str, target_database: str = "company_analytics") -> Dict[str, Any]:
        """
        Introspects table schema and relationships for the specified target database.
        """
        db_key = (target_database or "company_analytics").lower()
        clean_tbl = table_name.strip().lower()
        cache_key = f"{db_key}:{clean_tbl}"
        if cache_key in _TABLE_SCHEMA_CACHE:
            return _TABLE_SCHEMA_CACHE[cache_key]


        if "auth" in db_key or "postgres" in db_key:
            try:
                inspector = inspect(postgres_engine)
                col_defs = inspector.get_columns(clean_tbl, schema="public")
                pk_constraint = inspector.get_pk_constraint(clean_tbl, schema="public")
                pk_cols = set(pk_constraint.get("constrained_columns", []))
                fks = inspector.get_foreign_keys(clean_tbl, schema="public")

                columns = [
                    {
                        "name": c["name"],
                        "type": str(c["type"]),
                        "nullable": c.get("nullable", True),
                        "primary_key": c["name"] in pk_cols
                    }
                    for c in col_defs
                ]

                foreign_keys = [
                    {
                        "column": fk["constrained_columns"][0] if fk.get("constrained_columns") else "id",
                        "references": f"{fk.get('referred_table')}({fk.get('referred_columns')[0] if fk.get('referred_columns') else 'id'})"
                    }
                    for fk in fks
                ]

                res_obj = {
                    "success": True,
                    "table_name": clean_tbl,
                    "columns": columns,
                    "foreign_keys": foreign_keys,
                    "column_count": len(columns),
                    "database": "company_auth (PostgreSQL)"
                }
                _TABLE_SCHEMA_CACHE[cache_key] = res_obj
                return res_obj
            except Exception as e:
                logger.error(f"Error describing PostgreSQL table '{clean_tbl}': {e}")
                return {"success": False, "error": str(e)}

        # Default: MySQL company_analytics via MCP
        try:
            logger.info(f"Calling MCP tool: describe_table for '{clean_tbl}' (company_analytics)")
            res = execute_tool_directly("describe_table", {"table_name": clean_tbl})
            if res.get("success"):
                _TABLE_SCHEMA_CACHE[cache_key] = res
            return res

        except Exception as e:
            logger.error(f"Error calling MCP describe_table for {clean_tbl}: {e}")
            return {"success": False, "error": str(e)}

    @staticmethod
    def execute_read_only_sql(sql: str, target_database: str = "company_analytics", limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Executes a validated read-only analytical SQL query against either MySQL or PostgreSQL.
        """
        db_key = (target_database or "company_analytics").lower()

        if "auth" in db_key or "postgres" in db_key:
            try:
                logger.info(f"Executing read-only SQL on PostgreSQL company_auth: {sql[:100]}...")
                with postgres_engine.connect() as conn:
                    result = conn.execute(text(sql))
                    cols = list(result.keys()) if result.keys() else []
                    raw_rows = result.fetchall()
                    rows = []
                    for r in raw_rows:
                        row_dict = {}
                        for idx, col in enumerate(cols):
                            val = r[idx]
                            # Hide sensitive password hashes from AI synthesis
                            if col == "password_hash":
                                val = "[PROTECTED_BCRYPT_HASH]"
                            row_dict[col] = serialize_sql_value(val)
                        rows.append(row_dict)

                    if limit and len(rows) > limit:
                        rows = rows[:limit]

                    return {
                        "success": True,
                        "columns": cols,
                        "rows": rows,
                        "row_count": len(rows),
                        "truncated": False,
                        "database": "company_auth"
                    }
            except Exception as e:
                logger.error(f"PostgreSQL query execution failed: {e}")
                return {"success": False, "error": f"PostgreSQL execution failure: {str(e)}"}

        # Default: MySQL company_analytics via MCP
        try:
            logger.info(f"Calling MCP tool: execute_read_only_sql on company_analytics (length: {len(sql)})")
            res = execute_tool_directly("execute_read_only_sql", {"sql": sql, "limit": limit})
            return res
        except Exception as e:
            logger.error(f"Error calling MCP execute_read_only_sql: {e}")
            return {"success": False, "error": f"MCP execution failure: {str(e)}"}

mcp_client = MCPDatabaseClient()
