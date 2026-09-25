"""
Export OpenAPI Specification (JSON and YAML) for FreshMart Agentic Analytics.
Generates:
- backend/openapi.json
- backend/openapi.yaml
- docs/openapi.json
- docs/openapi.yaml
"""

import os
import sys
import json
import yaml

# Ensure backend root is on sys.path
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.main import app

def export_openapi():
    print("Generating OpenAPI specification...")
    spec = app.openapi()

    docs_dir = os.path.join(PROJECT_ROOT, "docs")
    os.makedirs(docs_dir, exist_ok=True)

    # 1. Export JSON to backend and docs
    backend_json_path = os.path.join(BACKEND_DIR, "openapi.json")
    docs_json_path = os.path.join(docs_dir, "openapi.json")

    with open(backend_json_path, "w", encoding="utf-8") as f:
        json.dump(spec, f, indent=2)
    print(f"Exported JSON: {backend_json_path}")

    with open(docs_json_path, "w", encoding="utf-8") as f:
        json.dump(spec, f, indent=2)
    print(f"Exported JSON: {docs_json_path}")

    # 2. Export YAML to backend and docs
    backend_yaml_path = os.path.join(BACKEND_DIR, "openapi.yaml")
    docs_yaml_path = os.path.join(docs_dir, "openapi.yaml")

    with open(backend_yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(spec, f, sort_keys=False, allow_unicode=True)
    print(f"Exported YAML: {backend_yaml_path}")

    with open(docs_yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(spec, f, sort_keys=False, allow_unicode=True)
    print(f"Exported YAML: {docs_yaml_path}")

    print("\nOpenAPI export complete! Files generated successfully.")

if __name__ == "__main__":
    export_openapi()
