#!/usr/bin/env python3
"""
BOLDR Self-Improving Customer Intelligence Engine
n8n Workflow Auto-Import Script

Imports all 5 n8n workflows into a running n8n instance via REST API.
Run this after starting n8n with `docker compose up -d n8n`.

Usage:
    python scripts/import_workflows.py [--host http://localhost:5678] [--api-key BOLDR_n8n_API_KEY_2026]

Author: Steve Ng, Founder and CEO — Digital Futures Consultancy LLP
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests

# Default configuration
DEFAULT_HOST = os.environ.get("N8N_HOST", "http://localhost:5678")
DEFAULT_API_KEY = os.environ.get("N8N_API_KEY", "BOLDR_n8n_API_KEY_2026")
WORKFLOWS_DIR = Path(__file__).parent.parent / "n8n" / "workflows"

# Workflow files to import (in order)
WORKFLOW_FILES = [
    "chat_intake.json",
    "whatsapp_intake.json",
    "instagram_dm_intake.json",
    "email_intake.json",
    "intelligence_loop.json",
]

# Workflow display names
WORKFLOW_NAMES = {
    "chat_intake.json": "BOLDR Chat Intake",
    "whatsapp_intake.json": "BOLDR WhatsApp Intake",
    "instagram_dm_intake.json": "BOLDR Instagram DM Intake",
    "email_intake.json": "BOLDR Email Intake",
    "intelligence_loop.json": "BOLDR Intelligence Loop",
}


def check_n8n_health(host: str) -> bool:
    """Check if n8n is running and healthy."""
    try:
        resp = requests.get(f"{host}/healthz", timeout=10)
        return resp.status_code == 200
    except Exception:
        return False


def get_existing_workflows(host: str, api_key: str) -> dict:
    """Get all existing workflows, returns a dict of name -> id."""
    headers = {"X-N8N-API-KEY": api_key}
    try:
        resp = requests.get(f"{host}/api/v1/workflows", headers=headers, timeout=10)
        if resp.status_code == 200:
            workflows = resp.json().get("data", [])
            return {wf["name"]: wf["id"] for wf in workflows}
        return {}
    except Exception:
        return {}


def delete_workflow(host: str, api_key: str, workflow_id: str) -> bool:
    """Delete a workflow by ID."""
    headers = {"X-N8N-API-KEY": api_key}
    try:
        resp = requests.delete(f"{host}/api/v1/workflows/{workflow_id}", headers=headers, timeout=10)
        return resp.status_code in (200, 204)
    except Exception:
        return False


def import_workflow(host: str, api_key: str, workflow_file: Path, name: str) -> dict:
    """Import a single workflow into n8n."""
    headers = {"X-N8N-API-KEY": api_key, "Content-Type": "application/json"}

    with open(workflow_file) as f:
        workflow_data = json.load(f)

    # Set the workflow name
    workflow_data["name"] = name

    # Remove fields that n8n doesn't accept on import
    for field in ["id", "createdAt", "updatedAt", "activeData"]:
        workflow_data.pop(field, None)

    # Ensure nodes have position data
    for node in workflow_data.get("nodes", []):
        if "position" not in node:
            node["position"] = [0, 0]

    try:
        resp = requests.post(
            f"{host}/api/v1/workflows",
            headers=headers,
            json=workflow_data,
            timeout=30,
        )
        if resp.status_code in (200, 201):
            result = resp.json()
            return {"status": "imported", "name": name, "id": result.get("id"), "file": workflow_file.name}
        else:
            return {"status": "error", "name": name, "error": f"HTTP {resp.status_code}: {resp.text[:200]}", "file": workflow_file.name}
    except Exception as e:
        return {"status": "error", "name": name, "error": str(e), "file": workflow_file.name}


def activate_workflow(host: str, api_key: str, workflow_id: str) -> bool:
    """Activate a workflow so it starts listening for webhooks."""
    headers = {"X-N8N-API-KEY": api_key}
    try:
        resp = requests.patch(
            f"{host}/api/v1/workflows/{workflow_id}",
            headers=headers,
            json={"active": True},
            timeout=10,
        )
        return resp.status_code == 200
    except Exception:
        return False


def test_webhook(host: str, webhook_path: str, test_payload: dict) -> dict:
    """Test a webhook endpoint with a sample payload."""
    url = f"{host}{webhook_path}"
    try:
        resp = requests.post(url, json=test_payload, timeout=30)
        return {
            "endpoint": webhook_path,
            "status_code": resp.status_code,
            "response": resp.json() if resp.headers.get("content-type", "").startswith("application/json") else resp.text[:200],
        }
    except Exception as e:
        return {"endpoint": webhook_path, "status_code": 0, "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Import BOLDR n8n workflows")
    parser.add_argument("--host", default=DEFAULT_HOST, help="n8n host URL (default: http://localhost:5678)")
    parser.add_argument("--api-key", default=DEFAULT_API_KEY, help="n8n API key")
    parser.add_argument("--skip-existing", action="store_true", help="Skip workflows that already exist")
    parser.add_argument("--force", action="store_true", help="Delete existing workflows before importing")
    parser.add_argument("--activate", action="store_true", default=True, help="Activate workflows after import")
    parser.add_argument("--test", action="store_true", help="Test webhook endpoints after import")
    args = parser.parse_args()

    print("=" * 60)
    print("BOLDR n8n Workflow Auto-Import")
    print("=" * 60)
    print(f"n8n Host: {args.host}")
    print(f"Workflows Dir: {WORKFLOWS_DIR}")
    print()

    # Check n8n is running
    print("Checking n8n health...")
    if not check_n8n_health(args.host):
        print("ERROR: n8n is not running. Start it with: docker compose up -d n8n")
        sys.exit(1)
    print("n8n is healthy.")

    # Get existing workflows
    print("\nChecking existing workflows...")
    existing = get_existing_workflows(args.host, args.api_key)
    if existing:
        print(f"Found {len(existing)} existing workflows:")
        for name, wf_id in existing.items():
            print(f"  - {name} (ID: {wf_id})")
    else:
        print("No existing workflows found.")

    # Delete existing BOLDR workflows if force mode
    if args.force and existing:
        print("\nForce mode: Deleting existing BOLDR workflows...")
        for name, wf_id in existing.items():
            if "BOLDR" in name.upper() or name in WORKFLOW_NAMES.values():
                if delete_workflow(args.host, args.api_key, wf_id):
                    print(f"  Deleted: {name} (ID: {wf_id})")
                else:
                    print(f"  Failed to delete: {name} (ID: {wf_id})")

    # Import workflows
    print("\nImporting workflows...")
    results = []
    for filename in WORKFLOW_FILES:
        filepath = WORKFLOWS_DIR / filename
        if not filepath.exists():
            print(f"  SKIP: {filename} not found")
            continue

        name = WORKFLOW_NAMES.get(filename, filename.replace(".json", ""))
        existing_id = None
        for existing_name, eid in get_existing_workflows(args.host, args.api_key).items():
            if existing_name == name:
                existing_id = eid
                break

        if existing_id and args.skip_existing:
            print(f"  SKIP: {name} already exists (ID: {existing_id})")
            results.append({"status": "skipped", "name": name, "id": existing_id})
            continue

        if existing_id and not args.force:
            print(f"  SKIP: {name} already exists (ID: {existing_id}). Use --force to replace.")
            results.append({"status": "skipped", "name": name, "id": existing_id})
            continue

        result = import_workflow(args.host, args.api_key, filepath, name)
        results.append(result)
        if result["status"] == "imported":
            print(f"  IMPORTED: {name} (ID: {result['id']})")
            # Activate the workflow
            if args.activate and result.get("id"):
                if activate_workflow(args.host, args.api_key, result["id"]):
                    print(f"  ACTIVATED: {name}")
                else:
                    print(f"  WARNING: Could not activate {name}")
        else:
            print(f"  ERROR: {name} - {result.get('error', 'Unknown error')}")

    # Summary
    print("\n" + "=" * 60)
    print("Import Summary")
    print("=" * 60)
    imported = sum(1 for r in results if r["status"] == "imported")
    skipped = sum(1 for r in results if r["status"] == "skipped")
    errors = sum(1 for r in results if r["status"] == "error")
    print(f"Imported: {imported}")
    print(f"Skipped: {skipped}")
    print(f"Errors: {errors}")

    # Test webhooks if requested
    if args.test:
        print("\n" + "=" * 60)
        print("Testing Webhook Endpoints")
        print("=" * 60)
        test_payloads = {
            "/webhook/chat": {"message": "Are your straps BPA-free?", "sender_name": "Test User", "channel": "chat"},
            "/webhook/whatsapp": {"message": "How much for engraving?", "sender_name": "Test User", "channel": "whatsapp"},
            "/webhook/instagram-dm": {"message": "Do you have vegan straps?", "sender_name": "Test User", "channel": "instagram_dm"},
            "/webhook/email": {"message": "I need to service my watch", "subject": "Watch Servicing", "sender_name": "Test User", "channel": "email"},
            "/webhook/boldr-intake": {"message": "Are your straps BPA-free?", "sender_name": "Caleb", "channel": "chat"},
        }
        for path, payload in test_payloads.items():
            # Use the API server for intelligence loop, n8n for intake
            if path == "/webhook/boldr-intake":
                url = f"http://localhost:8000/api/v1/intake"
            else:
                url = f"{args.host}{path}"
            result = test_webhook(args.host, path, payload)
            status = result.get("status_code", "N/A")
            print(f"  {path}: HTTP {status}")

    print("\nDone.")


if __name__ == "__main__":
    main()