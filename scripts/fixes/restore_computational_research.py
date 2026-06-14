#!/usr/bin:/usr/bin/env python3
"""Restore Computational Research (ID course, 2025-new) and its resources.

The previous cleanup incorrectly flagged Computational Research as a non-ID PA
course and archived it along with 20 linked resources. The user clarified it is
an ID course (new in 2025, not yet in the public catalog).

This script:
1. Un-archives the Computational Research course page.
2. Un-archives all 20 resources that were archived by cleanup_computational_research.py.
3. Re-links the 20 resources to Computational Research.
4. Re-adds Computational Research to the 2 multi-linked resources.
5. Adds MDes programs link to the course page.
"""
import json
import ssl
import sys
import time
import urllib.error
import urllib.request

ENV_PATH = "/Users/idstuart/Projects/idcodex/.env"
NOTION_API_KEY = None
with open(ENV_PATH) as f:
    for line in f:
        if line.startswith("NOTION_API_KEY="):
            NOTION_API_KEY = line.split("=", 1)[1].strip()
            break
assert NOTION_API_KEY

SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

COMP_RESEARCH_ID = "34b89b8f-3cf1-816d-8dd1-c74f9262e185"
RESOURCES_DB = "dd4ea6d9-92b4-4f28-b75c-ecb7f6b851be"

# Programs
MDES = "31a89b8f-3cf1-8148-ac0b-e039fbfd5ca5"
MDES_MBA = "31a89b8f-3cf1-8176-9244-dda153ff356b"
MDES_MPA = "31a89b8f-3cf1-8134-8c67-c099929e647f"

# The 20 archived resource titles (from cleanup_computational_research.py output)
ARCHIVED_TITLES = [
    "Simulation and Its Discontents",
    "Doing Digital Methods",
    "Statistics in a Nutshell (O'Reilly)",
    "Predictive or Imaginative Futures (Durante et al. 2024)",
    "Algorithms (MIT Press Essential Knowledge)",
    "Data Science (MIT Press Essential Knowledge)",
    "The Signal and the Noise",
    "Building SimCity",
    "Computational Literature Reviews (Antons et al. 2021)",
    "The End of Average",
    "Ghost Stories for Darwin",
    "journal.pmed.1003583",
    "Human-Centered Data Science",
    "MAST: User Behavior Pattern Analysis",
    "Grokking Algorithms",
    "Big Data Little Data No Data",
    "The Seductions of Quantification",
    "Sensors Journal Paper",
    "Corporate Foresight to Future-Making (Wenzel 2022)",
    "spider.pdf",
]

# The 2 resources that were unlinked (still exist, just had Computational Research removed)
# Their titles
MULTI_LINKED_TITLES = [
    "The Disability Studies Reader",
    "The Nature of Data",
]

SLEEP = 0.35


def api(method, url, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req, context=SSL_CTX) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        text = e.read().decode(errors="replace")
        print(f"  HTTP {e.code}: {text[:200]}")
        return None


def search_page_by_title(title):
    """Use Notion search to find a page by title. Returns the matching page obj or None."""
    body = {
        "query": title,
        "filter": {"value": "page", "property": "object"},
        "page_size": 20,
    }
    resp = api("POST", "https://api.notion.com/v1/search", body)
    if not resp:
        return None
    for r in resp.get("results", []):
        # Extract title
        props = r.get("properties", {})
        for pname, pval in props.items():
            if pval.get("type") == "title":
                page_title = "".join(t.get("plain_text", "") for t in pval.get("title", []))
                if page_title.strip() == title.strip():
                    return r
    return None


def main():
    print("=== STEP 1: Un-archive Computational Research course page ===")
    page = api("GET", f"https://api.notion.com/v1/pages/{COMP_RESEARCH_ID}")
    if page:
        archived = page.get("archived", False)
        print(f"  Current archived state: {archived}")
        if archived:
            api("PATCH", f"https://api.notion.com/v1/pages/{COMP_RESEARCH_ID}",
                {"archived": False})
            print("  UNARCHIVED.")
        else:
            print("  Already active — skipping.")

    print()
    print("=== STEP 2: Add MDes programs link to Computational Research course ===")
    # Get current programs
    page = api("GET", f"https://api.notion.com/v1/pages/{COMP_RESEARCH_ID}")
    if page:
        current_progs = [r["id"] for r in page["properties"].get("Programs", {}).get("relation", [])]
        want = [MDES, MDES_MBA, MDES_MPA]
        if set(current_progs) != set(want):
            api("PATCH", f"https://api.notion.com/v1/pages/{COMP_RESEARCH_ID}",
                {"properties": {"Programs": {"relation": [{"id": p} for p in want]}}})
            print("  PROGRAMS LINKED: MDes, MDes+MBA, MDes+MPA")
        else:
            print("  Programs already set — skipping.")

    print()
    print("=== STEP 3: Un-archive + relink 20 archived resources ===")
    restored = 0
    not_found = []
    for title in ARCHIVED_TITLES:
        time.sleep(SLEEP)
        found = search_page_by_title(title)
        if not found:
            print(f"  NOT FOUND: {title!r}")
            not_found.append(title)
            continue
        pid = found["id"]
        was_archived = found.get("archived", False)
        # Un-archive
        if was_archived:
            api("PATCH", f"https://api.notion.com/v1/pages/{pid}",
                {"archived": False})
        # Re-link to Comp Research (include any existing courses)
        current_courses = [r["id"] for r in found["properties"].get("Courses", {}).get("relation", [])]
        if COMP_RESEARCH_ID.replace("-", "") not in [c.replace("-", "") for c in current_courses]:
            new_courses = current_courses + [COMP_RESEARCH_ID]
        else:
            new_courses = current_courses
        api("PATCH", f"https://api.notion.com/v1/pages/{pid}",
            {"properties": {"Courses": {"relation": [{"id": c} for c in new_courses]}}})
        print(f"  RESTORED: {title!r}  (was_archived={was_archived})")
        restored += 1
        time.sleep(SLEEP)

    print()
    print(f"  Restored: {restored}/{len(ARCHIVED_TITLES)}")
    if not_found:
        print(f"  NOT FOUND ({len(not_found)}):")
        for t in not_found:
            print(f"    - {t}")

    print()
    print("=== STEP 4: Re-add Computational Research link to 2 multi-linked resources ===")
    relinked = 0
    for title in MULTI_LINKED_TITLES:
        time.sleep(SLEEP)
        found = search_page_by_title(title)
        if not found:
            print(f"  NOT FOUND: {title!r}")
            continue
        pid = found["id"]
        current_courses = [r["id"] for r in found["properties"].get("Courses", {}).get("relation", [])]
        if COMP_RESEARCH_ID.replace("-", "") in [c.replace("-", "") for c in current_courses]:
            print(f"  ALREADY LINKED: {title!r}")
            continue
        new_courses = current_courses + [COMP_RESEARCH_ID]
        api("PATCH", f"https://api.notion.com/v1/pages/{pid}",
            {"properties": {"Courses": {"relation": [{"id": c} for c in new_courses]}}})
        print(f"  RELINKED: {title!r}")
        relinked += 1

    print()
    print(f"=== DONE. Restored {restored} archived resources, relinked {relinked} multi-linked.")


if __name__ == "__main__":
    main()
