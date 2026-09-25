"""
MCP Schema Introspection Tools for FreshMart Database
Implements:
- list_tables: Dynamic discovery of accessible business tables.
- describe_table: Deep structural introspection of columns, data types, primary keys, and foreign keys.
"""

import logging
from typing import Dict, Any, List
from mcp_server.database import db_manager

logger = logging.getLogger("mcp_server.tools.schema")

def list_tables() -> Dict[str, Any]:
    """
    List all available business tables and views in the FreshMart database.

    Returns:
        JSON object containing the list of accessible tables and total count.
    """
    try:
        tables = db_manager.get_table_names()
        logger.info(f"list_tables called: discovered {len(tables)} tables")
        return {
            "success": True,
            "tables": tables,
            "table_count": len(tables)
        }
    except Exception as e:
        logger.error(f"Error in list_tables: {e}")
        return {
            "success": False,
            "error": f"Failed to retrieve tables: {str(e)}"
        }

def describe_table(table_name: str) -> Dict[str, Any]:
    """
    Retrieve structural schema details for a specific FreshMart business table.

    Args:
        table_name: Name of the table to inspect (e.g. 'employees', 'products', 'sales_orders').

    Returns:
        JSON object with column definitions, data types, primary keys, and foreign keys.
    """
    if not table_name or not isinstance(table_name, str):
        return {
            "success": False,
            "error": "table_name must be a non-empty string."
        }

    clean_table_name = table_name.strip().lower()

    try:
        schema_info = db_manager.get_table_schema(clean_table_name)
        logger.info(f"describe_table called for '{clean_table_name}': {schema_info['column_count']} columns")
        return {
            "success": True,
            **schema_info
        }
    except ValueError as e:
        logger.warning(f"describe_table requested invalid table '{table_name}': {e}")
        return {
            "success": False,
            "error": str(e)
        }
    except Exception as e:
        logger.error(f"Error describing table '{table_name}': {e}")
        return {
            "success": False,
            "error": f"Failed to describe table '{table_name}': {str(e)}"
        }
