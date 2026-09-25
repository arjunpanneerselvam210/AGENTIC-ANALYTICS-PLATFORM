"""
Phase 9 Verification Suite: Real Analytics Integration & Visualization
Tests end-to-end integration between:
FastAPI Gateway <-> PostgreSQL RBAC <-> LangGraph Pipeline <-> MCP Server <-> FreshMart MySQL
"""

import sys
import time
import httpx

BASE_URL = "http://localhost:8000/api/v1"

def print_header(title: str):
    print("\n" + "=" * 70)
    print(f"  {title.upper()}")
    print("=" * 70)

def print_result(label: str, passed: bool, detail: str = ""):
    status_str = "[PASS]" if passed else "[FAIL]"
    # Clean detail for cp1252 terminal compatibility
    safe_detail = detail.replace("\u20b9", "INR ")
    print(f"  {status_str} {label:<45} {safe_detail}")

def run_verification():
    print_header("Phase 9: Real FreshMart Analytics & Visualization Verification")
    client = httpx.Client(base_url=BASE_URL, timeout=90.0)

    # 1. Authenticate CEO
    print("\n1. Authentication & Session Initialization")
    login_res = client.post("/auth/login", data={"username": "ceo", "password": "CeoPassword123!"})
    ceo_token = login_res.json().get("access_token")
    print_result("CEO Authentication", login_res.status_code == 200, f"HTTP {login_res.status_code}")
    ceo_headers = {"Authorization": f"Bearer {ceo_token}"}

    # 2. Live Dashboard Endpoint
    print("\n2. Live Deterministic Executive Dashboard Endpoint")
    dash_res = client.get("/analytics/dashboard?range=30d", headers=ceo_headers)
    dash_ok = dash_res.status_code == 200
    if dash_ok:
        d = dash_res.json()
        print_result("Live Dashboard Query (30d)", True, f"KPIs: {len(d['kpis'])}, Trend: {len(d['sales_trend'])}, SKUs: {len(d['top_products'])}")
    else:
        print_result("Live Dashboard Query (30d)", False, f"HTTP {dash_res.status_code}")

    # 3. Sales Benchmark Query
    print("\n3. Real Sales Analytics Query")
    q_sales = "Show monthly sales trend for the last 12 months"
    t0 = time.time()
    res_sales = client.post("/analytics/query", headers=ceo_headers, json={"question": q_sales})
    t_sales = time.time() - t0
    sales_ok = res_sales.status_code == 200 and res_sales.json().get("success", False)
    if sales_ok:
        s_data = res_sales.json()
        row_cnt = s_data["data"]["row_count"]
        viz = s_data["visualization_hint"]
        print_result("Monthly Sales Trend", True, f"Returned {row_cnt} months in {t_sales:.1f}s (Viz: {viz})")
    else:
        print_result("Monthly Sales Trend", False, f"HTTP {res_sales.status_code}")

    # 4. Inventory Benchmark Query
    print("\n4. Real Inventory Health Query")
    q_inv = "Show products that are currently low in stock"
    t0 = time.time()
    res_inv = client.post("/analytics/query", headers=ceo_headers, json={"question": q_inv})
    t_inv = time.time() - t0
    inv_ok = res_inv.status_code == 200 and res_inv.json().get("success", False)
    if inv_ok:
        i_data = res_inv.json()
        row_cnt = i_data["data"]["row_count"]
        sources = i_data["sources"]
        print_result("Low Stock Products", True, f"Returned {row_cnt} items in {t_inv:.1f}s (Sources: {sources})")
    else:
        print_result("Low Stock Products", False, f"HTTP {res_inv.status_code}")

    # 5. Cross-Domain Query (Sales + Inventory)
    print("\n5. Cross-Domain Analytics Query")
    q_cross = "Which products generated the highest revenue and are currently low in stock?"
    t0 = time.time()
    res_cross = client.post("/analytics/query", headers=ceo_headers, json={"question": q_cross})
    t_cross = time.time() - t0
    cross_ok = res_cross.status_code == 200 and res_cross.json().get("success", False)
    if cross_ok:
        c_data = res_cross.json()
        row_cnt = c_data["data"]["row_count"]
        cols = c_data["data"]["columns"]
        print_result("Cross-Domain (Revenue + Inventory)", True, f"Returned {row_cnt} rows in {t_cross:.1f}s (Cols: {cols[:3]})")
    else:
        print_result("Cross-Domain (Revenue + Inventory)", False, f"HTTP {res_cross.status_code}")

    # 6. Root-Cause Diagnostic Query
    print("\n6. Root-Cause Analysis Query")
    q_rc = "Why did profit decrease in August?"
    t0 = time.time()
    res_rc = client.post("/analytics/query", headers=ceo_headers, json={"question": q_rc})
    t_rc = time.time() - t0
    rc_ok = res_rc.status_code == 200 and res_rc.json().get("success", False)
    if rc_ok:
        rc_data = res_rc.json()
        print_result("Root-Cause (August Profit Contraction)", True, f"Analysis returned in {t_rc:.1f}s")
    else:
        print_result("Root-Cause (August Profit Contraction)", False, f"HTTP {res_rc.status_code}")

    # 7. CRM Distribution Query
    print("\n7. CRM Lead Distribution Query")
    q_crm = "Show lead status distribution"
    t0 = time.time()
    res_crm = client.post("/analytics/query", headers=ceo_headers, json={"question": q_crm})
    t_crm = time.time() - t0
    crm_ok = res_crm.status_code == 200 and res_crm.json().get("success", False)
    if crm_ok:
        crm_data = res_crm.json()
        row_cnt = crm_data["data"]["row_count"]
        print_result("CRM Lead Status Distribution", True, f"Returned {row_cnt} statuses in {t_crm:.1f}s")
    else:
        print_result("CRM Lead Status Distribution", False, f"HTTP {res_crm.status_code}")

    # 8. RBAC Negative Test: Sales Manager Asking for Salaries (Must 403 Forbidden)
    print("\n8. Enterprise RBAC Security Guard Verification")
    sm_login = client.post("/auth/login", data={"username": "sales.manager", "password": "SalesPassword123!"})
    sm_token = sm_login.json().get("access_token")
    sm_headers = {"Authorization": f"Bearer {sm_token}"}

    q_sal = "Show employee salaries"
    res_unauth = client.post("/analytics/query", headers=sm_headers, json={"question": q_sal})
    unauth_blocked = res_unauth.status_code == 403
    print_result("Sales Manager blocked from Salaries (403)", unauth_blocked, f"HTTP {res_unauth.status_code} - {res_unauth.json().get('detail', '')[:40]}")

    # Sales Manager Asking for Allowed Sales Query (Must 200 OK)
    res_auth = client.post("/analytics/query", headers=sm_headers, json={"question": "Show monthly sales trend for the last 12 months"})
    auth_allowed = res_auth.status_code == 200 and res_auth.json().get("success", False)
    print_result("Sales Manager allowed for Sales Query (200)", auth_allowed, f"HTTP {res_auth.status_code}")

    print_header("ALL PHASE 9 BACKEND INTEGRATION CHECKS COMPLETE")

if __name__ == "__main__":
    run_verification()
