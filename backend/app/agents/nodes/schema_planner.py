"""
Node: Schema Planner & Multi-Database Schema Discovery
Discovers accessible tables and inspects targeted schemas for both:
- company_analytics (MySQL 8.0)
- company_auth (PostgreSQL 16)
Ensures correct database and schema identification before SQL generation.
"""

import logging
from typing import Dict, Any, List
from app.agents.state import AnalyticsState
from app.agents.mcp_client import mcp_client

logger = logging.getLogger("agents.schema_planner")

def plan_schema_node(state: AnalyticsState) -> AnalyticsState:
    """
    Step 1: Discover available tables via target database introspection.
    Cross-checks candidate tables against target database's catalog.
    """
    target_db = state.get("target_database", "company_analytics")
    all_tables = mcp_client.list_tables(target_database=target_db)
    logger.info(f"Discovered {len(all_tables)} tables in target database '{target_db}'")

    candidate_tables = state.get("required_tables", [])
    valid_tables = [t for t in candidate_tables if t in all_tables]

    q_lower = state.get("original_question", "").lower()

    if "auth" in target_db:
        # PostgreSQL authentication / security domain
        if not valid_tables:
            if any(k in q_lower for k in ["role", "permission", "privilege"]):
                valid_tables = ["roles", "permissions", "role_permissions"]
            elif any(k in q_lower for k in ["session", "chat", "history"]):
                valid_tables = ["user_chat_sessions", "users"]
            else:
                valid_tables = ["users", "roles"]
    else:
        # MySQL company_analytics domain
        # If candidate tables specified, ensure salaries is included if question involves compensation
        if any(k in q_lower for k in ["salary", "salaries", "compensation", "payroll", "wage"]):
            if "salaries" in all_tables and "salaries" not in valid_tables:
                valid_tables.append("salaries")

        # If no candidate tables matched or candidate list was empty, fallback to relevant domain tables
        if not valid_tables:
            intent_domain = state.get("intent", {}).get("domain", "")
            if intent_domain == "SALES":
                valid_tables = ["sales_orders", "sales_order_items", "products"]
            elif intent_domain == "HR":
                if any(k in q_lower for k in ["salary", "salaries", "compensation", "payroll", "wage"]):
                    valid_tables = ["departments", "employees", "salaries"]
                else:
                    valid_tables = ["departments", "employees"]
            elif intent_domain == "CRM":
                valid_tables = ["leads", "customers"]
            elif intent_domain == "INVENTORY":
                valid_tables = ["products", "inventory"]
            elif intent_domain == "PURCHASING":
                valid_tables = ["suppliers", "purchase_orders"]
            elif intent_domain in ["FINANCE", "ROOT_CAUSE"]:
                valid_tables = ["company_financials", "expenses"]
            else:
                valid_tables = ["sales_orders", "products"]

    logger.info(f"Planned tables for {target_db}: {valid_tables}")

    return {
        "available_tables": all_tables,
        "required_tables": valid_tables
    }

def discover_schema_node(state: AnalyticsState) -> AnalyticsState:
    """
    Step 2: Inspect schemas of the required tables for the target database.
    Builds a formatted schema context with column definitions, data types, PKs, and FKs.
    """
    target_db = state.get("target_database", "company_analytics")
    target_schema = state.get("target_schema", target_db)
    tables_to_inspect = state.get("required_tables", [])
    logger.info(f"Inspecting schemas for target DB '{target_db}' on tables: {tables_to_inspect}")

    schema_details: Dict[str, Any] = {}
    dialect = "PostgreSQL 16" if "auth" in target_db else "MySQL 8.0"

    formatted_context_lines: List[str] = [
        f"TARGET DATABASE: {target_db}",
        f"TARGET SCHEMA: {target_schema}",
        f"DATABASE DIALECT: {dialect}",
        f"TABLE SPECIFICATIONS:",
        ""
    ]

    for tbl in tables_to_inspect:
        desc = mcp_client.describe_table(tbl, target_database=target_db)
        if desc.get("success"):
            schema_details[tbl] = desc
            cols = desc.get("columns", [])
            col_strs = [f"{c['name']} ({c['type']}{', PK' if c.get('primary_key') else ''})" for c in cols]
            fks = desc.get("foreign_keys", [])
            fk_strs = [f"{fk.get('column')} -> {fk.get('references')}" for fk in fks if fk.get('references')]

            formatted_context_lines.append(f"TABLE: {tbl}")
            formatted_context_lines.append(f"  Columns: {', '.join(col_strs)}")
            if fk_strs:
                formatted_context_lines.append(f"  Foreign Keys: {', '.join(fk_strs)}")
            formatted_context_lines.append("")
        else:
            logger.warning(f"Failed to describe table '{tbl}' in {target_db}: {desc.get('error')}")

    schema_text = "\n".join(formatted_context_lines)
    return {
        "schema_context": {
            "database": target_db,
            "dialect": dialect,
            "tables": schema_details,
            "formatted_text": schema_text
        }
    }
