"""
High-Level Entrypoint Runner for FreshMart LangGraph Analytics Pipeline.
Initializes state, orchestrates graph execution, and extracts structured response.
"""

import logging
from typing import Dict, Any, List, Optional
from app.agents.state import AnalyticsState
from app.agents.workflow import analytics_graph

logger = logging.getLogger("agents.runner")

def run_analytics_query(
    question: str,
    user_id: int,
    user_name: str,
    role: str,
    permissions: List[str],
    conversation_history: Optional[List[Dict[str, str]]] = None,
    max_retries: int = 2
) -> Dict[str, Any]:
    """
    Executes the full LangGraph analytics pipeline for an authenticated FreshMart user.
    """
    initial_state: AnalyticsState = {
        "user_id": user_id,
        "user_name": user_name,
        "role": role,
        "permissions": permissions,
        "original_question": question,
        "conversation_history": conversation_history or [],
        "is_valid_request": False,
        "permission_granted": False,
        "retry_count": 0,
        "max_retries": max_retries,
        "sources": [],
        "columns_used": [],
        "visualization_hint": "table",
        "success": False
    }

    logger.info(f"Initiating LangGraph pipeline for user '{user_name}' ({role}) | Question: '{question}'")

    final_state = analytics_graph.invoke(initial_state)

    query_res = final_state.get("query_result", {})
    columns = query_res.get("columns", [])
    rows = query_res.get("rows", [])

    return {
        "success": final_state.get("success", False),
        "question": question,
        "answer": final_state.get("final_answer", ""),
        "data": {
            "columns": columns,
            "rows": rows,
            "row_count": len(rows),
            "truncated": query_res.get("truncated", False)
        },
        "intent": final_state.get("intent", {}),
        "sources": final_state.get("sources", []),
        "columns_used": final_state.get("columns_used", []),
        "visualization_hint": final_state.get("visualization_hint", "table"),
        "investigation_plan": final_state.get("investigation_plan"),
        "root_cause_analysis": final_state.get("root_cause_analysis"),
        "comparisons": final_state.get("comparisons"),
        "trends": final_state.get("trends"),
        "anomalies": final_state.get("anomalies"),
        "insights": final_state.get("insights", []),
        "recommendations": final_state.get("recommendations", []),
        "confidence": final_state.get("confidence", "HIGH"),
        "error": final_state.get("error")
    }

