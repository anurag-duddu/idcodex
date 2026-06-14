#!/usr/bin/env python3
"""
Apply Former Names rename pattern to three renamed courses in the ID Codex Notion workspace.
Consolidates duplicate merged pages by transferring resources and archiving old pages.
"""

import json
import os
import ssl
import sys
import time
import urllib.request
import urllib.error

# --- Setup ---
ENV_PATH = "/Users/idstuart/Projects/idcodex/.env"
NOTION_VERSION = "2022-06-28"
API_BASE = "https://api.notion.com/v1"
RATE_LIMIT_SEC = 0.35

RESOURCES_DB_ID = "dd4ea6d9-92b4-4f28-b75c-ecb7f6b851be"

SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE


def load_api_key():
    with open(ENV_PATH) as f:
        for line in f:
            line = line.strip()
            if line.startswith("NOTION_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise RuntimeError("NOTION_API_KEY not found in .env")


API_KEY = load_api_key()

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Notion-Version": NOTION_VERSION,
    "Content-Type": "application/json",
}


def _request(method, path, body=None):
    url = f"{API_BASE}{path}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    for k, v in HEADERS.items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, context=SSL_CTX, timeout=30) as resp:
            payload = resp.read().decode("utf-8")
            return json.loads(payload) if payload else {}
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code} {method} {path}: {err_body}") from None
    finally:
        time.sleep(RATE_LIMIT_SEC)


def get_page(page_id):
    return _request("GET", f"/pages/{page_id}")


def patch_page(page_id, body):
    return _request("PATCH", f"/pages/{page_id}", body)


def query_db(db_id, body):
    # handle pagination
    results = []
    next_cursor = None
    while True:
        q = dict(body)
        if next_cursor:
            q["start_cursor"] = next_cursor
        resp = _request("POST", f"/databases/{db_id}/query", q)
        results.extend(resp.get("results", []))
        if resp.get("has_more"):
            next_cursor = resp.get("next_cursor")
        else:
            break
    return results


def set_former_names(page_id, names_str):
    body = {
        "properties": {
            "Former Names": {
                "rich_text": [{"text": {"content": names_str}}]
            }
        }
    }
    return patch_page(page_id, body)


def find_resources_for_course(course_page_id):
    body = {
        "filter": {
            "property": "Courses",
            "relation": {"contains": course_page_id},
        }
    }
    return query_db(RESOURCES_DB_ID, body)


def transfer_resource(resource, old_course_id, new_course_id):
    """Replace old_course_id with new_course_id in the resource's Courses relation."""
    courses_prop = resource.get("properties", {}).get("Courses", {})
    relations = courses_prop.get("relation", [])
    new_relations = []
    seen = set()
    has_new = False
    for rel in relations:
        rid = rel.get("id")
        if rid == old_course_id:
            continue  # drop
        if rid == new_course_id:
            has_new = True
        if rid and rid not in seen:
            new_relations.append({"id": rid})
            seen.add(rid)
    if not has_new and new_course_id not in seen:
        new_relations.append({"id": new_course_id})
    body = {"properties": {"Courses": {"relation": new_relations}}}
    return patch_page(resource["id"], body)


def archive_page(page_id):
    return patch_page(page_id, {"archived": True})


def process_rename(label, current_id, former_names, old_id=None):
    print(f"\n=== {label} ===")
    errors = []

    # A: Set Former Names on current page
    try:
        set_former_names(current_id, former_names)
        print(f"  [OK] Former Names set on {current_id}: {former_names!r}")
    except Exception as e:
        msg = f"  [ERR] Setting Former Names on {current_id}: {e}"
        print(msg)
        errors.append(msg)

    transferred = 0
    # B/C: consolidation
    if old_id:
        try:
            resources = find_resources_for_course(old_id)
            print(f"  Found {len(resources)} resource(s) linked to old page {old_id}")
            for r in resources:
                try:
                    transfer_resource(r, old_id, current_id)
                    transferred += 1
                except Exception as e:
                    msg = f"  [ERR] Transferring resource {r.get('id')}: {e}"
                    print(msg)
                    errors.append(msg)
            print(f"  [OK] Transferred {transferred}/{len(resources)} resources")
        except Exception as e:
            msg = f"  [ERR] Querying resources for old page {old_id}: {e}"
            print(msg)
            errors.append(msg)

        try:
            archive_page(old_id)
            print(f"  [OK] Archived old page {old_id}")
        except Exception as e:
            msg = f"  [ERR] Archiving old page {old_id}: {e}"
            print(msg)
            errors.append(msg)

    return {"transferred": transferred, "errors": errors}


def main():
    results = {}

    # Rename 1
    results["rename1"] = process_rename(
        "Rename 1: Design for Digital Technology",
        current_id="31a89b8f-3cf1-8153-b12a-d359ba4bcaee",
        former_names="Smart Connected Service Management; Smart and Connected Systems",
        old_id=None,  # no consolidation
    )

    # Rename 2
    results["rename2"] = process_rename(
        "Rename 2: Behavioral Design for Organizational Leadership",
        current_id="31a89b8f-3cf1-81ab-b129-c03f6f0c9c61",
        former_names="Behavioral Economics",
        old_id="31a89b8f-3cf1-81dc-85cb-cafbb89cdeda",
    )

    # Rename 3
    results["rename3"] = process_rename(
        "Rename 3: Systems and Systems Theory in Design",
        current_id="31a89b8f-3cf1-81cc-b87c-ef50e55eb681",
        former_names="Introduction to Systems Theory",
        old_id="31a89b8f-3cf1-8107-9dea-e72bda1275ad",
    )

    # Summary
    print("\n\n=== SUMMARY ===")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
