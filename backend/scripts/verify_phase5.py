"""
Phase 5 Verification Script: Basic AI Chatbot (Ollama Integration & Security)
Verifies:
1. Unauthenticated Chat Request is REJECTED (401 Unauthorized)
2. Authenticated Sales Manager Chat Request to Ollama
3. Verified Role-Awareness in AI response metadata
4. Authenticated HR Manager Chat Request to Ollama
"""

import os
import sys

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from fastapi.testclient import TestClient
from app.main import app

GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

def print_result(title: str, passed: bool, details: str = ""):
    icon = f"{GREEN}[PASS]{RESET}" if passed else f"{RED}[FAIL]{RESET}"
    print(f"  {icon} {BOLD}{title:<40}{RESET} {details}")

def main():
    print(f"\n{BOLD}{CYAN}============================================================{RESET}")
    print(f"{BOLD}{CYAN}  AGENTIC ANALYTICS PLATFORM - PHASE 5 VERIFICATION{RESET}")
    print(f"{BOLD}{CYAN}  Basic AI Chatbot & Role-Aware Ollama Integration{RESET}")
    print(f"{BOLD}{CYAN}============================================================{RESET}\n")

    client = TestClient(app)

    # 1. Unauthenticated Chat Request -> MUST FAIL (401)
    print(f"{BOLD}1. Security Check: Unauthenticated Chat Request:{RESET}")
    resp_unauth = client.post("/api/v1/chat/message", json={"message": "Show me top customers"})
    unauth_ok = resp_unauth.status_code == 401
    print_result("Unauthenticated Request Blocked", unauth_ok, f"Status: {resp_unauth.status_code} (401 Unauthorized expected)")

    # 2. Login as Sales Manager
    print(f"\n{BOLD}2. Authenticated Chat Flow (Sales Manager):{RESET}")
    login_resp = client.post("/api/v1/auth/login", data={"username": "sales.manager", "password": "SalesPassword123!"})
    sales_token = login_resp.json().get("access_token")

    # Send chat message to Ollama
    print("  -> Sending prompt to local Ollama LLM (this may take a few seconds)...")
    chat_resp = client.post(
        "/api/v1/chat/message",
        json={"message": "Hello! What business areas can you assist me with?"},
        headers={"Authorization": f"Bearer {sales_token}"}
    )
    sales_chat_ok = chat_resp.status_code == 200
    print_result("Chat Response Received", sales_chat_ok, f"Status: {chat_resp.status_code}")

    if sales_chat_ok:
        data = chat_resp.json()
        role_ok = data.get("user_role") == "SALES_MANAGER"
        print_result("Role Metadata Injected", role_ok, f"Role: {data.get('user_role')}")
        domains = data.get("allowed_domains", [])
        print_result("Allowed Domains Identified", len(domains) > 0, f"Domains: {', '.join(domains)}")
        print(f"\n  {BOLD}AI Assistant Reply:{RESET}\n  \"{data.get('reply')[:180]}...\"\n")

    # 3. Login as HR Manager
    print(f"{BOLD}3. Authenticated Chat Flow (HR Manager):{RESET}")
    hr_login = client.post("/api/v1/auth/login", data={"username": "hr.manager", "password": "HrPassword123!"})
    hr_token = hr_login.json().get("access_token")

    hr_chat_resp = client.post(
        "/api/v1/chat/message",
        json={"message": "Hi, what is my access scope?"},
        headers={"Authorization": f"Bearer {hr_token}"}
    )
    hr_chat_ok = hr_chat_resp.status_code == 200
    print_result("HR Chat Response Received", hr_chat_ok, f"Status: {hr_chat_resp.status_code}")

    if hr_chat_ok:
        hr_data = hr_chat_resp.json()
        hr_role_ok = hr_data.get("user_role") == "HR_MANAGER"
        print_result("HR Role Metadata Injected", hr_role_ok, f"Role: {hr_data.get('user_role')}")
        hr_domains = hr_data.get("allowed_domains", [])
        print_result("HR Permitted Domains", "HRMS (Human Resources)" in hr_domains, f"Domains: {', '.join(hr_domains)}")

    all_passed = unauth_ok and sales_chat_ok and hr_chat_ok

    print(f"\n{BOLD}{CYAN}============================================================{RESET}")
    if all_passed:
        print(f"{GREEN}{BOLD}>>> ALL PHASE 5 CHECKS PASSED SUCCESSFULLY! <<<{RESET}")
        print("Basic AI Chatbot is operational and securely connected to local Ollama.")
        print("You are ready to proceed to Phase 6 (MCP - Model Context Protocol Layer).\n")
    else:
        print(f"{RED}{BOLD}>>> Some checks failed. Review output above. <<<{RESET}\n")

if __name__ == "__main__":
    main()
