from mcp_server.database import MCPDatabaseManager
mgr = MCPDatabaseManager()

trend = mgr.execute_read_only_query("SELECT DATE_FORMAT(order_date, '%b %y') AS month, ROUND(SUM(total_amount), 2) AS revenue, COUNT(order_id) AS orders FROM sales_orders GROUP BY DATE_FORMAT(order_date, '%Y-%m'), month ORDER BY DATE_FORMAT(order_date, '%Y-%m') ASC LIMIT 12;")
print("Trend rows:", len(trend["rows"]))

cats = mgr.execute_read_only_query("SELECT p.category AS name, ROUND(SUM(soi.subtotal), 2) AS value FROM sales_order_items soi JOIN products p ON soi.product_id = p.product_id GROUP BY p.category ORDER BY value DESC;")
print("Categories:", len(cats["rows"]))

low = mgr.execute_read_only_query("SELECT COUNT(*) AS low_stock_count FROM inventory i JOIN products p ON i.product_id = p.product_id WHERE i.quantity_on_hand <= p.reorder_level;")
print("Low stock count:", low["rows"][0]["low_stock_count"])
