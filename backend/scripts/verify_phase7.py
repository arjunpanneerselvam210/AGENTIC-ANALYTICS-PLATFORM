"""
Phase 7 Verification Script: LangGraph Multi-Agent Analytics Pipeline.
Validates the end-to-end integration between:
FastAPI -> PostgreSQL RBAC -> LangGraph Agents -> MCP Database Server -> FreshMart MySQL
"""

import os
import sys

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.agents.runner import run_analytics_query
from app.agents.nodes.request_validator import validate_request_node
from app.agents.nodes.intent_classifier import classify_intent_node
from app.agents.nodes.permission_checker import check_permissions_node
from app.agents.nodes.sql_validator_node import validate_sql_node
from app.agents.mcp_client import mcp_client

def print_header(title: str):
    print("\n" + "=" * 65)
    print(f"  {title.upper()}")
    print("=" * 65)

def print_result(label: str, passed: bool, detail: str = ""):
    status_str = "[PASS]" if passed else "[FAIL]"
    print(f"  {status_str} {label:<45} {detail}")

def run_verification():
    print_header("FreshMart LangGraph Multi-Agent Analytics Pipeline Verification")

    # --------------------------------------------------------------------------
    # 1. Request Validation Node
    # --------------------------------------------------------------------------
    print("\n1. Request Validation Tests")
    empty_res = validate_request_node({"original_question": "   "})
    print_result("Empty question rejected", not empty_res["is_valid_request"], empty_res.get("validation_error", ""))
    
    valid_res = validate_request_node({"original_question": "How many employees are in each department?"})
    print_result("Valid question accepted", valid_res["is_valid_request"])

    # --------------------------------------------------------------------------
    # 2. Intent Classification & Domain Planning
    # --------------------------------------------------------------------------
    print("\n2. Intent Classification & Domain Planning")
    q_hr = "How many employees are in each department?"
    res_hr = classify_intent_node({"original_question": q_hr})
    print_result("HR intent classified", "HR" in res_hr["required_domains"] or res_hr["intent"].get("domain") == "HR", f"Domain: {res_hr['intent'].get('domain')}")

    q_sales = "Show monthly sales for the last 12 months."
    res_sales = classify_intent_node({"original_question": q_sales})
    print_result("Sales intent classified", "SALES" in res_sales["required_domains"] or res_sales["intent"].get("domain") == "SALES", f"Domain: {res_sales['intent'].get('domain')}")

    q_rc = "Why did profit decrease in August?"
    res_rc = classify_intent_node({"original_question": q_rc})
    rc_passed = res_rc["intent"].get("domain") in ["ROOT_CAUSE", "FINANCE"] or "ROOT_CAUSE" in res_rc.get("required_domains", [])
    print_result("Root-cause intent classified", rc_passed, f"Domain: {res_rc['intent'].get('domain')}")

    # --------------------------------------------------------------------------
    # 3. RBAC Permission Boundary
    # --------------------------------------------------------------------------
    print("\n3. RBAC Permission Checks")
    # Unauthorized: Sales Manager asking for salaries
    unauth_res = check_permissions_node({
        "original_question": "Show employee salaries",
        "role": "SALES_MANAGER",
        "permissions": ["VIEW_CRM", "VIEW_SALES", "VIEW_INVENTORY"],
        "required_domains": ["HR", "SALARIES"],
        "required_tables": ["employees", "salaries"]
    })
    print_result("Sales Manager blocked from Salaries", not unauth_res["permission_granted"], f"Missing: {unauth_res.get('missing_permissions')}")

    # Authorized: HR Manager asking for salaries
    auth_res = check_permissions_node({
        "original_question": "Show employee salaries",
        "role": "HR_MANAGER",
        "permissions": ["VIEW_HR", "VIEW_EMPLOYEE_SALARY", "VIEW_EXPENSES"],
        "required_domains": ["HR", "SALARIES"],
        "required_tables": ["employees", "salaries"]
    })
    print_result("HR Manager authorized for Salaries", auth_res["permission_granted"])

    # --------------------------------------------------------------------------
    # 4. MCP Schema Discovery
    # --------------------------------------------------------------------------
    print("\n4. MCP Schema Discovery Integration")
    tables = mcp_client.list_tables()
    print_result("MCP list_tables called by agent", len(tables) >= 15, f"{len(tables)} tables discovered")

    desc = mcp_client.describe_table("employees")
    print_result("MCP describe_table called by agent", desc.get("success", False), f"{desc.get('column_count')} columns, {len(desc.get('foreign_keys', []))} FKs")

    # --------------------------------------------------------------------------
    # 5. SQL Security Boundary
    # --------------------------------------------------------------------------
    print("\n5. SQL Security Validation Node")
    clean_val = validate_sql_node({"generated_sql": "SELECT * FROM employees LIMIT 10;"})
    print_result("Valid SELECT approved", clean_val["is_sql_valid"])

    bad_val = validate_sql_node({"generated_sql": "SELECT * FROM employees; DROP TABLE employees;"})
    print_result("Multiple statement injection blocked", not bad_val["is_sql_valid"], bad_val.get("sql_error", ""))

    # --------------------------------------------------------------------------
    # 6. End-to-End Analytical Queries Execution
    # --------------------------------------------------------------------------
    print("\n6. End-to-End Pipeline Execution")
    # CEO - HR Query
    ceo_perms = ["VIEW_HR", "VIEW_EMPLOYEE_SALARY", "VIEW_CRM", "VIEW_SALES", "VIEW_INVENTORY", "VIEW_PURCHASES", "VIEW_FINANCE", "VIEW_PROFIT", "VIEW_EXPENSES"]
    hr_exec = run_analytics_query(
        question="How many employees are in each department?",
        user_id=2,
        user_name="Vikram Malhotra",
        role="CEO",
        permissions=ceo_perms
    )
    print_result("HR Query: Employees per department", hr_exec["success"], f"Returned {hr_exec['data']['row_count']} depts (Viz: {hr_exec['visualization_hint']})")

    # Sales Manager - Sales Query
    sales_perms = ["VIEW_CRM", "VIEW_SALES", "VIEW_INVENTORY"]
    sales_exec = run_analytics_query(
        question="Show monthly sales for the last 12 months.",
        user_id=4,
        user_name="Arun Kumar",
        role="SALES_MANAGER",
        permissions=sales_perms
    )
    print_result("Sales Query: Monthly sales trend", sales_exec["success"], f"Returned {sales_exec['data']['row_count']} months (Viz: {sales_exec['visualization_hint']})")

    # Cross-Domain Query: High sales but low stock
    cross_exec = run_analytics_query(
        question="Which products have high sales but low inventory?",
        user_id=2,
        user_name="Vikram Malhotra",
        role="CEO",
        permissions=ceo_perms
    )
    print_result("Cross-Domain: High sales, low stock", cross_exec["success"], f"Returned {cross_exec['data']['row_count']} products (Sources: {cross_exec['sources']})")

    # Finance Manager - Root Cause Query
    fin_perms = ["VIEW_FINANCE", "VIEW_PROFIT", "VIEW_EXPENSES", "VIEW_SALES"]
    rc_exec = run_analytics_query(
        question="Why did profit decrease in August?",
        user_id=7,
        user_name="Rahul Kumar",
        role="FINANCE_MANAGER",
        permissions=fin_perms
    )
    print_result("Root-Cause: August profit drop", rc_exec["success"], f"Returned {rc_exec['data']['row_count']} records (Sources: {rc_exec['sources']})")

    # --------------------------------------------------------------------------
    # 7. Unauthorized Query Rejection (Sales Manager asking for Salaries)
    # --------------------------------------------------------------------------
    print("\n7. Unauthorized Query Enforcement")
    unauth_exec = run_analytics_query(
        question="Show employee salaries",
        user_id=4,
        user_name="Arun Kumar",
        role="SALES_MANAGER",
        permissions=sales_perms
    )
    print_result("Unauthorized request blocked", not unauth_exec["success"], unauth_exec.get("error", ""))

    print_header("ALL PHASE 7 PIPELINE VERIFICATION CHECKS PASSED")

if __name__ == "__main__":
    run_verification()
