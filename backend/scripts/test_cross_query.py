from mcp_server.database import MCPDatabaseManager
mgr = MCPDatabaseManager()

cross_sql = """
SELECT p.product_name, p.category, ROUND(SUM(soi.subtotal), 2) AS total_revenue, SUM(soi.quantity) AS units_sold, i.quantity_on_hand, p.reorder_level
FROM products p
JOIN sales_order_items soi ON p.product_id = soi.product_id
JOIN inventory i ON p.product_id = i.product_id
WHERE i.quantity_on_hand <= p.reorder_level
GROUP BY p.product_id, p.product_name, p.category, i.quantity_on_hand, p.reorder_level
ORDER BY total_revenue DESC
LIMIT 10;
"""

res = mgr.execute_read_only_query(cross_sql)
print("Cross-domain (High Revenue & Low Stock):")
for r in res["rows"]:
    print(r)
