import os
import sys
import pymysql

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.core.config import settings

def setup_reader_user():
    print(f"Connecting to MySQL {settings.MYSQL_HOST}:{settings.MYSQL_PORT} as root...")
    conn = pymysql.connect(
        host=settings.MYSQL_HOST,
        port=settings.MYSQL_PORT,
        user=settings.MYSQL_USER,
        password=settings.MYSQL_PASSWORD,
        autocommit=True
    )
    cur = conn.cursor()
    mcp_user = "freshmart_mcp_reader"
    mcp_pass = "McpReaderPassword123!"

    print(f"Creating read-only user '{mcp_user}'...")
    cur.execute(f"CREATE USER IF NOT EXISTS '{mcp_user}'@'localhost' IDENTIFIED BY '{mcp_pass}';")
    cur.execute(f"ALTER USER '{mcp_user}'@'localhost' IDENTIFIED BY '{mcp_pass}';")
    cur.execute(f"CREATE USER IF NOT EXISTS '{mcp_user}'@'%' IDENTIFIED BY '{mcp_pass}';")
    cur.execute(f"ALTER USER '{mcp_user}'@'%' IDENTIFIED BY '{mcp_pass}';")
    
    print(f"Granting strict SELECT-only privileges on {settings.MYSQL_DB}.*...")
    cur.execute(f"REVOKE ALL PRIVILEGES, GRANT OPTION FROM '{mcp_user}'@'localhost';")
    cur.execute(f"REVOKE ALL PRIVILEGES, GRANT OPTION FROM '{mcp_user}'@'%';")
    cur.execute(f"GRANT SELECT ON `{settings.MYSQL_DB}`.* TO '{mcp_user}'@'localhost';")
    cur.execute(f"GRANT SELECT ON `{settings.MYSQL_DB}`.* TO '{mcp_user}'@'%';")
    cur.execute("FLUSH PRIVILEGES;")
    
    cur.close()
    conn.close()
    print("SUCCESS: freshmart_mcp_reader user created and configured with strict SELECT-only permissions!")

if __name__ == "__main__":
    setup_reader_user()
