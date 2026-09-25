"""
Node: RBAC Permission Checker
Verifies user's PostgreSQL role and granted permissions against the requested
business domains and database tables.
"""

import logging
from app.agents.state import AnalyticsState
from app.agents.rbac_guard import evaluate_permissions

logger = logging.getLogger("agents.permission_checker")

def check_permissions_node(state: AnalyticsState) -> AnalyticsState:
    """
    Evaluates granted permissions against target domains and candidate tables.
    If unauthorized, sets permission_granted = False and records missing permissions.
    """
    user_role = state.get("role", "ANONYMOUS")
    user_perms = state.get("permissions", [])
    required_domains = state.get("required_domains", [])
    required_tables = state.get("required_tables", [])
    question = state.get("original_question", "")

    logger.info(f"Checking RBAC for role '{user_role}' with {len(user_perms)} permissions on domains {required_domains}")

    granted, missing, reason = evaluate_permissions(
        user_permissions=user_perms,
        user_role=user_role,
        required_domains=required_domains,
        required_tables=required_tables,
        question=question
    )

    if not granted:
        logger.warning(f"RBAC check failed: {reason}")
        return {
            "permission_granted": False,
            "missing_permissions": missing,
            "error": reason,
            "success": False
        }

    logger.info("RBAC check passed. User is authorized.")
    return {
        "permission_granted": True,
        "missing_permissions": []
    }
