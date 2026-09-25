"""
LangGraph Multi-Agent Workflow Engine for FreshMart Analytics.
Constructs and compiles the StateGraph connecting:
Validation -> Intent -> RBAC -> MCP Schema -> SQL Gen -> Security -> MCP Exec -> Result -> Analysis -> Output
"""

import logging
from langgraph.graph import StateGraph, START, END
from app.agents.state import AnalyticsState
from app.agents.nodes.request_validator import validate_request_node
from app.agents.nodes.intent_classifier import classify_intent_node
from app.agents.nodes.investigation_planner import plan_investigation_node
from app.agents.nodes.permission_checker import check_permissions_node
from app.agents.nodes.schema_planner import plan_schema_node, discover_schema_node
from app.agents.nodes.sql_generator import generate_sql_node
from app.agents.nodes.sql_validator_node import validate_sql_node
from app.agents.nodes.sql_corrector import correct_sql_node
from app.agents.nodes.sql_executor import execute_sql_node
from app.agents.nodes.result_validator import validate_result_node
from app.agents.nodes.business_analyzer import analyze_results_node
from app.agents.nodes.response_generator import generate_response_node

logger = logging.getLogger("agents.workflow")

# ------------------------------------------------------------------------------
# Conditional Edge Routing Functions
# ------------------------------------------------------------------------------
def route_after_request_validation(state: AnalyticsState) -> str:
    """Routes to intent classifier if request is valid, else response generator."""
    if state.get("is_valid_request", False):
        return "classify_intent"
    return "generate_response"

def route_after_permission_check(state: AnalyticsState) -> str:
    """Routes to schema planner if user is authorized, else directly to response generator."""
    if state.get("permission_granted", False):
        return "plan_schema"
    return "generate_response"

def route_after_sql_validation(state: AnalyticsState) -> str:
    """Routes to execution if SQL is valid, or self-correction if retry budget permits."""
    if state.get("is_sql_valid", False):
        return "execute_sql"
    
    retry_count = state.get("retry_count", 0)
    max_retries = state.get("max_retries", 2)
    if retry_count < max_retries:
        return "correct_sql"
    return "generate_response"

def route_after_sql_execution(state: AnalyticsState) -> str:
    """Routes to result validator if query succeeded, or self-correction if failed and retry budget permits."""
    if state.get("result_valid", False):
        return "validate_result"
    
    retry_count = state.get("retry_count", 0)
    max_retries = state.get("max_retries", 2)
    if retry_count < max_retries:
        return "correct_sql"
    return "generate_response"

def route_after_result_validation(state: AnalyticsState) -> str:
    """Routes to business analyzer if data valid, else response generator."""
    if state.get("result_valid", False):
        return "analyze_results"
    return "generate_response"

# ------------------------------------------------------------------------------
# StateGraph Assembly
# ------------------------------------------------------------------------------
def create_analytics_graph() -> StateGraph:
    """
    Constructs and compiles the complete multi-agent analytics pipeline.
    """
    workflow = StateGraph(AnalyticsState)

    # 1. Register Nodes
    workflow.add_node("validate_request", validate_request_node)
    workflow.add_node("classify_intent", classify_intent_node)
    workflow.add_node("plan_investigation", plan_investigation_node)
    workflow.add_node("check_permissions", check_permissions_node)
    workflow.add_node("plan_schema", plan_schema_node)
    workflow.add_node("discover_schema", discover_schema_node)
    workflow.add_node("generate_sql", generate_sql_node)
    workflow.add_node("validate_sql", validate_sql_node)
    workflow.add_node("correct_sql", correct_sql_node)
    workflow.add_node("execute_sql", execute_sql_node)
    workflow.add_node("validate_result", validate_result_node)
    workflow.add_node("analyze_results", analyze_results_node)
    workflow.add_node("generate_response", generate_response_node)

    # 2. Add Edges & Conditional Branches
    workflow.add_edge(START, "validate_request")

    workflow.add_conditional_edges(
        "validate_request",
        route_after_request_validation,
        {
            "classify_intent": "classify_intent",
            "generate_response": "generate_response"
        }
    )

    workflow.add_edge("classify_intent", "plan_investigation")
    workflow.add_edge("plan_investigation", "check_permissions")

    workflow.add_conditional_edges(
        "check_permissions",
        route_after_permission_check,
        {
            "plan_schema": "plan_schema",
            "generate_response": "generate_response"
        }
    )

    workflow.add_edge("plan_schema", "discover_schema")
    workflow.add_edge("discover_schema", "generate_sql")
    workflow.add_edge("generate_sql", "validate_sql")

    workflow.add_conditional_edges(
        "validate_sql",
        route_after_sql_validation,
        {
            "execute_sql": "execute_sql",
            "correct_sql": "correct_sql",
            "generate_response": "generate_response"
        }
    )

    workflow.add_edge("correct_sql", "validate_sql")

    workflow.add_conditional_edges(
        "execute_sql",
        route_after_sql_execution,
        {
            "validate_result": "validate_result",
            "correct_sql": "correct_sql",
            "generate_response": "generate_response"
        }
    )

    workflow.add_conditional_edges(
        "validate_result",
        route_after_result_validation,
        {
            "analyze_results": "analyze_results",
            "generate_response": "generate_response"
        }
    )

    workflow.add_edge("analyze_results", "generate_response")
    workflow.add_edge("generate_response", END)

    return workflow.compile()

# Singleton compiled workflow instance
analytics_graph = create_analytics_graph()
