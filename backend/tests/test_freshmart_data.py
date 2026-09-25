"""
Tests for FreshMart business data volumes, mathematical consistency, and profit drop scenario.
"""
import pytest
from decimal import Decimal

def test_data_volumes(mysql_cursor):
    """Verify that all entity counts meet or exceed the target enterprise volumes."""
    table_expectations = {
        "departments": 10,
        "employees": 500,
        "salaries": 500,
        "customers": 300,
        "leads": 500,
        "customer_interactions": 1000,
        "suppliers": 30,
        "products": 200,
        "inventory": 200,
        "purchase_orders": 500,
        "purchase_order_items": 1200,
        "sales_orders": 2000,
        "sales_order_items": 4000,
        "expenses": 300,
        "company_financials": 12,
    }

    for table, min_count in table_expectations.items():
        mysql_cursor.execute(f"SELECT COUNT(*) FROM {table};")
        actual_count = mysql_cursor.fetchone()[0]
        assert actual_count >= min_count, (
            f"Table '{table}' has {actual_count} records, expected at least {min_count}"
        )

def test_employee_uniqueness_and_managers(mysql_cursor):
    """Verify no duplicate employees and that managers are real employee records."""
    mysql_cursor.execute("SELECT COUNT(*), COUNT(DISTINCT employee_id), COUNT(DISTINCT email) FROM employees;")
    total, distinct_ids, distinct_emails = mysql_cursor.fetchone()
    assert total == distinct_ids, "Duplicate employee_id found in employees table"
    assert total == distinct_emails, "Duplicate email found in employees table"

    # Verify CEO exists
    mysql_cursor.execute("SELECT employee_id, first_name, last_name, job_title FROM employees WHERE employee_id = 'E006';")
    ceo = mysql_cursor.fetchone()
    assert ceo is not None, "CEO E006 (Vikram Malhotra) not found"
    assert ceo[1] == "Vikram" and ceo[2] == "Malhotra"

    # Verify Sales Manager exists
    mysql_cursor.execute("SELECT employee_id, first_name, last_name, job_title FROM employees WHERE employee_id = 'E001';")
    sales_mgr = mysql_cursor.fetchone()
    assert sales_mgr is not None, "Sales Manager E001 (Arun Kumar) not found"
    assert sales_mgr[1] == "Arun" and sales_mgr[2] == "Kumar"

def test_sales_orders_mathematical_consistency(mysql_cursor):
    """Verify that every sales order total equals the sum of its order item subtotals."""
    mysql_cursor.execute("""
        SELECT so.order_id, so.total_amount, ROUND(SUM(soi.subtotal), 2) AS calculated_sum
        FROM sales_orders so
        JOIN sales_order_items soi ON so.order_id = soi.order_id
        GROUP BY so.order_id, so.total_amount
        HAVING ABS(so.total_amount - calculated_sum) > 0.05
        LIMIT 10;
    """)
    discrepancies = mysql_cursor.fetchall()
    assert len(discrepancies) == 0, f"Found sales order total discrepancies: {discrepancies}"

def test_purchase_orders_mathematical_consistency(mysql_cursor):
    """Verify that every purchase order total equals the sum of its PO item subtotals."""
    mysql_cursor.execute("""
        SELECT po.po_id, po.total_amount, ROUND(SUM(poi.subtotal), 2) AS calculated_sum
        FROM purchase_orders po
        JOIN purchase_order_items poi ON po.po_id = poi.po_id
        GROUP BY po.po_id, po.total_amount
        HAVING ABS(po.total_amount - calculated_sum) > 0.05
        LIMIT 10;
    """)
    discrepancies = mysql_cursor.fetchall()
    assert len(discrepancies) == 0, f"Found purchase order total discrepancies: {discrepancies}"

