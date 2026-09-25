"""
Node: Intent Classifier & Planner
Analyzes natural language questions, extracts domain, metric, dimension, candidate tables,
and handles conversational context.
"""

import json
import re
import logging
from typing import Dict, Any, List
from app.agents.state import AnalyticsState
from app.agents.prompts import INTENT_SYSTEM_PROMPT
from app.core.llm import ollama_client
from app.core.config import settings

logger = logging.getLogger("agents.intent_classifier")

def rule_based_intent_fallback(question: str) -> Dict[str, Any]:
    """
    High-accuracy heuristic fallback when LLM output is malformed or offline.
    Correctly identifies database (company_analytics vs company_auth) and schema.
    """
    q = question.lower()

    # 0. Application Security, User Accounts & Roles (PostgreSQL company_auth)
    if any(k in q for k in ["user", "users", "role", "roles", "permission", "permissions", "login", "application account", "application login", "provisioned", "rbac", "privilege", "who has access", "chat session"]):
        return {
            "target_database": "company_auth",
            "target_schema": "company_auth",
            "domain": "AUTH_ADMIN",
            "operation": "lookup",
            "metric": "users_and_roles",
            "dimension": "role",
            "time_range": "current",
            "required_domains": ["AUTH_ADMIN"],
            "candidate_tables": ["users", "roles", "permissions", "role_permissions"],
            "visualization_hint": "table"
        }
    
    # 1. Root Cause Analysis (company_analytics)
    if any(k in q for k in ["why did profit", "decrease in august", "drop in august", "profit drop", "root cause", "profit decrease"]):
        return {
            "target_database": "company_analytics",
            "target_schema": "company_analytics",
            "domain": "ROOT_CAUSE",
            "operation": "root_cause_analysis",
            "metric": "net_profit_and_expenses",
            "dimension": "month_and_expense_category",
            "time_range": "August 2026",
            "required_domains": ["FINANCE", "EXPENSES"],
            "candidate_tables": ["company_financials", "expenses"],
            "visualization_hint": "bar_chart"
        }

    # 2. Cross Domain (Sales + Inventory)
    if ("sales" in q or "sold" in q or "revenue" in q) and ("inventory" in q or "stock" in q):
        return {
            "target_database": "company_analytics",
            "target_schema": "company_analytics",
            "domain": "CROSS_DOMAIN",
            "operation": "correlation_and_ranking",
            "metric": "units_sold_and_stock",
            "dimension": "product",
            "time_range": "all_time",
            "required_domains": ["SALES", "INVENTORY"],
            "candidate_tables": ["products", "sales_order_items", "inventory"],
            "visualization_hint": "bar_chart"
        }

    # 3. Top Products by Revenue
    if "highest revenue" in q or "top products" in q or "top revenue" in q:
        return {
            "target_database": "company_analytics",
            "target_schema": "company_analytics",
            "domain": "SALES",
            "operation": "ranking",
            "metric": "revenue",
            "dimension": "product",
            "time_range": "all_time",
            "required_domains": ["SALES"],
            "candidate_tables": ["products", "sales_order_items"],
            "visualization_hint": "bar_chart"
        }

    # 4. HR / Salaries
    if any(k in q for k in ["salary", "salaries", "compensation", "bonus", "payroll", "paid", "wage"]):
        return {
            "target_database": "company_analytics",
            "target_schema": "company_analytics",
            "domain": "HR",
            "operation": "aggregation",
            "metric": "salary",
            "dimension": "department_or_employee",
            "time_range": "current",
            "required_domains": ["HR", "SALARIES"],
            "candidate_tables": ["departments", "employees", "salaries"],
            "visualization_hint": "bar_chart"
        }
    if any(k in q for k in ["employee", "employees", "department", "departments", "headcount", "staff", "manager"]):
        return {
            "target_database": "company_analytics",
            "target_schema": "company_analytics",
            "domain": "HR",
            "operation": "count_and_aggregation",
            "metric": "employee_count",
            "dimension": "department",
            "time_range": "current",
            "required_domains": ["HR"],
            "candidate_tables": ["departments", "employees"],
            "visualization_hint": "bar_chart"
        }

    # 5. CRM
    if any(k in q for k in ["lead", "leads", "customer", "customers", "interaction", "pipeline"]):
        return {
            "target_database": "company_analytics",
            "target_schema": "company_analytics",
            "domain": "CRM",
            "operation": "distribution",
            "metric": "lead_count_or_value",
            "dimension": "status_or_region",
            "time_range": "all_time",
            "required_domains": ["CRM"],
            "candidate_tables": ["leads", "customers", "customer_interactions"],
            "visualization_hint": "pie_chart"
        }

    # 6. Inventory
    if any(k in q for k in ["inventory", "stock", "reorder", "quantity on hand", "deficit"]):
        return {
            "target_database": "company_analytics",
            "target_schema": "company_analytics",
            "domain": "INVENTORY",
            "operation": "threshold_filtering",
            "metric": "quantity_on_hand",
            "dimension": "product",
            "time_range": "current",
            "required_domains": ["INVENTORY"],
            "candidate_tables": ["products", "inventory"],
            "visualization_hint": "bar_chart"
        }

    # 7. Purchasing
    if any(k in q for k in ["supplier", "suppliers", "purchase order", "procurement", "po", "vendor"]):
        return {
            "target_database": "company_analytics",
            "target_schema": "company_analytics",
            "domain": "PURCHASING",
            "operation": "ranking",
            "metric": "purchase_value",
            "dimension": "supplier",
            "time_range": "all_time",
            "required_domains": ["PURCHASING"],
            "candidate_tables": ["suppliers", "purchase_orders", "purchase_order_items"],
            "visualization_hint": "bar_chart"
        }

    # 8. Finance
    if any(k in q for k in ["p&l", "profit", "revenue, expenses", "expense", "expenses", "financials", "operating expense"]):
        return {
            "target_database": "company_analytics",
            "target_schema": "company_analytics",
            "domain": "FINANCE",
            "operation": "financial_summary",
            "metric": "revenue_expenses_profit",
            "dimension": "month",
            "time_range": "2025_2026",
            "required_domains": ["FINANCE"],
            "candidate_tables": ["company_financials", "expenses"],
            "visualization_hint": "line_chart"
        }

    # 9. Sales
    if any(k in q for k in ["sales", "revenue", "order", "orders", "monthly sales", "top products"]):
        return {
            "target_database": "company_analytics",
            "target_schema": "company_analytics",
            "domain": "SALES",
            "operation": "trend",
            "metric": "total_sales",
            "dimension": "month",
            "time_range": "last_12_months",
            "required_domains": ["SALES"],
            "candidate_tables": ["sales_orders", "sales_order_items", "products"],
            "visualization_hint": "line_chart"
        }

    # Default: General Analytics
    return {
        "target_database": "company_analytics",
        "target_schema": "company_analytics",
        "domain": "GENERAL_ANALYTICS",
        "operation": "general_query",
        "metric": "general",
        "dimension": "general",
        "time_range": "all_time",
        "required_domains": ["SALES"],
        "candidate_tables": ["sales_orders", "products"],
        "visualization_hint": "table"
    }

