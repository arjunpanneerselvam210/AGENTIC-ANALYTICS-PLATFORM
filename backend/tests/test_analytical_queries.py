"""
Tests verifying the required analytical demonstration queries from Section 23.
"""
import pytest

def test_query_hr_employees_per_department(mysql_cursor):
    """Query: How many employees are in each department?"""
    query = """
        SELECT d.dept_id, d.dept_name, COUNT(e.employee_id) AS employee_count
        FROM departments d
        LEFT JOIN employees e ON d.dept_id = e.department_id
        GROUP BY d.dept_id, d.dept_name
        ORDER BY employee_count DESC;
    """
    mysql_cursor.execute(query)
    results = mysql_cursor.fetchall()
    assert len(results) == 10, "Expected all 10 departments in employee distribution"
    total_employees = sum(r[2] for r in results)
    assert total_employees == 500, f"Expected 500 total employees across departments, found {total_employees}"

def test_query_hr_average_salary_by_department(mysql_cursor):
    """Query: What is the average salary by department?"""
    query = """
        SELECT d.dept_name, ROUND(AVG(s.base_salary), 2) AS avg_salary, SUM(s.base_salary) AS total_payroll
        FROM departments d
        JOIN employees e ON d.dept_id = e.department_id
        JOIN salaries s ON e.employee_id = s.employee_id
        GROUP BY d.dept_id, d.dept_name
        ORDER BY avg_salary DESC;
    """
    mysql_cursor.execute(query)
    results = mysql_cursor.fetchall()
    assert len(results) == 10
    # Executive Leadership should have highest average salary
    top_dept = results[0]
    assert "Executive" in top_dept[0], f"Executive department expected to have highest avg salary, got {top_dept[0]}"
    assert float(top_dept[1]) > 100000.00

def test_query_crm_leads_by_status(mysql_cursor):
    """Query: How many leads exist by status?"""
    query = """
        SELECT status, COUNT(*) AS lead_count, ROUND(SUM(estimated_value), 2) AS total_pipeline
        FROM leads
        GROUP BY status
        ORDER BY lead_count DESC;
    """
    mysql_cursor.execute(query)
    results = mysql_cursor.fetchall()
    statuses = {r[0] for r in results}
    expected_statuses = {"New", "Contacted", "Qualified", "Lost", "Converted"}
    assert expected_statuses.issubset(statuses), f"Missing lead statuses: {expected_statuses - statuses}"
    total_leads = sum(r[1] for r in results)
    assert total_leads >= 500

def test_query_crm_top_sales_rep_by_leads(mysql_cursor):
    """Query: Which sales representative has the most leads?"""
    query = """
        SELECT e.employee_id, CONCAT(e.first_name, ' ', e.last_name) AS rep_name,
               COUNT(l.lead_id) AS lead_count, ROUND(SUM(l.estimated_value), 2) AS total_lead_value
        FROM employees e
        JOIN leads l ON e.employee_id = l.assigned_employee_id
        GROUP BY e.employee_id, rep_name
        ORDER BY lead_count DESC
        LIMIT 5;
    """
    mysql_cursor.execute(query)
    results = mysql_cursor.fetchall()
    assert len(results) > 0
    top_rep = results[0]
    assert top_rep[2] > 0, "Top sales rep should have assigned leads"

def test_query_sales_total_sales_by_month(mysql_cursor):
    """Query: What are total sales by month?"""
    query = """
        SELECT DATE_FORMAT(order_date, '%Y-%m') AS sales_month,
               COUNT(order_id) AS total_orders,
               ROUND(SUM(total_amount), 2) AS monthly_revenue
        FROM sales_orders
        GROUP BY sales_month
        ORDER BY sales_month ASC;
    """
    mysql_cursor.execute(query)
    results = mysql_cursor.fetchall()
    assert len(results) >= 12, f"Expected at least 12 months of sales history, found {len(results)}"
    for r in results:
        assert float(r[2]) > 0.00, f"Month {r[0]} revenue must be greater than zero"

def test_query_sales_top_revenue_products(mysql_cursor):
    """Query: Which products generated the highest revenue?"""
    query = """
        SELECT p.product_id, p.product_name, p.category,
               SUM(soi.quantity) AS total_units_sold,
               ROUND(SUM(soi.subtotal), 2) AS total_revenue
        FROM products p
        JOIN sales_order_items soi ON p.product_id = soi.product_id
        GROUP BY p.product_id, p.product_name, p.category
        ORDER BY total_revenue DESC
        LIMIT 5;
    """
    mysql_cursor.execute(query)
    results = mysql_cursor.fetchall()
    assert len(results) == 5
    assert float(results[0][4]) > float(results[4][4])

