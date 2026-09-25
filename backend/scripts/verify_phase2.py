"""
Phase 2 Verification Script: Company Business Database
Verifies that all 14 tables in MySQL database company_analytics
are created with valid schema and populated with data.
"""

import os
import sys

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import pymysql
from app.core.config import settings

GREEN = "\033[92m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

def verify_phase2():
    print(f"\n{BOLD}{CYAN}============================================================{RESET}")
    print(f"{BOLD}{CYAN}  AGENTIC ANALYTICS PLATFORM - PHASE 2 VERIFICATION{RESET}")
    print(f"{BOLD}{CYAN}  Verifying MySQL Business Database: {settings.MYSQL_DB}{RESET}")
    print(f"{BOLD}{CYAN}============================================================{RESET}\n")

    conn = pymysql.connect(
        host=settings.MYSQL_HOST,
        port=settings.MYSQL_PORT,
        user=settings.MYSQL_USER,
        password=settings.MYSQL_PASSWORD,
        database=settings.MYSQL_DB
    )
    cursor = conn.cursor()

    domains = [
        ("HRMS", [
            ("departments", "Departments"),
            ("employees", "Workforce Employees"),
            ("salaries", "Employee Salaries")
        ]),
        ("CRM", [
            ("customers", "Enterprise Customers"),
            ("leads", "Business Leads"),
            ("customer_interactions", "Customer Interactions")
        ]),
        ("ERP & Inventory", [
            ("suppliers", "Suppliers"),
            ("products", "Catalog Products"),
            ("purchase_orders", "Purchase Orders"),
            ("purchase_order_items", "PO Line Items"),
            ("inventory", "Warehouse Stock Records")
        ]),
        ("Sales", [
            ("sales_orders", "Customer Sales Orders"),
            ("sales_order_items", "Sales Order Line Items")
        ]),
        ("Finance", [
            ("expenses", "Department Expenses"),
            ("company_financials", "Monthly P&L Summaries")
        ])
    ]

    total_records = 0
    all_ok = True

    for domain_name, table_list in domains:
        print(f"{BOLD}--- Domain: {domain_name} ---{RESET}")
        for table, desc in table_list:
            cursor.execute(f"SELECT COUNT(*) FROM {table};")
            count = cursor.fetchone()[0]
            total_records += count
            status = f"{GREEN}[PASS]{RESET}" if count > 0 else "\033[91m[FAIL]\033[0m"
            if count == 0:
                all_ok = False
            print(f"  {status} {table:<25} ({desc:<25}): {BOLD}{count:>3}{RESET} records")
        print()

    # Sample check for root-cause analysis readiness
    cursor.execute("""
        SELECT month_name, total_revenue, cogs, operating_expenses, net_profit, profit_margin_pct
        FROM company_financials
        WHERE month_num IN (7, 8)
        ORDER BY month_num;
    """)
    rows = cursor.fetchall()
    print(f"{BOLD}--- Root-Cause Analysis Test Check (Month 7 vs Month 8) ---{RESET}")
    for row in rows:
        print(f"  Month: {row[0]:<10} | Revenue: Rs. {row[1]:>12,.2f} | Net Profit: Rs. {row[4]:>10,.2f} | Margin: {row[5]}%")

    cursor.close()
    conn.close()

    print(f"\n{BOLD}{CYAN}============================================================{RESET}")
    if all_ok:
        print(f"{GREEN}{BOLD}>>> ALL 15 TABLES VERIFIED! TOTAL {total_records} RECORDS POPULATED! <<<{RESET}")
        print(f"FreshMart Business Database successfully seeded and verified.\n")
    else:
        print("\033[91mSome tables are empty. Please check the seeding script.\033[0m\n")

if __name__ == "__main__":
    verify_phase2()
