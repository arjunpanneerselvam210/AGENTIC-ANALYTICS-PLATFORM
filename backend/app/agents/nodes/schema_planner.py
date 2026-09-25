"""
Node: Schema Planner & MCP Schema Discovery
Uses MCP `list_tables` and `describe_table` to retrieve targeted schema definitions
for relevant tables, avoiding context window clutter.
"""

import logging
from typing import Dict, Any, List
from app.agents.state import AnalyticsState
from app.agents.mcp_client import mcp_client

logger = logging.getLogger("agents.schema_planner")

def plan_schema_node(state: AnalyticsState) -> AnalyticsState:
    """
    Step 1: Discover available tables via MCP `list_tables`.
    Cross-checks candidate tables against active database tables.
    """
    all_tables = mcp_client.list_tables()
    logger.info(f"Discovered {len(all_tables)} tables via MCP list_tables")

    candidate_tables = state.get("required_tables", [])
    valid_tables = [t for t in candidate_tables if t in all_tables]

    # If candidate tables specified, ensure salaries is included if question involves compensation
    q_lower = state.get("original_question", "").lower()
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

    return {
        "available_tables": all_tables,
        "required_tables": valid_tables
    }

def discover_schema_node(state: AnalyticsState) -> AnalyticsState:
    """
    Step 2: Inspect schemas of the required tables using MCP `describe_table`.
    Builds a formatted schema context with column definitions, data types, PKs, and FKs.
    """
    tables_to_inspect = state.get("required_tables", [])
    logger.info(f"Inspecting schemas via MCP describe_table for: {tables_to_inspect}")

    schema_details: Dict[str, Any] = {}
    formatted_context_lines: List[str] = []

    for tbl in tables_to_inspect:
        desc = mcp_client.describe_table(tbl)
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
            logger.warning(f"Failed to describe table '{tbl}': {desc.get('error')}")

    schema_text = "\n".join(formatted_context_lines)
    return {
        "schema_context": {
            "tables": schema_details,
            "formatted_text": schema_text
        }
    }
