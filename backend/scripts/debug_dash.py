import traceback
from app.api.analytics import get_live_dashboard_metrics

class MockRole:
    role_name = "CEO"

class MockUser:
    user_id = 2
    full_name = "Vikram Malhotra"
    role = MockRole()
    permission_codes = ["VIEW_ALL"]

try:
    res = get_live_dashboard_metrics(range="30d", current_user=MockUser())
    print("Success! Keys:", res.model_dump().keys())
except Exception as e:
    traceback.print_exc()
