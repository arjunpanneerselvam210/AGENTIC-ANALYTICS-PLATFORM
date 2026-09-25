"""
Pytest Suite for FreshMart MCP Database Server
Tests:
1. Discovery of tables via list_tables (and zero leakage of PostgreSQL auth tables).
2. Table structural inspection via describe_table across 5 core domains.
3. Strict SQL security boundary (rejection of UPDATE, DELETE, INSERT, DROP, ALTER, TRUNCATE, multi-statements).
4. Analytical SQL queries across HR, CRM, Sales, Inventory, Purchasing, Finance, and Cross-domain.
5. Root-Cause investigation data retrieval (August 2026 profit drop).
6. Result limits and truncation flags.
"""

import pytest
from mcp_server import execute_tool_directly

def test_mcp_list_tables():
    """Verify list_tables returns all FreshMart business tables and no auth tables."""
    res = execute_tool_directly("list_tables")
    assert res.get("success") is True, f"list_tables failed: {res.get('error')}"
    tables = res.get("tables", [])
    assert len(tables) >= 15, f"Expected at least 15 tables, found {len(tables)}"

    # Required FreshMart tables
    expected_tables = {
        "departments", "employees", "salaries", "customers", "leads",
        "customer_interactions", "suppliers", "products", "purchase_orders",
        "purchase_order_items", "inventory", "sales_orders", "sales_order_items",
        "expenses", "company_financials"
    }
    assert expected_tables.issubset(set(tables)), f"Missing tables: {expected_tables - set(tables)}"

    # Ensure zero leakage of PostgreSQL auth tables
    forbidden_tables = {"users", "roles", "permissions", "role_permissions"}
    leaked = forbidden_tables.intersection(set(tables))
    assert len(leaked) == 0, f"PostgreSQL tables leaked in MCP response: {leaked}"

@pytest.mark.parametrize("table_name", [
    "employees", "products", "sales_orders", "inventory", "expenses"
])
def test_mcp_describe_table_valid(table_name):
    """Verify describe_table returns columns, types, and foreign keys for core domains."""
    res = execute_tool_directly("describe_table", {"table_name": table_name})
    assert res.get("success") is True, f"describe_table failed for {table_name}: {res.get('error')}"
    assert res.get("table") == table_name
    assert res.get("column_count", 0) > 0
    assert len(res.get("columns", [])) == res.get("column_count")

    # Verify column structure
    col_names = [c["name"] for c in res["columns"]]
    if table_name == "employees":
        assert "employee_id" in col_names
        assert "department_id" in col_names
        assert "hire_date" in col_names
        assert len(res.get("foreign_keys", [])) >= 1
    elif table_name == "products":
        assert "product_id" in col_names
        assert "unit_cost" in col_names
        assert "unit_price" in col_names
    elif table_name == "sales_orders":
        assert "order_id" in col_names
        assert "total_amount" in col_names

def test_mcp_describe_table_invalid():
    """Verify describe_table returns structured error for non-existent table."""
    res = execute_tool_directly("describe_table", {"table_name": "ghost_table_xyz"})
    assert res.get("success") is False
    assert "does not exist" in res.get("error", "")

def test_mcp_execute_read_only_sql_select():
    """Verify standard SELECT queries execute and return structured columns and rows."""
    sql = "SELECT department_id, COUNT(*) AS emp_cnt FROM employees GROUP BY department_id ORDER BY emp_cnt DESC LIMIT 3;"
    res = execute_tool_directly("execute_read_only_sql", {"sql": sql})
    assert res.get("success") is True, f"Query failed: {res.get('error')}"
    assert res.get("columns") == ["department_id", "emp_cnt"]
    assert res.get("row_count") == 3
    assert len(res.get("rows")) == 3
    assert res.get("truncated") is False

def test_mcp_execute_read_only_sql_cte():
    """Verify Common Table Expressions (WITH ... SELECT) execute safely."""
    sql = """
        WITH regional_sales AS (
            SELECT region, SUM(total_amount) AS revenue
            FROM sales_orders
            GROUP BY region
        )
        SELECT region, revenue FROM regional_sales ORDER BY revenue DESC;
    """
    res = execute_tool_directly("execute_read_only_sql", {"sql": sql})
    assert res.get("success") is True, f"CTE query failed: {res.get('error')}"
    assert len(res.get("rows")) == 5

