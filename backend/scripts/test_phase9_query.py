import sys
import time
from app.agents.runner import run_analytics_query

ceo_perms = ['VIEW_HR', 'VIEW_EMPLOYEE_SALARY', 'VIEW_CRM', 'VIEW_SALES', 'VIEW_INVENTORY', 'VIEW_PURCHASES', 'VIEW_FINANCE', 'VIEW_PROFIT', 'VIEW_EXPENSES']

print("Starting query...", flush=True)
t0 = time.time()
res = run_analytics_query(
    question="Show monthly sales for the last 12 months.",
    user_id=2,
    user_name="Vikram Malhotra",
    role="CEO",
    permissions=ceo_perms
)
t1 = time.time()
print(f"Finished in {t1-t0:.2f}s! Success: {res.get('success')}", flush=True)
print("Data rows:", len(res.get("data", {}).get("rows", [])))
print("Data columns:", res.get("data", {}).get("columns"))
print("Sources:", res.get("sources"))
print("Visualization hint:", res.get("visualization_hint"))
print("Answer:\n", res.get("answer"))
