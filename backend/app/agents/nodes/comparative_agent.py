"""
Node: Comparative, Trend & Anomaly Analytics Agent
Calculates deterministic period-over-period deltas, trend trajectories,
and statistical anomaly flags against FreshMart operational baselines.
"""

import logging
from typing import Dict, Any, List, Optional
from mcp_server.database import MCPDatabaseManager

logger = logging.getLogger("agents.comparative")

def compute_comparative_metrics(question: str, query_rows: List[Dict[str, Any]]) -> Optional[List[Dict[str, Any]]]:
    """
    Computes deterministic period-over-period comparative metrics for questions
    requesting July vs August comparisons or quarterly variance.
    """
    q = question.lower()
    if not ("compare" in q or "versus" in q or "vs" in q or "difference" in q):
        return None

    comparisons: List[Dict[str, Any]] = []

    # Check for Financials Comparison (July vs August)
    july_row = next((r for r in query_rows if r.get("month_num") == 7 or str(r.get("month_name", "")).lower() == "july"), None)
    aug_row = next((r for r in query_rows if r.get("month_num") == 8 or str(r.get("month_name", "")).lower() == "august"), None)

    if july_row and aug_row:
        for metric, label in [
            ("total_revenue", "Gross Revenue"),
            ("cogs", "Cost of Goods Sold (COGS)"),
            ("operating_expenses", "Operating Expenses"),
            ("net_profit", "Net Profit")
        ]:
            if metric in july_row and metric in aug_row:
                curr_val = float(aug_row[metric])
                prev_val = float(july_row[metric])
                diff = curr_val - prev_val
                pct = ((diff / prev_val) * 100) if prev_val != 0 else 0.0
                comparisons.append({
                    "dimension": label,
                    "current_period": "August 2026",
                    "previous_period": "July 2026",
                    "current_value": curr_val,
                    "previous_value": prev_val,
                    "absolute_change": round(diff, 2),
                    "percentage_change": round(pct, 2)
                })

    # Generic first two rows comparison if tabular
    elif len(query_rows) >= 2:
        r1, r2 = query_rows[0], query_rows[1]
        for k, v in r2.items():
            if isinstance(v, (int, float)) and isinstance(r1.get(k), (int, float)):
                v1, v2 = float(r1[k]), float(v)
                diff = v2 - v1
                pct = ((diff / v1) * 100) if v1 != 0 else 0.0
                p1 = str(r1.get("month_name") or r1.get("month") or r1.get("dept_name") or "Period 1")
                p2 = str(r2.get("month_name") or r2.get("month") or r2.get("dept_name") or "Period 2")
                comparisons.append({
                    "dimension": k.replace("_", " ").title(),
                    "current_period": p2,
                    "previous_period": p1,
                    "current_value": v2,
                    "previous_value": v1,
                    "absolute_change": round(diff, 2),
                    "percentage_change": round(pct, 2)
                })
                break

    return comparisons if comparisons else None

def compute_trend_summary(query_rows: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Evaluates multi-period time-series trend velocity, direction, peak, and trough.
    """
    if len(query_rows) < 3:
        return None

    # Detect revenue or sales metric
    val_key = None
    for k in ["total_revenue", "sales", "revenue", "order_count", "amount"]:
        if any(k in r for r in query_rows):
            val_key = k
            break

    if not val_key:
        return None

    numeric_vals = [float(r[val_key]) for r in query_rows if r.get(val_key) is not None]
    if len(numeric_vals) < 3:
        return None

    first_val = numeric_vals[0]
    last_val = numeric_vals[-1]
    overall_change = last_val - first_val
    overall_pct = ((overall_change / first_val) * 100) if first_val > 0 else 0.0

    max_idx = numeric_vals.index(max(numeric_vals))
    min_idx = numeric_vals.index(min(numeric_vals))

    peak_period = str(query_rows[max_idx].get("month") or query_rows[max_idx].get("month_name") or f"Period {max_idx + 1}")
    trough_period = str(query_rows[min_idx].get("month") or query_rows[min_idx].get("month_name") or f"Period {min_idx + 1}")

    if overall_pct > 5.0:
        direction = "UPWARD"
    elif overall_pct < -5.0:
        direction = "DOWNWARD"
    else:
        direction = "STABLE"

    return {
        "direction": direction,
        "highest_period": {"period": peak_period, "value": max(numeric_vals)},
        "lowest_period": {"period": trough_period, "value": min(numeric_vals)},
        "avg_growth_pct": round(overall_pct / len(numeric_vals), 2),
        "summary": f"Trajectory displays an {direction.lower()} momentum with peak performance recorded in {peak_period}."
    }

def detect_operational_anomalies(question: str) -> Optional[List[Dict[str, Any]]]:
    """
    Lightweight deterministic anomaly detection against FreshMart expense ledgers.
    """
    q = question.lower()
    if not ("anomaly" in q or "unusual" in q or "outlier" in q or "spike" in q or "august" in q):
        return None

    db = MCPDatabaseManager()
    exp_res = db.execute_read_only_query(
        "SELECT category, "
        "SUM(CASE WHEN expense_date BETWEEN '2026-07-01' AND '2026-07-31' THEN amount ELSE 0 END) AS july_total, "
        "SUM(CASE WHEN expense_date BETWEEN '2026-08-01' AND '2026-08-31' THEN amount ELSE 0 END) AS august_total "
        "FROM expenses "
        "WHERE expense_date BETWEEN '2026-07-01' AND '2026-08-31' "
        "GROUP BY category;"
    )
    rows = exp_res.get("rows", [])
    anomalies: List[Dict[str, Any]] = []

    for r in rows:
        cat = str(r.get("category", ""))
        j_amt = float(r.get("july_total", 0))
        a_amt = float(r.get("august_total", 0))

        if j_amt > 0:
            pct_change = ((a_amt - j_amt) / j_amt) * 100
            # Flag spikes greater than +50%
            if pct_change >= 50.0:
                severity = "HIGH" if pct_change > 150.0 else "MEDIUM"
                anomalies.append({
                    "metric": f"{cat} Ledger",
                    "period": "August 2026",
                    "value": a_amt,
                    "baseline": j_amt,
                    "change_percent": round(pct_change, 1),
                    "anomaly": True,
                    "severity": severity
                })

    return anomalies if anomalies else None
