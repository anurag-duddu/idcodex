#!/usr/bin/env python3
"""
Fix missing Programs relations on ID (Institute of Design) courses in the
ID Codex Notion Courses DB.

These are legitimate ID courses seeded without their Programs relation set.

Usage:
    python3 fix_program_links.py

Idempotent: uses GET before PATCH and skips pages that already have the
correct set of program relations.
"""

import json
import ssl
import sys
import time
import urllib.error
import urllib.request
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
    if not line or line.startswith("#") or "=" not in line:
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

COURSES_DB_ID = "f6d577cb-5358-468c-9981-2ede7a140638"

# --- Program page IDs ---
FOUNDATION = "31a89b8f-3cf1-810f-a00e-d3a7ccafe6e1"
MDES = "31a89b8f-3cf1-8148-ac0b-e039fbfd5ca5"
MDES_MBA = "31a89b8f-3cf1-8176-9244-dda153ff356b"
MDES_MPA = "31a89b8f-3cf1-8134-8c67-c099929e647f"
MS_SDL = "31a89b8f-3cf1-81d5-8615-e421ef31be80"

MDES_ALL = [MDES, MDES_MBA, MDES_MPA]
MDES_ALL_PLUS_SDL = [MDES, MDES_MBA, MDES_MPA, MS_SDL]

RATE_LIMIT_SEC = 0.35


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
        try:
            return e.code, json.loads(body_text)
        except Exception:
            return e.code, {"error": body_text}


def normalize_id(raw):
    """Strip dashes for robust comparison."""
    return (raw or "").replace("-", "").lower()


def query_course_by_name(name):
    """Return list of (page_id, title) matches."""
    body = {
        "page_size": 10,
        "filter": {"property": "Name", "title": {"equals": name}},
    }
    code, data = request(
        "POST",
        f"https://api.notion.com/v1/databases/{COURSES_DB_ID}/query",
        body,
    )
    time.sleep(RATE_LIMIT_SEC)
    if code != 200:
        return code, None
    results = []
    for row in data.get("results", []):
        pid = row.get("id")
        title = ""
        for p in (row.get("properties") or {}).values():
            if p.get("type") == "title":
                rts = p.get("title") or []
                title = "".join(rt.get("plain_text", "") for rt in rts)
                break
        results.append((pid, title))
    return code, results


def get_page(page_id):
    code, data = request("GET", f"https://api.notion.com/v1/pages/{page_id}")
    time.sleep(RATE_LIMIT_SEC)
    return code, data


def extract_programs_ids(page_json):
    props = page_json.get("properties", {}) or {}
    prog = props.get("Programs") or {}
    rel = prog.get("relation") or []
    return [r.get("id") for r in rel if r.get("id")]


def patch_programs(page_id, program_ids):
    body = {
        "properties": {
            "Programs": {
                "relation": [{"id": pid} for pid in program_ids]
            }
        }
    }
    code, data = request(
        "PATCH", f"https://api.notion.com/v1/pages/{page_id}", body
    )
    time.sleep(RATE_LIMIT_SEC)
    return code, data


# --- Courses to fix ---
# (name, explicit_page_id_or_None, desired_program_ids, note)
COURSES = [
    ("Re-Thinking Systems", "31a89b8f-3cf1-8112-9344-dbc7240d94df", MDES_ALL, None),
    ("Embodied Design", None, MDES_ALL, None),
    ("Introduction to Data Visualization", None, MDES_ALL, None),
    ("Activating Frameworks", None, MDES_ALL, None),
    ("Introduction to Objects & Artifacts", None, MDES_ALL_PLUS_SDL, "Alignment"),
    ("Introduction to Product Strategy", None, MDES_ALL, None),
    ("Multidisciplinary Innovation", None, MDES_ALL, None),
    ("Metrics that Matter", None, MDES_ALL, None),
    ("Research Synthesis", None, MDES_ALL, None),
    ("Methods of Community Development", None, MDES_ALL, None),
    ("Implementing Innovation", None, MDES_ALL, "ID540"),
    ("Decision Quality", None, MDES_ALL, None),
    ("AI for Rapid Prototyping", None, MDES_ALL, None),
    ("Social Entrepreneurship", None, [FOUNDATION], "Foundation"),
]

SKIP_PAGE_IDS = {
    # "Introduction to Systems Theory" — being merged into
    # "Systems and Systems Theory in Design". Leave programs empty.
    normalize_id("31a89b8f-3cf1-8107-9dea-e72bda1275ad"),
}


def resolve_page_id(name, explicit_id):
    if explicit_id:
        return explicit_id, None
    code, results = query_course_by_name(name)
    if code != 200:
        return None, f"query failed code={code}"
    if not results:
        return None, "not found"
    # Filter out skip pages first.
    filtered = [
        r for r in results if normalize_id(r[0]) not in SKIP_PAGE_IDS
    ]
    if not filtered:
        return None, "only skip-listed matches"
    if len(filtered) > 1:
        # Prefer active / current entry if we had a way to tell — just report.
        listing = "; ".join(f"{pid} ({title})" for pid, title in filtered)
        return None, f"multiple matches: {listing}"
    return filtered[0][0], None


def main():
    updated = []
    already_ok = []
    errors = []

    for name, explicit_id, desired, note in COURSES:
        label = f'"{name}"' + (f" [{note}]" if note else "")
        print(f"\n=== {label} ===")

        page_id, resolve_err = resolve_page_id(name, explicit_id)
        if not page_id:
            msg = f"lookup failed: {resolve_err}"
            print(f"  ERROR: {msg}")
            errors.append((name, None, msg))
            continue

        if normalize_id(page_id) in SKIP_PAGE_IDS:
            print(f"  SKIP page_id={page_id} (in skip list)")
            continue

        print(f"  page_id={page_id}")
        code, page = get_page(page_id)
        if code != 200:
            msg = f"GET failed code={code} body={page}"
            print(f"  ERROR: {msg}")
            errors.append((name, page_id, msg))
            continue

        existing = extract_programs_ids(page)
        existing_set = {normalize_id(pid) for pid in existing}
        desired_set = {normalize_id(pid) for pid in desired}

        if existing_set == desired_set:
            print(f"  already correct: {len(existing)} relations")
            already_ok.append((name, page_id))
            continue

        print(
            f"  updating: existing={len(existing)} -> desired={len(desired)}"
        )
        code, resp = patch_programs(page_id, desired)
        if code != 200:
            msg = f"PATCH failed code={code} body={resp}"
            print(f"  ERROR: {msg}")
            errors.append((name, page_id, msg))
            continue
        updated.append((name, page_id))
        print("  OK updated")

    # --- Summary ---
    print("\n\n==== SUMMARY ====")
    print(f"Updated: {len(updated)}")
    for n, pid in updated:
        print(f"  - {n}  [{pid}]")
    print(f"Already correct: {len(already_ok)}")
    for n, pid in already_ok:
        print(f"  - {n}  [{pid}]")
    print(f"Errors: {len(errors)}")
    for n, pid, msg in errors:
        print(f"  - {n}  [{pid}]  {msg}")

    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
