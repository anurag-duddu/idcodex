#!/usr/bin/env python3
"""
Fix duplicate courses in the ID Codex Notion workspace.

Duplicate 1: IDN 542
  - "Behavioral Economics" (OLD 2018 name) -> mark as Merged
  - "Behavioral Design for Organizational Leadership" (CURRENT)

Duplicate 2: Systems Theory
  - "Introduction to Systems Theory" (OLD 2018) -> mark as Merged
  - "Systems and Systems Theory in Design" (CURRENT IDN 571)

For each merged page, add a callout to the body pointing to the current page.
"""

import json
import os
import ssl
import sys
import urllib.request
import urllib.error
from pathlib import Path

# --- SSL (macOS Python workaround) ---
SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

# --- Load NOTION_API_KEY from .env ---
ENV_PATH = Path("/Users/idstuart/Projects/idcodex/.env")
API_KEY = None
for raw in ENV_PATH.read_text().splitlines():
    line = raw.strip()
    if not line or line.startswith("#"):
        continue
    if "=" not in line:
        continue
    k, v = line.split("=", 1)
    k = k.strip()
    v = v.strip().strip('"').strip("'")
    if k == "NOTION_API_KEY":
        API_KEY = v
        break

if not API_KEY:
    print("ERROR: NOTION_API_KEY not found in .env", file=sys.stderr)
    sys.exit(1)

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}


def request(method, url, body=None):
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, method=method, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, context=SSL_CTX) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8", errors="replace")
        return e.code, {"error": body_text}


def get_page(page_id):
    return request("GET", f"https://api.notion.com/v1/pages/{page_id}")


def get_database(db_id):
    return request("GET", f"https://api.notion.com/v1/databases/{db_id}")


def patch_page_status(page_id, status_name):
    body = {"properties": {"Status": {"select": {"name": status_name}}}}
    return request("PATCH", f"https://api.notion.com/v1/pages/{page_id}", body)


def append_callout(page_id, content, emoji="🔀"):
    body = {
        "children": [
            {
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": [
                        {"type": "text", "text": {"content": content}}
                    ],
                    "icon": {"type": "emoji", "emoji": emoji},
                },
            }
        ]
    }
    return request(
        "PATCH", f"https://api.notion.com/v1/blocks/{page_id}/children", body
    )


def extract_status(page_json):
    props = page_json.get("properties", {}) or {}
    status_prop = props.get("Status") or {}
    sel = status_prop.get("select")
    if sel and isinstance(sel, dict):
        return sel.get("name")
    return None


def extract_title(page_json):
    props = page_json.get("properties", {}) or {}
    for p in props.values():
        if p.get("type") == "title":
            rts = p.get("title") or []
            return "".join(rt.get("plain_text", "") for rt in rts)
    return "<unknown>"


# --- Duplicate definitions ---
DUPES = [
    {
        "label": "Duplicate 1: IDN 542",
        "old_page_id": "31a89b8f-3cf1-81dc-85cb-cafbb89cdeda",
        "old_name": "Behavioral Economics",
        "current_name": "Behavioral Design for Organizational Leadership",
        "callout_text": (
            "This course was renamed. Current title: "
            "Behavioral Design for Organizational Leadership (IDN 542). "
            "See that page for current content."
        ),
    },
    {
        "label": "Duplicate 2: Systems Theory",
        "old_page_id": "31a89b8f-3cf1-8107-9dea-e72bda1275ad",
        "old_name": "Introduction to Systems Theory",
        "current_name": "Systems and Systems Theory in Design",
        "callout_text": (
            "This course was renamed/merged. Current title: "
            "Systems and Systems Theory in Design (IDN 571). "
            "See that page for current content."
        ),
    },
]


def main():
    results = []
    errors = []

    for dupe in DUPES:
        print(f"\n=== {dupe['label']} ===")
        page_id = dupe["old_page_id"]

        # GET before
        code, data = get_page(page_id)
        if code != 200:
            msg = f"GET failed for {page_id}: {code} {data}"
            print(f"ERROR: {msg}")
            errors.append(msg)
            continue

        before_title = extract_title(data)
        before_status = extract_status(data)
        print(f"  Page: {before_title} ({page_id})")
        print(f"  Status before: {before_status!r}")

        # PATCH status -> Merged
        code, patch_data = patch_page_status(page_id, "Merged")
        if code != 200:
            msg = f"PATCH status failed for {page_id}: {code} {patch_data}"
            print(f"ERROR: {msg}")
            errors.append(msg)
            continue
        after_status = extract_status(patch_data)
        print(f"  Status after: {after_status!r}")

        # Append callout
        code, callout_data = append_callout(page_id, dupe["callout_text"])
        if code != 200:
            msg = f"Callout append failed for {page_id}: {code} {callout_data}"
            print(f"ERROR: {msg}")
            errors.append(msg)
            callout_ok = False
        else:
            callout_ok = True
            print("  Callout appended: OK")

        results.append(
            {
                "label": dupe["label"],
                "title": before_title,
                "before_status": before_status,
                "after_status": after_status,
                "callout_ok": callout_ok,
            }
        )

    # --- Summary ---
    print("\n\n=========== SUMMARY ===========")
    for r in results:
        print(
            f"- {r['label']}: {r['title']}\n"
            f"    Status: {r['before_status']} -> {r['after_status']}\n"
            f"    Callout appended: {r['callout_ok']}"
        )
    if errors:
        print("\nERRORS:")
        for e in errors:
            print(f"  - {e}")
    else:
        print("\nNo errors encountered.")


if __name__ == "__main__":
    main()
