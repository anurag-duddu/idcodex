#!/usr/bin/env python3
"""Remove wrong file attachments from ID Codex Resources DB pages.

Previous fuzzy filename matching created wrong attachments. This script:
1. Finds each page by title in the Resources DB
2. Verifies the current attached file matches the expected-wrong filename
3. If match confirmed -> PATCH to clear the File property
4. If different or empty -> skip and report
"""

import json
import os
import ssl
import urllib.request
from pathlib import Path

# Load NOTION_API_KEY from .env
ENV_PATH = Path("/Users/idstuart/Projects/idcodex/.env")
for line in ENV_PATH.read_text().splitlines():
    line = line.strip()
    if line and "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

NOTION_API_KEY = os.environ["NOTION_API_KEY"]
RESOURCES_DB_ID = "dd4ea6d9-92b4-4f28-b75c-ecb7f6b851be"

SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}


def _request(method: str, url: str, body: dict | None = None) -> dict:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers=HEADERS)
    with urllib.request.urlopen(req, context=SSL_CTX) as resp:
        return json.loads(resp.read().decode("utf-8"))


def query_by_title(title: str) -> list[dict]:
    url = f"https://api.notion.com/v1/databases/{RESOURCES_DB_ID}/query"
    body = {
        "page_size": 5,
        "filter": {"property": "Title", "title": {"equals": title}},
    }
    return _request("POST", url, body).get("results", [])


def get_page(page_id: str) -> dict:
    return _request("GET", f"https://api.notion.com/v1/pages/{page_id}")


def file_entry_name(entry: dict) -> str:
    # Notion file entries have a "name" plus either external.url or file.url.
    return entry.get("name") or ""


def current_file_info(page: dict) -> tuple[list[dict], list[str]]:
    files_prop = page.get("properties", {}).get("File", {})
    files = files_prop.get("files", []) if files_prop.get("type") == "files" else []
    names = [file_entry_name(f) for f in files]
    return files, names


def clear_file(page_id: str) -> dict:
    url = f"https://api.notion.com/v1/pages/{page_id}"
    return _request("PATCH", url, {"properties": {"File": {"files": []}}})


TARGETS = [
    {
        "title": "Week 1: Intro & Typography",
        "expected": "Week 1—peeps-hemophilia.pdf",
    },
    {
        "title": "Introduction to Lighting",
        "expected": "introduction-to-design-futures.pdf",
    },
    {
        "title": "The Internet of Things",
        "expected": "Benefits of the office.pdf",
    },
    {
        "title": "Week 5: Imagery",
        "expected": "Week 5 assignments.pdf",
    },
    {
        "title": "The Nature of Technology — Ch 2",
        "expected": "Simon - The Sciences of the Artificial Ch 1.pdf",
    },
    {
        "title": "BD-02 Cognitive Effort (Fall 2025)",
        "expected": "2024F-BD-02cognitiveeffort.pdf",
    },
]


def run() -> None:
    for target in TARGETS:
        title = target["title"]
        expected = target["expected"]
        print(f"\n=== {title} ===")
        try:
            results = query_by_title(title)
        except Exception as e:
            print(f"  ERROR querying: {e}")
            continue

        if not results:
            print("  NOT FOUND in Resources DB")
            continue
        if len(results) > 1:
            print(f"  WARN: {len(results)} matches; using first")

        page = results[0]
        page_id = page["id"]
        print(f"  page_id: {page_id}")

        files, names = current_file_info(page)
        if not files:
            print("  current file: (none) -- SKIP (already empty)")
            continue

        print(f"  current file(s): {names}")

        # Match on basename containment (exact or substring either way).
        def matches(actual: str, expected_: str) -> bool:
            a = actual.strip().lower()
            e = expected_.strip().lower()
            if not a or not e:
                return False
            # Compare by basename too, in case of URL paths.
            a_base = a.rsplit("/", 1)[-1]
            e_base = e.rsplit("/", 1)[-1]
            return a == e or a_base == e_base or e in a or a in e

        if not any(matches(n, expected) for n in names):
            print(
                f"  SKIP: current file doesn't match expected wrong "
                f"'{expected}'"
            )
            continue

        try:
            clear_file(page_id)
            print(f"  REMOVED: cleared File property (was '{names}')")
        except Exception as e:
            print(f"  ERROR clearing: {e}")


if __name__ == "__main__":
    run()
