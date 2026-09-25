"""
FreshMart RBAC Evaluation Engine for LangGraph Pipeline.
Enforces that user roles & permissions from PostgreSQL strictly authorize
the requested domains and tables before any MCP query is planned or executed.
"""

from typing import List, Dict, Set, Tuple

# Table to required permissions mapping
TABLE_PERMISSION_MAP: Dict[str, List[str]] = {
    "departments": ["VIEW_HR"],
    "employees": ["VIEW_HR"],
    "salaries": ["VIEW_EMPLOYEE_SALARY"],
    "customers": ["VIEW_CRM"],
    "leads": ["VIEW_CRM"],
    "customer_interactions": ["VIEW_CRM"],
    "interactions": ["VIEW_CRM"],
    "sales_orders": ["VIEW_SALES"],
    "sales_order_items": ["VIEW_SALES"],
    "products": ["VIEW_INVENTORY"],
    "inventory": ["VIEW_INVENTORY"],
    "suppliers": ["VIEW_PURCHASES"],
    "purchase_orders": ["VIEW_PURCHASES"],
    "purchase_order_items": ["VIEW_PURCHASES"],
    "expenses": ["VIEW_EXPENSES"],
    "company_financials": ["VIEW_FINANCE", "VIEW_PROFIT"],
}

# Domain to required permissions mapping
DOMAIN_PERMISSION_MAP: Dict[str, List[str]] = {
    "HR": ["VIEW_HR"],
    "SALARIES": ["VIEW_EMPLOYEE_SALARY"],
    "CRM": ["VIEW_CRM"],
    "SALES": ["VIEW_SALES"],
    "INVENTORY": ["VIEW_INVENTORY"],
    "PURCHASING": ["VIEW_PURCHASES"],
    "FINANCE": ["VIEW_FINANCE", "VIEW_PROFIT"],
    "EXPENSES": ["VIEW_EXPENSES"],
}

def evaluate_permissions(
    user_permissions: List[str],
    user_role: str,
    required_domains: List[str],
    required_tables: List[str],
    question: str
) -> Tuple[bool, List[str], str]:
    """
    Evaluates whether the user's granted permissions from PostgreSQL
    authorize the natural-language question, target domains, and required tables.
    
    Returns:
        (permission_granted: bool, missing_permissions: List[str], reason: str)
    """
    user_perms_set: Set[str] = set(user_permissions)
    missing: Set[str] = set()

    # Special check: Sensitive salary / compensation inquiry check in prompt
    salary_keywords = ["salary", "salaries", "compensation", "bonus", "payroll", "base_salary", "wage", "pay"]
    q_lower = question.lower()
    if any(kw in q_lower for kw in salary_keywords):
        if "VIEW_EMPLOYEE_SALARY" not in user_perms_set:
            missing.add("VIEW_EMPLOYEE_SALARY")

    # Evaluate table requirements
    for table in required_tables:
        table_clean = table.strip().lower()
        if table_clean in TABLE_PERMISSION_MAP:
            req_perms = TABLE_PERMISSION_MAP[table_clean]
            # If table allows either of multiple permissions (like financials: VIEW_FINANCE or VIEW_PROFIT)
            if not any(p in user_perms_set for p in req_perms):
                missing.add(req_perms[0])

    # Evaluate domain requirements
    for domain in required_domains:
        dom_clean = domain.strip().upper()
        if dom_clean in DOMAIN_PERMISSION_MAP:
            req_perms = DOMAIN_PERMISSION_MAP[dom_clean]
            if not any(p in user_perms_set for p in req_perms):
                missing.add(req_perms[0])

    if missing:
        missing_list = sorted(list(missing))
        reason = (
            f"Access Denied: Role '{user_role}' lacks required permission(s) "
            f"[{', '.join(missing_list)}] to access requested business data."
        )
        return False, missing_list, reason

    return True, [], "Authorized"