def test_query_inventory_low_in_stock(mysql_cursor):
    """Query: Which products are low in stock?"""
    query = """
        SELECT p.product_id, p.product_name, p.category,
               i.quantity_on_hand, p.reorder_level,
               (p.reorder_level - i.quantity_on_hand) AS stock_deficit
        FROM products p
        JOIN inventory i ON p.product_id = i.product_id
        WHERE i.quantity_on_hand <= p.reorder_level
        ORDER BY i.quantity_on_hand ASC;
    """
    mysql_cursor.execute(query)
    results = mysql_cursor.fetchall()
    assert len(results) >= 5, "Expected at least 5 low-stock products"

def test_query_purchasing_highest_value_suppliers(mysql_cursor):
    """Query: Which suppliers have the highest purchase value?"""
    query = """
        SELECT s.supplier_id, s.supplier_name, s.city,
               COUNT(po.po_id) AS total_pos,
               ROUND(SUM(po.total_amount), 2) AS total_procurement_value
        FROM suppliers s
        JOIN purchase_orders po ON s.supplier_id = po.supplier_id
        GROUP BY s.supplier_id, s.supplier_name, s.city
        ORDER BY total_procurement_value DESC
        LIMIT 5;
    """
    mysql_cursor.execute(query)
    results = mysql_cursor.fetchall()
    assert len(results) == 5
    assert float(results[0][4]) > 0

def test_query_finance_monthly_pnl(mysql_cursor):
    """Query: What is monthly revenue, expense, and profit?"""
    query = """
        SELECT fiscal_year, month_num, month_name,
               total_revenue, total_expenses, net_profit, profit_margin_pct
        FROM company_financials
        ORDER BY fiscal_year, month_num;
    """
    mysql_cursor.execute(query)
    results = mysql_cursor.fetchall()
    assert len(results) >= 12, "Expected at least 12 months of P&L history"

def test_query_cross_domain_high_sales_low_inventory(mysql_cursor):
    """Query: Which high-selling products currently have low inventory?"""
    query = """
        SELECT p.product_id, p.product_name, p.category,
               SUM(soi.quantity) AS units_sold,
               i.quantity_on_hand, p.reorder_level
        FROM products p
        JOIN sales_order_items soi ON p.product_id = soi.product_id
        JOIN inventory i ON p.product_id = i.product_id
        WHERE i.quantity_on_hand <= p.reorder_level
        GROUP BY p.product_id, p.product_name, p.category, i.quantity_on_hand, p.reorder_level
        HAVING units_sold > 50
        ORDER BY units_sold DESC;
    """
    mysql_cursor.execute(query)
    results = mysql_cursor.fetchall()
    assert len(results) >= 1, "Expected at least one high-sales low-stock product for cross-domain analytics"

def test_query_root_cause_august_profit_drop(mysql_cursor):
    """
    Query: Why did profit decrease in August?
    Demonstrates that querying multiple tables reveals:
    1. Financials: Net profit fell from 1,200,000 (July) to 600,000 (August)
    2. COGS escalated from 1,800,000 to 1,950,000
    3. OpEx escalated from 1,200,000 to 1,300,000
    4. Underlying Expenses reveals Emergency Shipping spiked to Rs. 430,000 in August
    """
    # Step 1: Query financials
    mysql_cursor.execute("""
        SELECT month_num, month_name, total_revenue, cogs, operating_expenses, net_profit, profit_margin_pct
        FROM company_financials
        WHERE fiscal_year = 2026 AND month_num IN (7, 8)
        ORDER BY month_num;
    """)
    fin_rows = mysql_cursor.fetchall()
    july_fin, aug_fin = fin_rows[0], fin_rows[1]
    profit_diff = float(july_fin[5]) - float(aug_fin[5])
    assert profit_diff >= 500000.00, "Profit drop between July and August should be >= Rs. 500,000"

    # Step 2: Query root cause in expenses
    mysql_cursor.execute("""
        SELECT category, SUM(amount) AS total_category_expense
        FROM expenses
        WHERE expense_date BETWEEN '2026-08-01' AND '2026-08-31'
        GROUP BY category
        ORDER BY total_category_expense DESC;
    """)
    expense_breakdown = dict(mysql_cursor.fetchall())
    assert "Emergency Shipping" in expense_breakdown, "Emergency shipping must appear in August expenses"
    assert float(expense_breakdown["Emergency Shipping"]) >= 400000.00, (
        f"Emergency shipping in August was {expense_breakdown['Emergency Shipping']}, expected >= 400000"
    )
