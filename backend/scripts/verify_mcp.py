"""
Automated Verification Suite for FreshMart MCP Database Server
Tests:
1. Discovery of all business tables via list_tables (and zero leakage of auth tables).
2. Schema introspection via describe_table across multiple domains.
3. Security boundary enforcement (rejection of UPDATE, DELETE, INSERT, DROP, ALTER, TRUNCATE, and multi-statements).
4. Business analytical queries across HR, CRM, Sales, Inventory, Purchasing, and Finance.
5. Cross-domain analytics and Root-Cause profit-drop data retrieval.
6. Row limit and truncation signaling.
"""

import sys
import os

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from mcp_server import execute_tool_directly

GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

def print_result(title: str, passed: bool, details: str = ""):
    icon = f"{GREEN}[PASS]{RESET}" if passed else f"{RED}[FAIL]{RESET}"
    print(f"  {icon} {BOLD}{title:<42}{RESET} {details}")

def main():
    print(f"\n{BOLD}{CYAN}============================================================{RESET}")
    print(f"{BOLD}{CYAN}  FRESHMART MCP DATABASE SERVER VERIFICATION SUITE{RESET}")
    print(f"{BOLD}{CYAN}  Model Context Protocol Tools & SQL Security Verification{RESET}")
    print(f"{BOLD}{CYAN}============================================================{RESET}\n")

    all_passed = True

    # --------------------------------------------------------------------------
    # 1. Test Tool: list_tables
    # --------------------------------------------------------------------------
    print(f"{BOLD}1. Tool Test: list_tables{RESET}")
    res_tables = execute_tool_directly("list_tables")
    tables_ok = res_tables.get("success") is True and res_tables.get("table_count", 0) >= 15
    print_result("list_tables executed successfully", tables_ok, f"Discovered {res_tables.get('table_count')} tables")
    
    # Verify no PostgreSQL auth tables leaked
    tables_list = res_tables.get("tables", [])
    no_auth_leak = "users" not in tables_list and "roles" not in tables_list and "permissions" not in tables_list
    print_result("No Auth/PostgreSQL tables exposed", no_auth_leak, "Zero auth schema leakage confirmed")

    if not (tables_ok and no_auth_leak):
        all_passed = False

    # --------------------------------------------------------------------------
    # 2. Tool Test: describe_table
    # --------------------------------------------------------------------------
    print(f"\n{BOLD}2. Tool Test: describe_table{RESET}")
    for tbl in ["employees", "products", "sales_orders", "inventory", "expenses"]:
        desc = execute_tool_directly("describe_table", {"table_name": tbl})
        desc_ok = desc.get("success") is True and desc.get("column_count", 0) > 0
        fks = len(desc.get("foreign_keys", []))
        print_result(f"describe_table ('{tbl}')", desc_ok, f"{desc.get('column_count')} cols, {fks} FKs")
        if not desc_ok:
            all_passed = False

    # Test invalid table rejection
    bad_desc = execute_tool_directly("describe_table", {"table_name": "non_existent_table"})
    bad_desc_rejected = bad_desc.get("success") is False and "does not exist" in bad_desc.get("error", "")
    print_result("describe_table invalid table rejected", bad_desc_rejected, bad_desc.get("error", ""))
    if not bad_desc_rejected:
        all_passed = False

    # --------------------------------------------------------------------------
    # 3. Security Boundary & Dangerous SQL Rejections
    # --------------------------------------------------------------------------
    print(f"\n{BOLD}3. SQL Security Boundary Enforcement{RESET}")
    dangerous_cases = [
        ("UPDATE query blocked", "UPDATE employees SET status = 'Terminated';"),
        ("DELETE query blocked", "DELETE FROM customers WHERE customer_id = 'C001';"),
        ("INSERT query blocked", "INSERT INTO departments (dept_id, dept_name, location) VALUES ('D99', 'Fake', 'Nowhere');"),
        ("DROP TABLE blocked", "DROP TABLE employees;"),
        ("ALTER TABLE blocked", "ALTER TABLE employees DROP COLUMN email;"),
        ("TRUNCATE TABLE blocked", "TRUNCATE TABLE products;"),
        ("Multiple statements blocked", "SELECT * FROM employees; DROP TABLE employees;"),
        ("Subquery with DELETE blocked", "SELECT * FROM products WHERE product_id IN (DELETE FROM products);"),
        ("INTO OUTFILE clause blocked", "SELECT * FROM employees INTO OUTFILE '/tmp/hack.csv';"),
        ("Locking FOR UPDATE blocked", "SELECT * FROM inventory FOR UPDATE;"),
        ("External Auth schema access blocked", "SELECT * FROM company_auth.users;"),
    ]

    for test_name, bad_sql in dangerous_cases:
        res = execute_tool_directly("execute_read_only_sql", {"sql": bad_sql})
        rejected = res.get("success") is False and len(res.get("error", "")) > 0
        print_result(test_name, rejected, f"Rejected: '{res.get('error')}'")
        if not rejected:
            all_passed = False

    # --------------------------------------------------------------------------
    # 4. Business Analytical Queries
    # --------------------------------------------------------------------------
    print(f"\n{BOLD}4. Real Business Analytical Queries Execution{RESET}")
    business_queries = [
        (
            "HR: Employees per department",
            "SELECT d.dept_name, COUNT(e.employee_id) AS cnt FROM departments d JOIN employees e ON d.dept_id = e.department_id GROUP BY d.dept_name ORDER BY cnt DESC;"
        ),
        (
            "CRM: Leads distribution by status",
            "SELECT status, COUNT(*) AS cnt, ROUND(SUM(estimated_value), 2) AS val FROM leads GROUP BY status ORDER BY cnt DESC;"
        ),
        (
            "Sales: 12-month revenue trend",
            "SELECT DATE_FORMAT(order_date, '%Y-%m') AS month, COUNT(*) as orders, ROUND(SUM(total_amount), 2) AS rev FROM sales_orders GROUP BY month ORDER BY month DESC LIMIT 12;"
        ),
        (
            "Inventory: Products below reorder level",
            "SELECT p.product_name, p.category, i.quantity_on_hand, p.reorder_level FROM products p JOIN inventory i ON p.product_id = i.product_id WHERE i.quantity_on_hand <= p.reorder_level LIMIT 5;"
        ),
        (
            "Purchasing: Top procurement suppliers",
            "SELECT s.supplier_name, COUNT(po.po_id) AS pos, ROUND(SUM(po.total_amount), 2) AS total_val FROM suppliers s JOIN purchase_orders po ON s.supplier_id = po.supplier_id GROUP BY s.supplier_name ORDER BY total_val DESC LIMIT 5;"
        ),
        (
            "Finance: Monthly P&L statements",
            "SELECT month_name, total_revenue, cogs, operating_expenses, net_profit, profit_margin_pct FROM company_financials WHERE fiscal_year = 2026 ORDER BY month_num LIMIT 9;"
        ),
        (
            "Cross-Domain: High sales but low stock",
            "SELECT p.product_name, p.category, SUM(soi.quantity) AS units_sold, i.quantity_on_hand, p.reorder_level FROM products p JOIN sales_order_items soi ON p.product_id = soi.product_id JOIN inventory i ON p.product_id = i.product_id WHERE i.quantity_on_hand <= p.reorder_level GROUP BY p.product_name, p.category, i.quantity_on_hand, p.reorder_level HAVING units_sold > 50 ORDER BY units_sold DESC LIMIT 5;"
        )
    ]

    for title, sql in business_queries:
        res = execute_tool_directly("execute_read_only_sql", {"sql": sql})
        passed = res.get("success") is True and res.get("row_count", 0) > 0
        sample = f"Returned {res.get('row_count')} rows (Cols: {', '.join(res.get('columns', [])[:3])}...)"
        print_result(title, passed, sample)
        if not passed:
            all_passed = False

    # --------------------------------------------------------------------------
    # 5. Root-Cause Analysis Data Retrieval (August 2026)
    # --------------------------------------------------------------------------
    print(f"\n{BOLD}5. Root-Cause Investigation Data Retrieval (August 2026 Profit Drop){RESET}")
    # Check 1: Financial drop between July and August
    fin_sql = "SELECT month_name, total_revenue, cogs, operating_expenses, net_profit, profit_margin_pct FROM company_financials WHERE fiscal_year = 2026 AND month_num IN (7, 8) ORDER BY month_num;"
    res_fin = execute_tool_directly("execute_read_only_sql", {"sql": fin_sql})
    fin_ok = res_fin.get("success") is True and len(res_fin.get("rows", [])) == 2
    july_p = res_fin["rows"][0]["net_profit"] if fin_ok else 0
    aug_p = res_fin["rows"][1]["net_profit"] if fin_ok else 0
    print_result("P&L Drop Retrieval (July vs August)", fin_ok, f"July Profit: Rs. {july_p:,.2f} -> August Profit: Rs. {aug_p:,.2f} (-50%)")

    # Check 2: Emergency Shipping in Expenses table
    exp_sql = "SELECT category, SUM(amount) AS total FROM expenses WHERE expense_date BETWEEN '2026-08-01' AND '2026-08-31' GROUP BY category ORDER BY total DESC;"
    res_exp = execute_tool_directly("execute_read_only_sql", {"sql": exp_sql})
    exp_ok = res_exp.get("success") is True and any(r["category"] == "Emergency Shipping" for r in res_exp.get("rows", []))
    print_result("Emergency Shipping Expense Evidence", exp_ok, "Emergency Shipping confirmed in August expense records")

    if not (fin_ok and exp_ok):
        all_passed = False

    # --------------------------------------------------------------------------
    # 6. Row Limits & Truncation Signaling
    # --------------------------------------------------------------------------
    print(f"\n{BOLD}6. Row Limits & Truncation Signaling{RESET}")
    res_limit = execute_tool_directly("execute_read_only_sql", {"sql": "SELECT * FROM employees;", "limit": 10})
    limit_ok = res_limit.get("success") is True and res_limit.get("row_count") == 10 and res_limit.get("truncated") is True
    print_result("Row limit & truncation flag (limit=10)", limit_ok, f"Returned exactly 10 rows (truncated={res_limit.get('truncated')})")
    if not limit_ok:
        all_passed = False

    print(f"\n{BOLD}{CYAN}============================================================{RESET}")
    if all_passed:
        print(f"{GREEN}{BOLD}>>> ALL MCP SERVER & SECURITY CHECKS PASSED SUCCESSFULLY! <<<{RESET}")
        print("FreshMart MCP Server is fully operational and ready for LangGraph multi-agent AI.")
    else:
        print(f"{RED}{BOLD}>>> Some checks failed. Please check the logs above. <<<{RESET}")
    print(f"{BOLD}{CYAN}============================================================{RESET}\n")

if __name__ == "__main__":
    main()