def classify_intent_node(state: AnalyticsState) -> AnalyticsState:
    """
    Extracts structured intent, target database, schema, required business domains, candidate tables,
    and visualization hints from the question.
    """
    question = state["original_question"]
    history = state.get("conversation_history", [])
    logger.info(f"Classifying intent and database routing for question: '{question}'")

    messages = [
        {"role": "system", "content": INTENT_SYSTEM_PROMPT},
    ]
    if history:
        for turn in history[-3:]:
            messages.append({"role": turn.get("role", "user"), "content": turn.get("content", "")})
    messages.append({"role": "user", "content": f"Classify this analytics question: {question}"})

    intent_data: Dict[str, Any] = {}
    heuristic = rule_based_intent_fallback(question)
    if heuristic.get("domain") != "GENERAL_ANALYTICS":
        intent_data = heuristic
        logger.info(f"Fast-path intent matched in <1ms: Domain={intent_data.get('domain')} on {intent_data.get('target_database')}")
    else:
        try:
            reply = ollama_client.generate_chat_sync(
                messages=messages,
                model=settings.OLLAMA_AGENT_MODEL,
                temperature=0.0,
                timeout=5.0
            )
            # Extract JSON from reply
            match = re.search(r"\{.*\}", reply, re.DOTALL)
            if match:
                intent_data = json.loads(match.group(0))
        except Exception as e:
            logger.warning(f"Ollama intent classification failed ({e}), using heuristic planner.")

    if not intent_data or "domain" not in intent_data:
        intent_data = heuristic

    # Ensure required_domains and candidate_tables are populated
    required_domains = intent_data.get("required_domains", [intent_data.get("domain", "GENERAL_ANALYTICS")])
    candidate_tables = intent_data.get("candidate_tables", [])
    if not candidate_tables:
        candidate_tables = heuristic.get("candidate_tables", ["sales_orders"])
        required_domains = heuristic.get("required_domains", required_domains)

    # Resolve target database & schema dynamically
    target_db = intent_data.get("target_database")
    if not target_db:
        if intent_data.get("domain") == "AUTH_ADMIN" or any(t in ["users", "roles", "permissions", "role_permissions", "user_chat_sessions"] for t in candidate_tables):
            target_db = settings.POSTGRES_DB
        else:
            target_db = settings.MYSQL_DB

    target_schema = intent_data.get("target_schema", target_db)
    viz_hint = intent_data.get("visualization_hint", "table")


    logger.info(f"Routed target DB: {target_db} ({target_schema}) | Domain: {intent_data.get('domain')} | Tables: {candidate_tables}")

    return {
        "intent": intent_data,
        "target_database": target_db,
        "target_schema": target_schema,
        "required_domains": required_domains,
        "required_tables": candidate_tables,
        "visualization_hint": viz_hint
    }
