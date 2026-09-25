"""
Tests for MySQL and PostgreSQL database schemas and foreign key integrity.
"""
import pytest
from sqlalchemy import text

def test_mysql_tables_exist(mysql_cursor):
    """Verify that all 15 expected tables in FreshMart MySQL business database exist."""
    expected_tables = {
        "departments",
        "employees",
        "salaries",
        "customers",
        "leads",
        "customer_interactions",
        "suppliers",
        "products",
        "purchase_orders",
        "purchase_order_items",
        "inventory",
        "sales_orders",
        "sales_order_items",
        "expenses",
        "company_financials"
    }
    mysql_cursor.execute("SHOW TABLES;")
    existing_tables = {row[0] for row in mysql_cursor.fetchall()}
    for table in expected_tables:
        assert table in existing_tables, f"Expected table '{table}' is missing from MySQL"

def test_mysql_interactions_view_exists(mysql_cursor):
    """Verify that the interactions view exists and is queryable."""
    mysql_cursor.execute("SELECT COUNT(*) FROM interactions;")
    count = mysql_cursor.fetchone()[0]
    assert count >= 1000, f"Expected at least 1000 interactions, found {count}"

def test_postgres_auth_tables_exist(postgres_db):
    """Verify that all required tables in PostgreSQL auth database exist."""
    expected_tables = ["roles", "permissions", "role_permissions", "users"]
    result = postgres_db.execute(text(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
    ))
    existing_tables = [row[0] for row in result.fetchall()]
    for table in expected_tables:
        assert table in existing_tables, f"Expected PostgreSQL table '{table}' is missing"

def test_mysql_foreign_key_integrity_employees(mysql_cursor):
    """Verify all employees reference a valid department and manager."""
    mysql_cursor.execute("""
        SELECT e.employee_id 
        FROM employees e 
        LEFT JOIN departments d ON e.department_id = d.dept_id 
        WHERE d.dept_id IS NULL;
    """)
    orphans = mysql_cursor.fetchall()
    assert len(orphans) == 0, f"Employees with invalid department_id: {orphans}"

    mysql_cursor.execute("""
        SELECT e.employee_id, e.manager_id 
        FROM employees e 
        LEFT JOIN employees m ON e.manager_id = m.employee_id 
        WHERE e.manager_id IS NOT NULL AND m.employee_id IS NULL;
    """)
    orphan_managers = mysql_cursor.fetchall()
    assert len(orphan_managers) == 0, f"Employees with invalid manager_id: {orphan_managers}"

def test_mysql_foreign_key_integrity_salaries(mysql_cursor):
    """Verify every salary record references an existing employee."""
    mysql_cursor.execute("""
        SELECT s.salary_id 
        FROM salaries s 
        LEFT JOIN employees e ON s.employee_id = e.employee_id 
        WHERE e.employee_id IS NULL;
    """)
    orphans = mysql_cursor.fetchall()
    assert len(orphans) == 0, f"Salaries with invalid employee_id: {orphans}"

def test_mysql_foreign_key_integrity_sales(mysql_cursor):
    """Verify sales orders and items reference valid customers, sales reps, and products."""
    mysql_cursor.execute("""
        SELECT so.order_id 
        FROM sales_orders so 
        LEFT JOIN customers c ON so.customer_id = c.customer_id 
        WHERE c.customer_id IS NULL;
    """)
    assert len(mysql_cursor.fetchall()) == 0, "Sales orders with invalid customer_id found"

    mysql_cursor.execute("""
        SELECT so.order_id 
        FROM sales_orders so 
        LEFT JOIN employees e ON so.sales_rep_id = e.employee_id 
        WHERE e.employee_id IS NULL;
    """)
    assert len(mysql_cursor.fetchall()) == 0, "Sales orders with invalid sales_rep_id found"

    mysql_cursor.execute("""
        SELECT soi.item_id 
        FROM sales_order_items soi 
        LEFT JOIN sales_orders so ON soi.order_id = so.order_id 
        WHERE so.order_id IS NULL;
    """)
    assert len(mysql_cursor.fetchall()) == 0, "Sales order items with invalid order_id found"

    mysql_cursor.execute("""
        SELECT soi.item_id 
        FROM sales_order_items soi 
        LEFT JOIN products p ON soi.product_id = p.product_id 
        WHERE p.product_id IS NULL;
    """)
    assert len(mysql_cursor.fetchall()) == 0, "Sales order items with invalid product_id found"

def test_mysql_foreign_key_integrity_purchasing(mysql_cursor):
    """Verify purchase orders and items reference valid suppliers and products."""
    mysql_cursor.execute("""
        SELECT po.po_id 
        FROM purchase_orders po 
        LEFT JOIN suppliers s ON po.supplier_id = s.supplier_id 
        WHERE s.supplier_id IS NULL;
    """)
    assert len(mysql_cursor.fetchall()) == 0, "Purchase orders with invalid supplier_id found"

    mysql_cursor.execute("""
        SELECT poi.item_id 
        FROM purchase_order_items poi 
        LEFT JOIN purchase_orders po ON poi.po_id = po.po_id 
        WHERE po.po_id IS NULL;
    """)
    assert len(mysql_cursor.fetchall()) == 0, "Purchase order items with invalid po_id found"

    mysql_cursor.execute("""
        SELECT poi.item_id 
        FROM purchase_order_items poi 
        LEFT JOIN products p ON poi.product_id = p.product_id 
        WHERE p.product_id IS NULL;
    """)
    assert len(mysql_cursor.fetchall()) == 0, "Purchase order items with invalid product_id found"

def test_mysql_foreign_key_integrity_crm(mysql_cursor):
    """Verify customer interactions and leads have valid relationships."""
    mysql_cursor.execute("""
        SELECT ci.interaction_id 
        FROM customer_interactions ci 
        LEFT JOIN customers c ON ci.customer_id = c.customer_id 
        WHERE c.customer_id IS NULL;
    """)
    assert len(mysql_cursor.fetchall()) == 0, "Interactions with invalid customer_id found"

    mysql_cursor.execute("""
        SELECT ci.interaction_id 
        FROM customer_interactions ci 
        LEFT JOIN employees e ON ci.employee_id = e.employee_id 
        WHERE e.employee_id IS NULL;
    """)
    assert len(mysql_cursor.fetchall()) == 0, "Interactions with invalid employee_id found"

    mysql_cursor.execute("""
        SELECT l.lead_id 
        FROM leads l 
        LEFT JOIN customers c ON l.converted_customer_id = c.customer_id 
        WHERE l.converted_customer_id IS NOT NULL AND c.customer_id IS NULL;
    """)
    assert len(mysql_cursor.fetchall()) == 0, "Converted leads with invalid customer_id found"
