#!/usr/bin/env python3
"""Remove contamination: Computational Research (MPA course) incorrectly added to ID course database."""
import json
import os
import ssl
import time
import urllib.request
import urllib.error

# Load API key from .env
ENV_PATH = "/Users/idstuart/Projects/idcodex/.env"
NOTION_API_KEY = None
with open(ENV_PATH, "r") as f:
    for line in f:
        if line.startswith("NOTION_API_KEY="):
            NOTION_API_KEY = line.split("=", 1)[1].strip()
            break
assert NOTION_API_KEY, "NOTION_API_KEY not found in .env"

SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

COMP_RESEARCH_ID = "34b89b8f-3cf1-816d-8dd1-c74f9262e185"
RESOURCES_DB_ID = "dd4ea6d9-92b4-4f28-b75c-ecb7f6b851be"
SLEEP = 0.35


def api_request(method, url, body=None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req, context=SSL_CTX) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8", errors="replace")
        print(f"HTTP ERROR {e.code} for {method} {url}: {body_text}")
        raise


def normalize_id(page_id):
    """Normalize a Notion ID by stripping dashes for comparison."""
    return page_id.replace("-", "").lower()


def get_page_title(page):
    """Extract the title from a page's properties."""
    props = page.get("properties", {})
    for prop_name, prop_val in props.items():
        if prop_val.get("type") == "title":
            title_arr = prop_val.get("title", [])
            return "".join(t.get("plain_text", "") for t in title_arr) or "(untitled)"
    return "(no title property)"


def query_linked_resources():
    """Paginated query for all resources linked to Computational Research."""
    url = f"https://api.notion.com/v1/databases/{RESOURCES_DB_ID}/query"
    results = []
    cursor = None
    while True:
        body = {
            "page_size": 100,
            "filter": {
                "property": "Courses",
                "relation": {"contains": COMP_RESEARCH_ID},
            },
        }
        if cursor:
            body["start_cursor"] = cursor
        resp = api_request("POST", url, body)
        results.extend(resp.get("results", []))
        if resp.get("has_more"):
            cursor = resp.get("next_cursor")
            time.sleep(SLEEP)
        else:
            break
    return results


def main():
    print("Querying resources linked to Computational Research...")
    resources = query_linked_resources()
    print(f"Found {len(resources)} linked resources.\n")

    archived_count = 0
    unlinked_count = 0
    comp_norm = normalize_id(COMP_RESEARCH_ID)

    for resource in resources:
        page_id = resource["id"]
        title = get_page_title(resource)
        courses_prop = resource.get("properties", {}).get("Courses", {})
        relations = courses_prop.get("relation", [])

        other_courses = [r for r in relations if normalize_id(r["id"]) != comp_norm]

        if not other_courses:
            # Only linked to Computational Research -> archive
            api_request(
                "PATCH",
                f"https://api.notion.com/v1/pages/{page_id}",
                {"archived": True},
            )
            print(f"ARCHIVED: {title}")
            archived_count += 1
        else:
            # Linked to others too -> remove only Computational Research
            api_request(
                "PATCH",
                f"https://api.notion.com/v1/pages/{page_id}",
                {"properties": {"Courses": {"relation": [{"id": r["id"]} for r in other_courses]}}},
            )
            kept_ids = ", ".join(r["id"] for r in other_courses)
            print(f"UNLINKED: {title} (kept on courses: {kept_ids})")
            unlinked_count += 1

        time.sleep(SLEEP)

    # Archive the course page itself
    print("\nArchiving Computational Research course page...")
    course_archived = False
    try:
        api_request(
            "PATCH",
            f"https://api.notion.com/v1/pages/{COMP_RESEARCH_ID}",
            {"archived": True},
        )
        course_archived = True
    except Exception as e:
        print(f"Failed to archive course page: {e}")

    print("\n=== SUMMARY ===")
    print(f"Total resources found: {len(resources)}")
    print(f"Archived: {archived_count}")
    print(f"Unlinked: {unlinked_count}")
    print(f"Course page archived: {'yes' if course_archived else 'no'}")


if __name__ == "__main__":
    main()
