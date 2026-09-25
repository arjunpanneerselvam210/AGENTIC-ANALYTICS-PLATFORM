"""
Automated PostgreSQL Database Initialization & Seeding Script
Populates company_auth with:
- 7 Enterprise Application Roles
- 11 Granular Permissions
- Role-Permission Mappings
- Initial Admin and Manager Application Accounts (with bcrypt password hashes)
"""

import os
import sys

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from app.core.config import settings
from app.core.security import get_password_hash

def run_seed():
    print(f"\n============================================================")
    print(f"  INITIALIZING & SEEDING AUTH DATABASE (PostgreSQL)")
    print(f"  Host: {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT} | DB: {settings.POSTGRES_DB}")
    print(f"============================================================")

    # 1. Connect to postgres database to ensure company_auth exists
    print("[1/6] Connecting to PostgreSQL server...")
    conn = psycopg2.connect(
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        dbname="postgres"
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()

    cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{settings.POSTGRES_DB}';")
    exists = cursor.fetchone()
    if not exists:
        print(f"Creating database '{settings.POSTGRES_DB}'...")
        cursor.execute(f"CREATE DATABASE {settings.POSTGRES_DB};")
    else:
        print(f"Database '{settings.POSTGRES_DB}' already exists.")
    cursor.close()
    conn.close()

    # 2. Connect to company_auth database
    print(f"[2/6] Applying schema to '{settings.POSTGRES_DB}'...")
    conn = psycopg2.connect(
        host=settings.POSTGRES_HOST,
        port=settings.POSTGRES_PORT,
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        dbname=settings.POSTGRES_DB
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()

    schema_path = os.path.join(BACKEND_DIR, "app", "db", "postgres_schema.sql")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    cursor.execute(schema_sql)

    # Clean existing data for clean re-seed
    cursor.execute("TRUNCATE TABLE users, role_permissions, permissions, roles RESTART IDENTITY CASCADE;")

    # 3. Seed Roles
    print("[3/6] Seeding Roles...")
    roles = [
        ("ADMIN", "System & Technical Administrator. Manages users, roles, and settings."),
        ("CEO", "Chief Executive Officer. Full company-wide business analytics access."),
        ("HR_MANAGER", "HR Manager. Manages employees, salaries, and workforce reports."),
        ("ERP_MANAGER", "ERP Operations Manager. Integrated operations, procurement, stock, and expenses."),
        ("SALES_MANAGER", "Sales Manager. Customers, CRM, orders, and sales trends."),
        ("INVENTORY_MANAGER", "Inventory Manager. Products, warehouse stock, and suppliers."),
        ("FINANCE_MANAGER", "Finance Manager. Revenue, expenses, P&L statements, and profit margins."),
    ]
    cursor.executemany(
        "INSERT INTO roles (role_name, description) VALUES (%s, %s)",
        roles
    )

    # 4. Seed Permissions
    print("[4/6] Seeding Permissions...")
    permissions = [
        # HRMS
        ("VIEW_HR", "HRMS", "View departments, employees, and workforce directory"),
        ("VIEW_EMPLOYEE_SALARY", "HRMS", "View sensitive employee salary records and bonuses"),
        # CRM & Sales
        ("VIEW_CRM", "CRM", "View customers, leads, and customer interactions"),
        ("VIEW_SALES", "Sales", "View sales orders, order items, and regional revenue"),
        # ERP & Inventory
        ("VIEW_INVENTORY", "Inventory", "View products, stock levels, and warehouse inventory"),
        ("VIEW_PURCHASES", "Purchases", "View suppliers and purchase orders"),
        # Finance
        ("VIEW_FINANCE", "Finance", "View overall company financials and revenue"),
        ("VIEW_PROFIT", "Finance", "View net profit, margins, and root-cause profit trends"),
        ("VIEW_EXPENSES", "Finance", "View department expenditures and operational costs"),
        # Admin Operations
        ("MANAGE_USERS", "Admin", "Create, edit, enable, and disable application user accounts"),
        ("MANAGE_ROLES", "Admin", "Assign and change application roles and permissions"),
    ]
    cursor.executemany(
        "INSERT INTO permissions (permission_code, category, description) VALUES (%s, %s, %s)",
        permissions
    )

    # Retrieve mapped IDs
    cursor.execute("SELECT role_name, role_id FROM roles;")
    role_map = dict(cursor.fetchall())

    cursor.execute("SELECT permission_code, permission_id FROM permissions;")
    perm_map = dict(cursor.fetchall())

    # 5. Seed Role-Permissions Mapping
    print("[5/6] Assigning Permissions to Roles...")
    role_perm_assignments = {
        "ADMIN": [
            "MANAGE_USERS",
            "MANAGE_ROLES"
        ],
        "CEO": [
            "VIEW_HR",
            "VIEW_EMPLOYEE_SALARY",
            "VIEW_CRM",
            "VIEW_SALES",
            "VIEW_INVENTORY",
            "VIEW_PURCHASES",
            "VIEW_FINANCE",
            "VIEW_PROFIT",
            "VIEW_EXPENSES"
        ],
        "HR_MANAGER": [
            "VIEW_HR",
            "VIEW_EMPLOYEE_SALARY",
            "VIEW_EXPENSES"
        ],
        "ERP_MANAGER": [
            "VIEW_PURCHASES",
            "VIEW_INVENTORY",
            "VIEW_SALES",
            "VIEW_EXPENSES",
            "VIEW_HR"
        ],
        "SALES_MANAGER": [
            "VIEW_CRM",
            "VIEW_SALES",
            "VIEW_INVENTORY"
        ],
        "INVENTORY_MANAGER": [
            "VIEW_INVENTORY",
            "VIEW_PURCHASES",
            "VIEW_SALES"
        ],
        "FINANCE_MANAGER": [
            "VIEW_FINANCE",
            "VIEW_PROFIT",
            "VIEW_EXPENSES",
            "VIEW_SALES"
        ]
    }

    role_perms_tuples = []
    for role_name, perm_codes in role_perm_assignments.items():
        r_id = role_map[role_name]
        for p_code in perm_codes:
            p_id = perm_map[p_code]
            role_perms_tuples.append((r_id, p_id))

    cursor.executemany(
        "INSERT INTO role_permissions (role_id, permission_id) VALUES (%s, %s)",
        role_perms_tuples
    )

    # 6. Seed Application Users
    print("[6/6] Creating Initial Application Users (with bcrypt hashed passwords)...")
    users = [
        ("admin", "admin@freshmart.local", "AdminPassword123!", "ADMIN", None, "Technical Administrator"),
        ("ceo", "ceo@freshmart.local", "CeoPassword123!", "CEO", "E006", "Vikram Malhotra"),
        ("hr.manager", "hr@freshmart.local", "HrPassword123!", "HR_MANAGER", "E002", "Priya Sharma"),
        ("sales.manager", "sales@freshmart.local", "SalesPassword123!", "SALES_MANAGER", "E001", "Arun Kumar"),
        ("inventory.manager", "inventory@freshmart.local", "InventoryPassword123!", "INVENTORY_MANAGER", "E005", "Karthik Raj"),
        ("finance.manager", "finance@freshmart.local", "FinancePassword123!", "FINANCE_MANAGER", "E003", "Rahul Kumar"),
        ("erp.manager", "erp@freshmart.local", "ErpPassword123!", "ERP_MANAGER", "E007", "Anita Desai"),
    ]

    for u in users:
        username, email, raw_pwd, role_name, emp_id, full_name = u
        pwd_hash = get_password_hash(raw_pwd)
        r_id = role_map[role_name]
        cursor.execute(
            """INSERT INTO users (username, email, password_hash, role_id, employee_id, full_name, is_active)
               VALUES (%s, %s, %s, %s, %s, %s, TRUE)""",
            (username, email, pwd_hash, r_id, emp_id, full_name)
        )

    cursor.close()
    conn.close()

    print(f"\n============================================================")
    print(f"  POSTGRESQL AUTH DATABASE SUCCESSFULLY SEEDED!")
    print(f"============================================================\n")

if __name__ == "__main__":
    run_seed()
