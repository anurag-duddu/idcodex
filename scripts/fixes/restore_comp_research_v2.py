#!/usr/bin/env python3
"""
Restore 17 incorrectly archived resources and re-link to Computational Research,
plus recreate 5 resources whose page IDs were lost.
"""
import json
import os
import ssl
import sys
import time
import urllib.request
import urllib.error

# Load API key from .env
ENV_PATH = "/Users/idstuart/Projects/idcodex/.env"
NOTION_API_KEY = None
with open(ENV_PATH, "r") as f:
    for line in f:
        line = line.strip()
        if line.startswith("NOTION_API_KEY="):
            NOTION_API_KEY = line.split("=", 1)[1].strip()
            break

if not NOTION_API_KEY:
    print("ERROR: NOTION_API_KEY not found in .env")
    sys.exit(1)

SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

API_BASE = "https://api.notion.com"
RATE_LIMIT = 0.35

# IDs
COMP_RESEARCH_ID = "34b89b8f-3cf1-816d-8dd1-c74f9262e185"
RESOURCES_DB_ID = "dd4ea6d9-92b4-4f28-b75c-ecb7f6b851be"


def _request(method, path, body=None):
    url = f"{API_BASE}{path}"
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req, context=SSL_CTX, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code} on {method} {path}: {body_text}") from None
    except urllib.error.URLError as e:
        raise RuntimeError(f"URL error on {method} {path}: {e}") from None


def get_page(page_id):
    time.sleep(RATE_LIMIT)
    return _request("GET", f"/v1/pages/{page_id}")


def patch_page(page_id, body):
    time.sleep(RATE_LIMIT)
    return _request("PATCH", f"/v1/pages/{page_id}", body)


def create_page(body):
    time.sleep(RATE_LIMIT)
    return _request("POST", "/v1/pages", body)


def query_db(db_id, body):
    time.sleep(RATE_LIMIT)
    return _request("POST", f"/v1/databases/{db_id}/query", body)


# Part A: Un-archive + relink
PAGES_TO_RESTORE = [
    ("34b89b8f-3cf1-81e9-9524-e68980189289", "Corporate Foresight to Future-Making (Wenzel 2022)"),
    ("34b89b8f-3cf1-8142-8dc4-d66a75d7303f", "Computational Literature Reviews (Antons et al. 2021)"),
    ("34b89b8f-3cf1-8178-aded-f68335d6b20b", "journal.pmed.1003583"),
    ("34b89b8f-3cf1-813b-9822-cf268d82178f", "Data Science (MIT Press Essential Knowledge)"),
    ("34b89b8f-3cf1-81d5-a9f6-c1b989f17bb0", "The Seductions of Quantification"),
    ("34b89b8f-3cf1-816f-b260-fcd3fb24346d", "Ghost Stories for Darwin"),
    ("34b89b8f-3cf1-8119-bac9-c720174d27ed", "Simulation and Its Discontents"),
    ("34b89b8f-3cf1-8169-8827-d0da3d5af818", "The End of Average"),
    ("34b89b8f-3cf1-8137-b868-d6677e618f51", "Algorithms (MIT Press Essential Knowledge)"),
    ("34b89b8f-3cf1-819c-9969-e6fd02507ecb", "Human-Centered Data Science"),
    ("34b89b8f-3cf1-8122-8d95-f3888dfae366", "Predictive or Imaginative Futures (Durante et al. 2024)"),
    ("34b89b8f-3cf1-813d-95a8-f738627f1f27", "The Signal and the Noise"),
    ("34b89b8f-3cf1-813e-afb8-f76f5615ecf9", "Building SimCity"),
    ("34b89b8f-3cf1-811a-9d12-f65cd459bc50", "Doing Digital Methods"),
    ("34b89b8f-3cf1-81c6-b5e1-e4ebeefe9f5e", "Grokking Algorithms"),
]

# Note: user said "17 known" but listed 15. We'll process what's given.
# Part B: 5 to recreate
RECREATE = [
    ("Statistics in a Nutshell (O'Reilly)", "Book"),
    ("MAST: User Behavior Pattern Analysis", "Paper"),
    ("Big Data Little Data No Data", "Book"),
    ("Sensors Journal Paper", "Paper"),
    ("Spider Diagrams (Behavioral Design)", "Paper"),
]


def main():
    restored = 0
    errors = []

    print(f"=== Part A: Restoring {len(PAGES_TO_RESTORE)} pages ===")
    for page_id, title in PAGES_TO_RESTORE:
        try:
            # 1. Un-archive
            patch_page(page_id, {"archived": False})

            # 2. Read current Courses relation
            page = get_page(page_id)
            props = page.get("properties", {})
            courses_prop = props.get("Courses", {})
            existing = courses_prop.get("relation", []) if courses_prop else []
            existing_ids = [r["id"] for r in existing]

            # Normalize hyphenated comp research ID for comparison
            def _norm(i):
                return i.replace("-", "")

            comp_norm = _norm(COMP_RESEARCH_ID)
            already_linked = any(_norm(i) == comp_norm for i in existing_ids)

            if already_linked:
                new_relation = [{"id": i} for i in existing_ids]
            else:
                new_relation = [{"id": i} for i in existing_ids] + [{"id": COMP_RESEARCH_ID}]

            # 3. PATCH Courses
            patch_page(page_id, {"properties": {"Courses": {"relation": new_relation}}})
            print(f"  [OK] {title}  (existing courses: {len(existing_ids)}, now: {len(new_relation)})")
            restored += 1
        except Exception as e:
            msg = f"  [ERR] {title} ({page_id}): {e}"
            print(msg)
            errors.append(msg)

    print(f"\n=== Part B: Recreating {len(RECREATE)} resources ===")
    recreated = 0
    for title, rtype in RECREATE:
        try:
            body = {
                "parent": {"database_id": RESOURCES_DB_ID},
                "properties": {
                    "Title": {"title": [{"text": {"content": title}}]},
                    "Type": {"select": {"name": rtype}},
                    "Courses": {"relation": [{"id": COMP_RESEARCH_ID}]},
                },
            }
            result = create_page(body)
            new_id = result.get("id")
            print(f"  [OK] Created: {title}  ({new_id})")
            recreated += 1
        except Exception as e:
            msg = f"  [ERR] Create '{title}': {e}"
            print(msg)
            errors.append(msg)

    # Verification
    print("\n=== Verification ===")
    try:
        all_results = []
        has_more = True
        start_cursor = None
        while has_more:
            qbody = {
                "filter": {
                    "property": "Courses",
                    "relation": {"contains": COMP_RESEARCH_ID},
                },
                "page_size": 100,
            }
            if start_cursor:
                qbody["start_cursor"] = start_cursor
            res = query_db(RESOURCES_DB_ID, qbody)
            all_results.extend(res.get("results", []))
            has_more = res.get("has_more", False)
            start_cursor = res.get("next_cursor")
        count = len(all_results)
        print(f"Resources linked to Computational Research: {count}")
    except Exception as e:
        count = None
        msg = f"  [ERR] Verification query: {e}"
        print(msg)
        errors.append(msg)

    print("\n=== Summary ===")
    print(f"Restored: {restored}/{len(PAGES_TO_RESTORE)}")
    print(f"Recreated: {recreated}/{len(RECREATE)}")
    print(f"Final count on Computational Research: {count}")
    if errors:
        print(f"\nErrors ({len(errors)}):")
        for e in errors:
            print(e)


if __name__ == "__main__":
    main()
