from mcp_server.database import MCPDatabaseManager
mgr = MCPDatabaseManager()
pnl = mgr.execute_read_only_query("SELECT month_name, total_revenue, cogs, operating_expenses, net_profit, profit_margin_pct FROM company_financials WHERE fiscal_year = 2026 AND month_num IN (7, 8) ORDER BY month_num ASC;")
print("July vs August PnL:")
for r in pnl["rows"]:
    print(r)

aug_exp = mgr.execute_read_only_query("SELECT category, description, amount FROM expenses WHERE expense_date BETWEEN '2026-08-01' AND '2026-08-31' ORDER BY amount DESC LIMIT 5;")
print("\nAugust Top Expenses:")
for r in aug_exp["rows"]:
    print(r)
