"""
Node: Request Validator
Validates that incoming natural language question is non-empty, clean, and of appropriate length.
"""

import logging
from app.agents.state import AnalyticsState

logger = logging.getLogger("agents.request_validator")

def validate_request_node(state: AnalyticsState) -> AnalyticsState:
    """
    Validates the incoming user query.
    Rejects empty, whitespace-only, or excessively long/malformed questions.
    """
    question = (state.get("original_question") or "").strip()
    logger.info(f"Validating request: '{question[:80]}' (len: {len(question)})")

    if not question:
        return {
            "is_valid_request": False,
            "validation_error": "Question cannot be empty. Please provide an analytics question.",
            "error": "Empty question provided.",
            "success": False
        }

    if len(question) < 3:
        return {
            "is_valid_request": False,
            "validation_error": "Question is too short. Please provide a descriptive analytics query.",
            "error": "Query too short.",
            "success": False
        }

    if len(question) > 1000:
        return {
            "is_valid_request": False,
            "validation_error": "Question exceeds maximum length of 1,000 characters.",
            "error": "Query exceeds maximum allowed length.",
            "success": False
        }

    # Reject destructive modification commands in natural language
    q_lower = question.lower()
    destructive_patterns = [
        "delete from", "delete all", "drop table", "drop database", "truncate table",
        "truncate ", "alter table", "update ", "insert into", "grant all", "revoke all"
    ]
    if any(pat in q_lower for pat in destructive_patterns):
        logger.warning(f"Rejected destructive operation attempt: '{question}'")
        return {
            "is_valid_request": False,
            "validation_error": "Data modification and destructive operations (DELETE, DROP, TRUNCATE, UPDATE, INSERT) are strictly rejected. FreshMart Analytics operates exclusively in read-only analytical mode.",
            "error": "Unsupported request: Data modification operations are forbidden.",
            "success": False
        }

    return {
        "is_valid_request": True,
        "validation_error": None
    }

