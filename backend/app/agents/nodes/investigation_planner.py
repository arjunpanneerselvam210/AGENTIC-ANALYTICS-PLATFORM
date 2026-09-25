"""
Node: Investigation Planner Agent
Formulates a structured multi-step investigation plan for analytical queries
before database discovery and execution.
"""

import logging
from typing import Dict, Any, List
from app.agents.state import AnalyticsState

logger = logging.getLogger("agents.investigation_planner")

def plan_investigation_node(state: AnalyticsState) -> AnalyticsState:
    """
    Constructs a structured investigation plan tailored to the analytical intent and question.
    """
    question = state.get("original_question", "")
    q_lower = question.lower()
    intent = state.get("intent", {})
    domain = intent.get("domain", "GENERAL_ANALYTICS")
    operation = intent.get("operation", "")

    # 1. Root-Cause Analysis
    if domain == "ROOT_CAUSE" or "why did profit" in q_lower or "decrease in august" in q_lower or "drop in august" in q_lower:
        plan = {
            "goal": "Identify primary operational and financial drivers behind August 2026 profit contraction",
            "steps": [
                "Retrieve baseline July vs August revenue and net margins from company financials",
                "Analyze Cost of Goods Sold (COGS) and gross margin shifts",
                "Examine operating expenses across logistics, procurement, and overhead categories",
                "Isolate ledger anomalies in emergency logistics and spot procurement",
                "Calculate exact numerical contribution of each variance factor to net profit change",
                "Formulate grounded business recommendations and corrective actions"
            ],
            "focus_metrics": ["net_profit", "total_revenue", "cogs", "emergency_shipping", "spot_procurement"]
        }

    # 2. Cross-Domain Analysis (Sales + Inventory / CRM)
    elif domain == "CROSS_DOMAIN" or ("sales" in q_lower and ("inventory" in q_lower or "stock" in q_lower)):
        plan = {
            "goal": "Cross-correlate commercial sales velocity with warehouse stock levels to identify stockout risks",
            "steps": [
                "Query top grossing products and sales order volume across channels",
                "Join sales velocity data with real-time warehouse inventory balances",
                "Identify high-revenue SKUs operating at or below safety reorder levels",
                "Calculate total commercial revenue at risk due to inventory deficit",
                "Formulate prioritized warehouse replenishment recommendations"
            ],
            "focus_metrics": ["total_revenue", "units_sold", "quantity_on_hand", "reorder_level", "stock_deficit"]
        }

    # 3. Comparative Analysis
    elif domain == "COMPARISON" or "compare" in q_lower or "versus" in q_lower or "vs" in q_lower:
        plan = {
            "goal": "Conduct period-over-period comparative variance analysis across key enterprise dimensions",
            "steps": [
                "Query metric values for the baseline reference period",
                "Query metric values for the target comparison period",
                "Calculate absolute nominal variance and percentage growth rate",
                "Break down variance by category, department, or operational unit",
                "Synthesize comparative business findings"
            ],
            "focus_metrics": ["current_value", "previous_value", "absolute_change", "percentage_change"]
        }

    # 4. Anomaly Detection
    elif domain == "ANOMALY" or "unusual" in q_lower or "anomaly" in q_lower or "outlier" in q_lower:
        plan = {
            "goal": "Detect statistical expenditure anomalies and ledger spikes against historical baselines",
            "steps": [
                "Establish historical baseline expenditure and transaction distribution",
                "Query target period line-item disbursements and ledger records",
                "Flag expenditure categories exceeding standard deviation thresholds",
                "Trace anomaly root causes to specific vendor invoices or operational events",
                "Provide risk classification and mitigation recommendations"
            ],
            "focus_metrics": ["baseline_expenditure", "observed_value", "variance_ratio", "severity"]
        }

    # 5. Trend Analysis / Sales
    elif domain in ["TREND_ANALYSIS", "SALES"] or "trend" in q_lower or "monthly sales" in q_lower:
        plan = {
            "goal": "Analyze multi-period sales trajectory, commercial velocity, and seasonality",
            "steps": [
                "Aggregate sequential monthly sales orders and gross merchandise value",
                "Determine overall trajectory direction (growth, contraction, stable)",
                "Identify historical peak performance and trough periods",
                "Evaluate month-over-month growth velocity",
                "Provide executive commercial observations"
            ],
            "focus_metrics": ["monthly_revenue", "order_count", "avg_order_value", "growth_pct"]
        }

    # 6. Default / Domain-Specific Plan
    else:
        plan = {
            "goal": f"Execute authorized analytical investigation for {domain} domain",
            "steps": [
                f"Verify schema structures and relationships for {domain} entities",
                "Execute read-only SQL query via MCP database bridge",
                "Validate returned dataset cardinality and mathematical integrity",
                "Perform business analysis and metric summarization",
                "Format data visualization and provenance citations"
            ],
            "focus_metrics": ["record_count", "aggregated_totals"]
        }

    logger.info(f"Formulated investigation plan with {len(plan['steps'])} steps for goal: '{plan['goal']}'")
    return {
        "investigation_plan": plan
    }
