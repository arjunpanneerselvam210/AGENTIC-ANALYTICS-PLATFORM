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
    """
    q = question.lower()
    
    # 1. Root Cause Analysis
    if any(k in q for k in ["why did profit", "decrease in august", "drop in august", "profit drop", "root cause", "profit decrease"]):
        return {
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
            "domain": "SALES",
            "operation": "ranking",
            "metric": "revenue",
            "dimension": "product",
            "time_range": "all_time",
            "required_domains": ["SALES"],
            "candidate_tables": ["products", "sales_order_items"],
            "visualization_hint": "bar_chart"
        }

    # 3. HR / Salaries
    if any(k in q for k in ["salary", "salaries", "compensation", "bonus", "payroll", "paid", "wage"]):
        return {
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
            "domain": "HR",
            "operation": "count_and_aggregation",
            "metric": "employee_count",
            "dimension": "department",
            "time_range": "current",
            "required_domains": ["HR"],
            "candidate_tables": ["departments", "employees"],
            "visualization_hint": "bar_chart"
        }

    # 4. CRM
    if any(k in q for k in ["lead", "leads", "customer", "customers", "interaction", "pipeline"]):
        return {
            "domain": "CRM",
            "operation": "distribution",
            "metric": "lead_count_or_value",
            "dimension": "status_or_region",
            "time_range": "all_time",
            "required_domains": ["CRM"],
            "candidate_tables": ["leads", "customers", "customer_interactions"],
            "visualization_hint": "pie_chart"
        }

    # 5. Inventory
    if any(k in q for k in ["inventory", "stock", "reorder", "quantity on hand", "deficit"]):
        return {
            "domain": "INVENTORY",
            "operation": "threshold_filtering",
            "metric": "quantity_on_hand",
            "dimension": "product",
            "time_range": "current",
            "required_domains": ["INVENTORY"],
            "candidate_tables": ["products", "inventory"],
            "visualization_hint": "bar_chart"
        }

    # 6. Purchasing
    if any(k in q for k in ["supplier", "suppliers", "purchase order", "procurement", "po", "vendor"]):
        return {
            "domain": "PURCHASING",
            "operation": "ranking",
            "metric": "purchase_value",
            "dimension": "supplier",
            "time_range": "all_time",
            "required_domains": ["PURCHASING"],
            "candidate_tables": ["suppliers", "purchase_orders", "purchase_order_items"],
            "visualization_hint": "bar_chart"
        }

    # 7. Finance
    if any(k in q for k in ["p&l", "profit", "revenue, expenses", "expense", "expenses", "financials", "operating expense"]):
        return {
            "domain": "FINANCE",
            "operation": "financial_summary",
            "metric": "revenue_expenses_profit",
            "dimension": "month",
            "time_range": "2025_2026",
            "required_domains": ["FINANCE"],
            "candidate_tables": ["company_financials", "expenses"],
            "visualization_hint": "line_chart"
        }

    # 8. Sales
    if any(k in q for k in ["sales", "revenue", "order", "orders", "monthly sales", "top products"]):
        return {
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
    Extracts structured intent, required business domains, candidate tables,
    and visualization hints from the question.
    """
    question = state["original_question"]
    history = state.get("conversation_history", [])
    logger.info(f"Classifying intent for question: '{question}'")

    messages = [
        {"role": "system", "content": INTENT_SYSTEM_PROMPT},
    ]
    if history:
        for turn in history[-3:]:
            messages.append({"role": turn.get("role", "user"), "content": turn.get("content", "")})
    messages.append({"role": "user", "content": f"Classify this analytics question: {question}"})

    intent_data: Dict[str, Any] = {}
    try:
        reply = ollama_client.generate_chat_sync(
            messages=messages,
            model=settings.OLLAMA_AGENT_MODEL,
            temperature=0.0,
            timeout=15.0
        )
        # Extract JSON from reply
        match = re.search(r"\{.*\}", reply, re.DOTALL)
        if match:
            intent_data = json.loads(match.group(0))
    except Exception as e:
        logger.warning(f"Ollama intent classification failed ({e}), using heuristic planner.")

    if not intent_data or "domain" not in intent_data:
        intent_data = rule_based_intent_fallback(question)

    # Ensure required_domains and candidate_tables are populated
    required_domains = intent_data.get("required_domains", [intent_data.get("domain", "GENERAL_ANALYTICS")])
    candidate_tables = intent_data.get("candidate_tables", [])
    if not candidate_tables:
        fallback = rule_based_intent_fallback(question)
        candidate_tables = fallback.get("candidate_tables", ["sales_orders"])
        required_domains = fallback.get("required_domains", required_domains)

    viz_hint = intent_data.get("visualization_hint", "table")

    logger.info(f"Classified domain: {intent_data.get('domain')} | Domains: {required_domains} | Tables: {candidate_tables}")

    return {
        "intent": intent_data,
        "required_domains": required_domains,
        "required_tables": candidate_tables,
        "visualization_hint": viz_hint
    }
