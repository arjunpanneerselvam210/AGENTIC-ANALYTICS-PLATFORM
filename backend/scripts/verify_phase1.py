"""
Phase 1 Verification Script: Agentic Analytics Platform
Checks all local services and components without Docker:
1. Python Environment & Virtualenv
2. Ollama Local LLM Server & Required Models
3. MySQL Database Server (Company Data)
4. PostgreSQL Database Server (Auth & Metadata)
5. FastAPI Backend Dependencies
6. React Frontend Scaffolding
"""
import sys
import os
import json
import urllib.request
import urllib.error

# Add backend directory to sys.path so app modules can be imported
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

def print_header(title: str):
    print(f"\n{BOLD}{CYAN}{'='*60}{RESET}")
    print(f"{BOLD}{CYAN}  {title}{RESET}")
    print(f"{BOLD}{CYAN}{'='*60}{RESET}")

def print_result(name: str, passed: bool, details: str = ""):
    status_icon = f"{GREEN}[PASS]{RESET}" if passed else f"{RED}[FAIL]{RESET}"
    print(f"{status_icon} {BOLD}{name:<32}{RESET} {details}")

def verify_python():
    print_header("1. Python Environment")
    py_ver = sys.version.split(" ")[0]
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    print_result("Python Executable", True, sys.executable)
    print_result("Python Version", sys.version_info >= (3, 10), f"v{py_ver} (Minimum required: 3.10+)")
    print_result("Virtual Environment Active", in_venv, f"Prefix: {sys.prefix}")
    return in_venv

def verify_ollama():
    print_header("2. Ollama Local LLM Server")
    base_url = "http://localhost:11434"
    try:
        req = urllib.request.Request(f"{base_url}/api/tags", headers={"User-Agent": "Phase1Verifier"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode())
            models = [m.get("name", "") for m in data.get("models", [])]
            print_result("Ollama Server Running", True, f"Accessible at {base_url}")
            
            llama_ready = any("llama3.1" in m for m in models)
            qwen_ready = any("qwen2.5-coder" in m for m in models)
            
            print_result("Agent Model (llama3.1)", llama_ready, f"Models found: {', '.join(models)}")
            print_result("SQL Model (qwen2.5-coder)", qwen_ready, "Ready for code & SQL generation")
            return True
    except urllib.error.URLError as e:
        print_result("Ollama Server Running", False, f"Could not connect to {base_url}: {e.reason}")
        print(f"  {YELLOW}Tip: Start Ollama by typing 'ollama serve' in a terminal.{RESET}")
        return False

def verify_mysql():
    print_header("3. MySQL Database Server (Company Data)")
    try:
        from app.core.config import settings
        import pymysql
        conn = pymysql.connect(
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
            connect_timeout=3
        )
        with conn.cursor() as cursor:
            cursor.execute("SELECT VERSION();")
            version = cursor.fetchone()
        conn.close()
        print_result("MySQL Connection", True, f"Host: {settings.MYSQL_HOST}:{settings.MYSQL_PORT}, User: {settings.MYSQL_USER}")
        print_result("MySQL Server Version", True, version[0] if version else "Unknown")
        return True
    except Exception as e:
        print_result("MySQL Connection", False, str(e))
        return False

def verify_postgres():
    print_header("4. PostgreSQL Database Server (Auth & Metadata)")
    try:
        from app.core.config import settings
        import psycopg2
        conn = psycopg2.connect(
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            dbname="postgres",
            connect_timeout=3
        )
        with conn.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
        conn.close()
        print_result("PostgreSQL Connection", True, f"Host: {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}, User: {settings.POSTGRES_USER}")
        print_result("PostgreSQL Server Version", True, version[0].split(",")[0] if version else "Unknown")
        return True
    except Exception as e:
        print_result("PostgreSQL Connection", False, str(e))
        return False

def verify_backend_libraries():
    print_header("5. FastAPI & Agent Framework Dependencies")
    modules = [
        ("FastAPI", "fastapi"),
        ("Uvicorn", "uvicorn"),
        ("SQLAlchemy", "sqlalchemy"),
        ("Pydantic", "pydantic"),
        ("LangGraph", "langgraph"),
        ("LangChain Core", "langchain_core"),
        ("LangChain Ollama", "langchain_ollama"),
        ("PyMySQL", "pymysql"),
        ("Psycopg2", "psycopg2"),
    ]
    all_ok = True
    for name, mod in modules:
        try:
            __import__(mod)
            print_result(name, True, "Installed")
        except ImportError as e:
            print_result(name, False, f"Missing: {e}")
            all_ok = False
    return all_ok

def verify_frontend():
    print_header("6. React Frontend Scaffolding")
    frontend_dir = os.path.join(os.path.dirname(BACKEND_DIR), "frontend")
    package_json = os.path.join(frontend_dir, "package.json")
    node_modules = os.path.join(frontend_dir, "node_modules")
    
    if os.path.exists(package_json):
        print_result("React App Project Exists", True, frontend_dir)
        with open(package_json, "r") as f:
            pkg = json.load(f)
        framework = pkg.get("dependencies", {}).get("react", "Unknown")
        print_result("React Version", True, f"React {framework}")
        modules_exist = os.path.exists(node_modules)
        print_result("node_modules Installed", modules_exist, "Ready to start Vite dev server" if modules_exist else "Run 'npm install' in frontend folder")
        return modules_exist
    else:
        print_result("React App Project Exists", False, f"Not found at {frontend_dir}")
        return False

def main():
    print(f"\n{BOLD}{CYAN}AGENTIC ANALYTICS PLATFORM - PHASE 1 VERIFICATION{RESET}")
    print(f"Platform: Local Development (NO Docker)")
    print(f"Date: 2026-09-24")
    
    py_ok = verify_python()
    ollama_ok = verify_ollama()
    deps_ok = verify_backend_libraries()
    mysql_ok = verify_mysql()
    pg_ok = verify_postgres()
    fe_ok = verify_frontend()
    
    print_header("Summary of Phase 1 Readiness")
    all_passed = all([py_ok, ollama_ok, deps_ok, mysql_ok, pg_ok, fe_ok])
    if all_passed:
        print(f"\n{GREEN}{BOLD}>>> ALL PHASE 1 CHECKS PASSED SUCCESSFULLY! <<<{RESET}")
        print(f"You are completely ready to proceed to Phase 2 (Company Database Setup).\n")
    else:
        print(f"\n{YELLOW}{BOLD}>>> Some checks did not pass. Review output above. <<<{RESET}\n")

if __name__ == "__main__":
    main()
