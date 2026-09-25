import httpx

client = httpx.Client(base_url="http://localhost:8000/api/v1", timeout=15.0)
login_res = client.post("/auth/login", data={"username": "ceo", "password": "CeoPassword123!"})
print("Login status:", login_res.status_code)
token = login_res.json()["access_token"]

dash_res = client.get("/analytics/dashboard?range=30d", headers={"Authorization": f"Bearer {token}"})
print("Dashboard status:", dash_res.status_code)
if dash_res.status_code == 200:
    data = dash_res.json()
    print("Range:", data.get("range"))
    print("KPIs:")
    for k in data.get("kpis", []):
        print(f"  {k['title']}: {k['value']} ({k['change']}) - {k['periodText']}")
    print(f"Sales trend points: {len(data.get('sales_trend', []))}")
    print(f"Categories: {len(data.get('category_distribution', []))}")
    print(f"Top products: {len(data.get('top_products', []))}")
    print(f"Insights: {len(data.get('insights', []))}")
else:
    print("Error:", dash_res.text)