@pytest.mark.parametrize("destructive_sql,expected_keyword", [
    ("UPDATE employees SET status = 'Terminated';", "UPDATE"),
    ("DELETE FROM customers WHERE customer_id = 'C001';", "DELETE"),
    ("INSERT INTO departments (dept_id, dept_name, location) VALUES ('D99', 'Fake', 'Nowhere');", "INSERT"),
    ("DROP TABLE employees;", "DROP"),
    ("ALTER TABLE employees DROP COLUMN email;", "ALTER"),
    ("TRUNCATE TABLE products;", "TRUNCATE"),
    ("REPLACE INTO departments (dept_id, dept_name, location) VALUES ('D01', 'Replaced', 'Nowhere');", "REPLACE"),
    ("GRANT ALL PRIVILEGES ON *.* TO 'hacker'@'%';", "GRANT"),
    ("SELECT * FROM employees; DROP TABLE employees;", "Multiple"),
    ("SELECT * FROM employees INTO OUTFILE '/tmp/hack.csv';", "OUTFILE"),
    ("SELECT * FROM inventory FOR UPDATE;", "FOR UPDATE"),
    ("SELECT * FROM company_auth.users;", "company_auth"),
])
def test_mcp_execute_destructive_sql_rejected(destructive_sql, expected_keyword):
    """Verify that all destructive, mutating, multi-statement, and external schema operations are rejected."""
    res = execute_tool_directly("execute_read_only_sql", {"sql": destructive_sql})
    assert res.get("success") is False, f"Expected destructive query to be blocked: {destructive_sql}"
    assert expected_keyword.lower() in res.get("error", "").lower(), (
        f"Expected '{expected_keyword}' in error message: {res.get('error')}"
    )

def test_mcp_row_limits():
    """Verify that row limits are enforced and truncation is signaled."""
    res = execute_tool_directly("execute_read_only_sql", {"sql": "SELECT * FROM employees;", "limit": 15})
    assert res.get("success") is True
    assert res.get("row_count") == 15
    assert res.get("truncated") is True
    assert res.get("limit_applied") == 15

def test_mcp_business_queries():
    """Verify that real business analytics queries across all domains execute cleanly."""
    queries = [
        # HR
        "SELECT d.dept_name, COUNT(e.employee_id) AS cnt FROM departments d JOIN employees e ON d.dept_id = e.department_id GROUP BY d.dept_name;",
        # CRM
        "SELECT status, COUNT(*) AS cnt FROM leads GROUP BY status;",
        # Sales
        "SELECT DATE_FORMAT(order_date, '%Y-%m') AS month, ROUND(SUM(total_amount), 2) AS rev FROM sales_orders GROUP BY month ORDER BY month DESC LIMIT 6;",
        # Inventory
        "SELECT p.product_name, i.quantity_on_hand FROM products p JOIN inventory i ON p.product_id = i.product_id WHERE i.quantity_on_hand <= p.reorder_level LIMIT 5;",
        # Purchasing
        "SELECT s.supplier_name, ROUND(SUM(po.total_amount), 2) AS total_val FROM suppliers s JOIN purchase_orders po ON s.supplier_id = po.supplier_id GROUP BY s.supplier_name LIMIT 5;",
        # Finance
        "SELECT month_name, total_revenue, net_profit FROM company_financials WHERE fiscal_year = 2026 LIMIT 6;",
        # Cross-Domain: High sales, low stock
        "SELECT p.product_name, SUM(soi.quantity) AS sold, i.quantity_on_hand FROM products p JOIN sales_order_items soi ON p.product_id = soi.product_id JOIN inventory i ON p.product_id = i.product_id WHERE i.quantity_on_hand <= p.reorder_level GROUP BY p.product_name, i.quantity_on_hand HAVING sold > 50 LIMIT 5;"
    ]

    for sql in queries:
        res = execute_tool_directly("execute_read_only_sql", {"sql": sql})
        assert res.get("success") is True, f"Business query failed: {sql} | Error: {res.get('error')}"
        assert res.get("row_count", 0) > 0

def test_mcp_root_cause_data_accessibility():
    """Verify that data required to diagnose the August 2026 profit drop is accessible via MCP."""
    # 1. P&L gap
    pnl_res = execute_tool_directly("execute_read_only_sql", {
        "sql": "SELECT month_num, month_name, net_profit FROM company_financials WHERE fiscal_year = 2026 AND month_num IN (7, 8) ORDER BY month_num;"
    })
    assert pnl_res.get("success") is True
    rows = pnl_res.get("rows", [])
    assert len(rows) == 2
    assert rows[0]["net_profit"] > rows[1]["net_profit"]

    # 2. Corroborating expense surge
    exp_res = execute_tool_directly("execute_read_only_sql", {
        "sql": "SELECT category, SUM(amount) AS total FROM expenses WHERE expense_date BETWEEN '2026-08-01' AND '2026-08-31' GROUP BY category;"
    })
    assert exp_res.get("success") is True
    categories = [r["category"] for r in exp_res.get("rows", [])]
    assert "Emergency Shipping" in categories