def test_company_financials_mathematical_consistency(mysql_cursor):
    """Verify financial formulas: total_expenses = cogs + operating_expenses, net_profit = revenue - expenses."""
    mysql_cursor.execute("""
        SELECT financial_id, fiscal_year, month_name, total_revenue, total_expenses,
               cogs, operating_expenses, net_profit, profit_margin_pct
        FROM company_financials;
    """)
    records = mysql_cursor.fetchall()
    assert len(records) >= 12, "Need at least 12 months of financial history"

    for row in records:
        f_id, yr, month, rev, exp, cogs, opex, net_p, margin = row
        rev, exp, cogs, opex, net_p, margin = (
            float(rev), float(exp), float(cogs), float(opex), float(net_p), float(margin)
        )

        assert abs(exp - (cogs + opex)) < 0.1, (
            f"{month} {yr}: Total expenses ({exp}) != COGS ({cogs}) + OpEx ({opex})"
        )
        assert abs(net_p - (rev - exp)) < 0.1, (
            f"{month} {yr}: Net profit ({net_p}) != Revenue ({rev}) - Expenses ({exp})"
        )
        expected_margin = round((net_p / rev) * 100, 2)
        assert abs(margin - expected_margin) < 0.1, (
            f"{month} {yr}: Margin ({margin}%) != calculated ({expected_margin}%)"
        )

def test_august_2026_profit_drop_scenario(mysql_cursor):
    """
    Verify the demonstrable profit-drop scenario in August 2026:
    - July 2026 profit is high (approx Rs 1.2M, ~28.5% margin)
    - August 2026 profit drops significantly (approx Rs 600K, ~15.5% margin)
    - August COGS is higher than July COGS
    - Emergency shipping expenses exist in August 2026 explaining the operating expense increase
    """
    mysql_cursor.execute("""
        SELECT month_num, month_name, total_revenue, cogs, operating_expenses, net_profit, profit_margin_pct
        FROM company_financials
        WHERE fiscal_year = 2026 AND month_num IN (7, 8)
        ORDER BY month_num;
    """)
    rows = mysql_cursor.fetchall()
    assert len(rows) == 2, "Expected financial records for July and August 2026"

    july = rows[0]
    august = rows[1]

    july_rev, july_cogs, july_opex, july_profit, july_margin = float(july[2]), float(july[3]), float(july[4]), float(july[5]), float(july[6])
    aug_rev, aug_cogs, aug_opex, aug_profit, aug_margin = float(august[2]), float(august[3]), float(august[4]), float(august[5]), float(august[6])

    # Profit dropped significantly
    assert aug_profit < july_profit, f"August profit ({aug_profit}) must be lower than July ({july_profit})"
    assert aug_profit <= july_profit * 0.6, "August profit should have dropped by at least 40%"
    assert aug_margin < july_margin, f"August margin ({aug_margin}%) must be lower than July ({july_margin}%)"

    # COGS escalated
    assert aug_cogs > july_cogs, f"August COGS ({aug_cogs}) should be higher than July ({july_cogs})"

    # Corroborating evidence in expenses table: Emergency Shipping in August
    mysql_cursor.execute("""
        SELECT category, SUM(amount) as total_amt, COUNT(*) as cnt
        FROM expenses
        WHERE expense_date BETWEEN '2026-08-01' AND '2026-08-31'
          AND category = 'Emergency Shipping'
        GROUP BY category;
    """)
    emergency_shipping = mysql_cursor.fetchone()
    assert emergency_shipping is not None, "Emergency shipping expenses must exist in August 2026"
    assert float(emergency_shipping[1]) >= 300000.00, "Emergency shipping in August 2026 should be substantial (>= Rs 300,000)"

def test_inventory_stock_states(mysql_cursor):
    """Verify that low-stock and out-of-stock products exist for cross-domain queries."""
    mysql_cursor.execute("""
        SELECT COUNT(*) 
        FROM inventory i 
        JOIN products p ON i.product_id = p.product_id 
        WHERE i.quantity_on_hand <= p.reorder_level;
    """)
    low_stock_count = mysql_cursor.fetchone()[0]
    assert low_stock_count >= 5, f"Expected at least 5 low-stock items, found {low_stock_count}"

    mysql_cursor.execute("SELECT COUNT(*) FROM inventory WHERE quantity_on_hand = 0;")
    out_of_stock_count = mysql_cursor.fetchone()[0]
    assert out_of_stock_count >= 1, "Expected at least 1 out-of-stock item"
