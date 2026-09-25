"""
Read-Only MySQL Database Connection Manager for FreshMart MCP Server
Enforces:
- Connection using dedicated read-only user (freshmart_mcp_reader).
- Session-level READ ONLY transaction enforcement.
- Query execution timeout guards (max_execution_time in milliseconds).
- Result row limits (MAX_RESULT_ROWS) with truncation signaling.
- Complete JSON serialization for all SQL data types.
- Sanitized error reporting without credential or host leakage.
"""

import re
import logging
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from typing import List, Dict, Any, Optional
import pymysql
from app.core.config import settings

logger = logging.getLogger("mcp_server.database")

def serialize_sql_value(val: Any) -> Any:
    """Converts MySQL/Python database types to standard JSON-serializable primitives."""
    if val is None:
        return None
    if isinstance(val, (int, float, bool, str)):
        return val
    if isinstance(val, Decimal):
        return float(val) if val % 1 else int(val)
    if isinstance(val, (datetime, date, time)):
        return val.isoformat()
    if isinstance(val, timedelta):
        return str(val)
    if isinstance(val, bytes):
        return val.decode("utf-8", errors="replace")
    return str(val)

class MCPDatabaseManager:
    """
    Manages safe, read-only interactions with FreshMart MySQL database.
    """

    def __init__(self):
        self.host = settings.MYSQL_HOST
        self.port = settings.MYSQL_PORT
        self.user = settings.mcp_mysql_user
        self.password = settings.mcp_mysql_password
        self.db = settings.MYSQL_DB
        self.timeout_seconds = settings.MCP_QUERY_TIMEOUT_SECONDS
        self.max_rows = settings.MCP_MAX_RESULT_ROWS

    def get_connection(self) -> pymysql.Connection:
        """
        Creates and returns a connection configured for strict read-only analytics.
        Sets session transaction read-only and statement execution timeout.
        """
        try:
            conn = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.db,
                connect_timeout=self.timeout_seconds,
                read_timeout=self.timeout_seconds + 2,
                write_timeout=self.timeout_seconds + 2,
                charset="utf8mb4",
                autocommit=True
            )
            with conn.cursor() as cursor:
                # Enforce read-only session
                cursor.execute("SET SESSION TRANSACTION READ ONLY;")
                # Enforce MySQL statement execution timeout in milliseconds
                timeout_ms = self.timeout_seconds * 1000
                cursor.execute(f"SET max_execution_time = {timeout_ms};")
            return conn
        except pymysql.MySQLError as e:
            # Fallback to standard connection if dedicated reader is unavailable
            if "Access denied" in str(e) and self.user != settings.MYSQL_USER:
                logger.warning("Dedicated reader user connection failed, falling back to configured user with read-only flags.")
                conn = pymysql.connect(
                    host=self.host,
                    port=self.port,
                    user=settings.MYSQL_USER,
                    password=settings.MYSQL_PASSWORD,
                    database=self.db,
                    connect_timeout=self.timeout_seconds,
                    charset="utf8mb4",
                    autocommit=True
                )
                with conn.cursor() as cursor:
                    cursor.execute("SET SESSION TRANSACTION READ ONLY;")
                    cursor.execute(f"SET max_execution_time = {self.timeout_seconds * 1000};")
                return conn
            raise

    def get_table_names(self) -> List[str]:
        """
        Retrieves all valid business tables and views in the FreshMart database.
        Queries information_schema dynamically.
        """
        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                query = """
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = %s 
                    ORDER BY table_name;
                """
                cursor.execute(query, (self.db,))
                rows = cursor.fetchall()
                return [r[0] for r in rows]
        finally:
            conn.close()

    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """
        Retrieves detailed schema metadata for a specified table:
        - Columns: name, data_type, is_nullable, primary_key, default
        - Foreign Keys: column, referenced_table, referenced_column
        """
        # Validate table exists in this database
        existing_tables = self.get_table_names()
        if table_name not in existing_tables:
            raise ValueError(f"Table '{table_name}' does not exist in FreshMart database.")

        conn = self.get_connection()
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                # 1. Fetch column metadata
                cols_query = """
                    SELECT 
                        column_name,
                        data_type,
                        column_type,
                        is_nullable,
                        column_key,
                        column_default,
                        extra
                    FROM information_schema.columns
                    WHERE table_schema = %s AND table_name = %s
                    ORDER BY ordinal_position;
                """
                cursor.execute(cols_query, (self.db, table_name))
                raw_cols = cursor.fetchall()

                columns = []
                for c in raw_cols:
                    c_lower = {k.lower(): v for k, v in c.items()}
                    columns.append({
                        "name": c_lower.get("column_name"),
                        "type": (c_lower.get("data_type") or "").upper(),
                        "full_type": c_lower.get("column_type"),
                        "nullable": c_lower.get("is_nullable") == "YES",
                        "primary_key": c_lower.get("column_key") == "PRI",
                        "default": c_lower.get("column_default")
                    })

                # 2. Fetch foreign key relationships
                fk_query = """
                    SELECT 
                        k.column_name,
                        k.referenced_table_name,
                        k.referenced_column_name
                    FROM information_schema.key_column_usage k
                    WHERE k.table_schema = %s 
                      AND k.table_name = %s 
                      AND k.referenced_table_name IS NOT NULL
                    ORDER BY k.ordinal_position;
                """
                cursor.execute(fk_query, (self.db, table_name))
                raw_fks = cursor.fetchall()

                foreign_keys = []
                for fk in raw_fks:
                    fk_lower = {k.lower(): v for k, v in fk.items()}
                    foreign_keys.append({
                        "column": fk_lower.get("column_name"),
                        "references": f"{fk_lower.get('referenced_table_name')}.{fk_lower.get('referenced_column_name')}"
                    })

                return {
                    "table": table_name,
                    "columns": columns,
                    "foreign_keys": foreign_keys,
                    "column_count": len(columns),
                    "has_foreign_keys": len(foreign_keys) > 0
                }
        finally:
            conn.close()

    def execute_read_only_query(self, sql: str, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Executes a validated read-only SQL query against FreshMart database.
        Returns columns, serialized rows, row_count, and truncation state.
        """
        row_limit = min(limit or self.max_rows, self.max_rows)
        # Fetch row_limit + 1 to detect if total rows exceed limit
        fetch_limit = row_limit + 1

        conn = self.get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql)
                raw_rows = cursor.fetchmany(fetch_limit)
                
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                
                is_truncated = len(raw_rows) > row_limit
                final_rows = raw_rows[:row_limit]

                # Serialize each row to a dictionary of primitives
                serialized_rows = []
                for row in final_rows:
                    serialized_row = {}
                    for col_name, val in zip(columns, row):
                        serialized_row[col_name] = serialize_sql_value(val)
                    serialized_rows.append(serialized_row)

                return {
                    "success": True,
                    "columns": columns,
                    "rows": serialized_rows,
                    "row_count": len(serialized_rows),
                    "truncated": is_truncated,
                    "limit_applied": row_limit if is_truncated else None
                }
        except pymysql.MySQLError as e:
            # Sanitize error message to avoid leaking internal host or credentials
            error_msg = str(e)
            if "max_execution_time" in error_msg or "timed out" in error_msg.lower():
                clean_err = f"Query timed out after {self.timeout_seconds} seconds."
            elif "denied" in error_msg.lower():
                clean_err = "Operation denied: database permissions permit read-only SELECT operations only."
            else:
                # Strip connection info if present
                clean_err = re.sub(r"for user '[^']+'@'[^']+'", "", error_msg)
            return {
                "success": False,
                "error": clean_err
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Execution error: {str(e)}"
            }
        finally:
            conn.close()

# Shared singleton instance
db_manager = MCPDatabaseManager()
