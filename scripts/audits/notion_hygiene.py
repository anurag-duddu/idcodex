#!/usr/bin/env python3
"""
Notion Data Hygiene Toolkit for ID Codex.

A CLI for auditing, cleaning, and managing the Resources and Courses databases.
Supports listing, duplicate detection, merging, deletion, updates, and stats.

Usage:
    python notion_hygiene.py stats
    python notion_hygiene.py list-resources [--course "CourseName"] [--format csv]
    python notion_hygiene.py list-courses
    python notion_hygiene.py find-duplicates [--threshold 0.85]
    python notion_hygiene.py delete-resource ID [--confirm]
    python notion_hygiene.py delete-resource --batch ID1,ID2,ID3 [--confirm]
    python notion_hygiene.py merge-courses SOURCE_ID TARGET_ID [--confirm]
    python notion_hygiene.py merge-resources KEEP_ID DELETE_ID [--confirm]
    python notion_hygiene.py update-resource ID [--title "X"] [--author "X"] [--type "X"] [--semester "X"] [--confirm]
"""

import os
import argparse
import csv
import difflib
import io
import json
import ssl
import sys
import time
import urllib.error
import urllib.request

# ── Configuration ──────────────────────────────────────────────────────────────

API_KEY = os.environ.get("NOTION_API_KEY")
RESOURCES_DB = "dd4ea6d9-92b4-4f28-b75c-ecb7f6b851be"
COURSES_DB = "f6d577cb-5358-468c-9981-2ede7a140638"
NOTION_VERSION = "2022-06-28"
BASE_URL = "https://api.notion.com/v1"

SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Notion-Version": NOTION_VERSION,
    "Content-Type": "application/json",
}


# ── Low-level API helpers ─────────────────────────────────────────────────────

def _api_request(method, path, body=None):
    """Make a Notion API request. Returns parsed JSON or raises."""
    url = f"{BASE_URL}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req, context=SSL_CTX) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"  API ERROR ({e.code}): {error_body[:300]}", file=sys.stderr)
        raise


def _query_database(database_id, filter_obj=None, sorts=None):
    """Query a Notion database with full pagination. Returns all pages."""
    all_pages = []
    start_cursor = None
    while True:
        body = {}
        if filter_obj:
            body["filter"] = filter_obj
        if sorts:
            body["sorts"] = sorts
        if start_cursor:
            body["start_cursor"] = start_cursor

        result = _api_request("POST", f"/databases/{database_id}/query", body)
        all_pages.extend(result.get("results", []))

        if result.get("has_more"):
            start_cursor = result.get("next_cursor")
            time.sleep(0.34)  # rate-limit courtesy
        else:
            break
    return all_pages


# ── Property extraction helpers ────────────────────────────────────────────────

def _get_title(page, prop_name="Title"):
    """Extract plain text from a title property."""
    prop = page.get("properties", {}).get(prop_name, {})
    title_arr = prop.get("title", [])
    return "".join(t.get("plain_text", "") for t in title_arr) if title_arr else ""


def _get_rich_text(page, prop_name):
    """Extract plain text from a rich_text property."""
    prop = page.get("properties", {}).get(prop_name, {})
    arr = prop.get("rich_text", [])
    return "".join(t.get("plain_text", "") for t in arr) if arr else ""


def _get_select(page, prop_name):
    """Extract name from a select property."""
    prop = page.get("properties", {}).get(prop_name, {})
    sel = prop.get("select")
    return sel.get("name", "") if sel else ""


def _get_multi_select(page, prop_name):
    """Extract list of names from a multi_select property."""
    prop = page.get("properties", {}).get(prop_name, {})
    return [s.get("name", "") for s in prop.get("multi_select", [])]


def _get_relation_ids(page, prop_name):
    """Extract list of related page IDs from a relation property."""
    prop = page.get("properties", {}).get(prop_name, {})
    return [r.get("id", "") for r in prop.get("relation", [])]


def _get_number(page, prop_name):
    """Extract number value from a number property."""
    prop = page.get("properties", {}).get(prop_name, {})
    return prop.get("number")


def _get_status(page, prop_name):
    """Extract name from a status property."""
    prop = page.get("properties", {}).get(prop_name, {})
    st = prop.get("status")
    return st.get("name", "") if st else ""


# ── Data loading ───────────────────────────────────────────────────────────────

def load_all_resources(course_filter=None):
    """Load all resources, optionally filtered by course name substring."""
    pages = _query_database(RESOURCES_DB)
    resources = []
    for p in pages:
        if p.get("archived"):
            continue
        resources.append({
            "id": p["id"],
            "title": _get_title(p, "Title") or _get_title(p, "Name"),
            "author": _get_rich_text(p, "Author(s)"),
            "type": _get_select(p, "Type"),
            "semester": _get_select(p, "Semester"),
            "course_ids": _get_relation_ids(p, "Courses"),
            "url": p.get("url", ""),
        })

    if course_filter:
        # We need course names to filter; build id->name map
        course_map = _build_course_id_map()
        filtered = []
        for r in resources:
            course_names = [course_map.get(cid, "") for cid in r["course_ids"]]
            if any(course_filter.lower() in cn.lower() for cn in course_names):
                r["course_names"] = course_names
                filtered.append(r)
        return filtered

    return resources


def load_all_courses():
    """Load all courses from the Courses database."""
    pages = _query_database(COURSES_DB)
    courses = []
    for p in pages:
        if p.get("archived"):
            continue
        # Try several common property names for the title
        title = _get_title(p, "Name") or _get_title(p, "Title") or _get_title(p, "Course Name")
        courses.append({
            "id": p["id"],
            "name": title,
            "number": _get_rich_text(p, "Course Number") or _get_rich_text(p, "Number"),
            "former_names": _get_rich_text(p, "Former Names") or _get_rich_text(p, "Former Course Name") or _get_rich_text(p, "Former Name"),
            "status": _get_select(p, "Status") or _get_status(p, "Status"),
            "url": p.get("url", ""),
        })
    return courses


def _build_course_id_map():
    """Return {course_page_id: course_name} dict."""
    courses = load_all_courses()
    return {c["id"]: c["name"] for c in courses}


# ── Commands ───────────────────────────────────────────────────────────────────

def cmd_list_resources(args):
    """List all resources with key fields."""
    print("Loading resources...", file=sys.stderr)
    resources = load_all_resources(course_filter=args.course)

    # Resolve course names for display
    if not args.course:
        course_map = _build_course_id_map()
        for r in resources:
            r["course_names"] = [course_map.get(cid, cid) for cid in r["course_ids"]]

    resources.sort(key=lambda r: r["title"].lower())

    if args.format == "csv":
        _print_resources_csv(resources)
    else:
        _print_resources_table(resources)

    print(f"\n{len(resources)} resource(s) found.", file=sys.stderr)


def _print_resources_table(resources):
    if not resources:
        print("No resources found.")
        return

    # Calculate column widths
    id_w = 36
    title_w = max((len(r["title"]) for r in resources), default=5)
    title_w = min(title_w, 55)
    type_w = max((len(r["type"]) for r in resources), default=4)
    type_w = min(type_w, 15)
    sem_w = max((len(r["semester"]) for r in resources), default=8)
    sem_w = min(sem_w, 15)

    header = f"{'ID':<{id_w}}  {'Title':<{title_w}}  {'Type':<{type_w}}  {'Semester':<{sem_w}}  Courses"
    print(header)
    print("-" * len(header))

    for r in resources:
        title = r["title"][:title_w]
        rtype = r["type"][:type_w]
        sem = r["semester"][:sem_w]
        courses = ", ".join(r.get("course_names", [])) or "(none)"
        print(f"{r['id']:<{id_w}}  {title:<{title_w}}  {rtype:<{type_w}}  {sem:<{sem_w}}  {courses}")


def _print_resources_csv(resources):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Title", "Author", "Type", "Semester", "Courses"])
    for r in resources:
        courses = "; ".join(r.get("course_names", []))
        writer.writerow([r["id"], r["title"], r["author"], r["type"], r["semester"], courses])
    print(output.getvalue(), end="")


def cmd_list_courses(args):
    """List all courses with key fields."""
    print("Loading courses...", file=sys.stderr)
    courses = load_all_courses()
    courses.sort(key=lambda c: c["name"].lower())

    if not courses:
        print("No courses found.")
        return

    # Determine column widths
    id_w = 36
    name_w = min(max((len(c["name"]) for c in courses), default=10), 55)
    num_w = min(max((len(c["number"]) for c in courses), default=6), 15)
    status_w = min(max((len(c["status"]) for c in courses), default=6), 20)

    header = f"{'ID':<{id_w}}  {'Name':<{name_w}}  {'Number':<{num_w}}  {'Status':<{status_w}}  Former Names"
    print(header)
    print("-" * len(header))

    for c in courses:
        name = c["name"][:name_w]
        num = c["number"][:num_w]
        status = c["status"][:status_w]
        former = c["former_names"][:40] if c["former_names"] else ""
        print(f"{c['id']:<{id_w}}  {name:<{name_w}}  {num:<{num_w}}  {status:<{status_w}}  {former}")

    print(f"\n{len(courses)} course(s) found.", file=sys.stderr)


def cmd_find_duplicates(args):
    """Find potential duplicate resources using fuzzy matching."""
    print("Loading resources...", file=sys.stderr)
    resources = load_all_resources()
    threshold = args.threshold

    print(f"Scanning {len(resources)} resources for duplicates (threshold={threshold})...\n")

    pairs_found = []
    for i in range(len(resources)):
        for j in range(i + 1, len(resources)):
            t1 = resources[i]["title"].lower().strip()
            t2 = resources[j]["title"].lower().strip()
            if not t1 or not t2:
                continue
            ratio = difflib.SequenceMatcher(None, t1, t2).ratio()
            if ratio >= threshold:
                pairs_found.append((resources[i], resources[j], ratio))

    if not pairs_found:
        print("No potential duplicates found.")
        return

    pairs_found.sort(key=lambda x: x[2], reverse=True)
    print(f"Found {len(pairs_found)} potential duplicate pair(s):\n")

    for r1, r2, score in pairs_found:
        print(f"  Similarity: {score:.2%}")
        print(f"    A: {r1['title']}")
        print(f"       ID={r1['id']}  Type={r1['type']}  Semester={r1['semester']}")
        print(f"    B: {r2['title']}")
        print(f"       ID={r2['id']}  Type={r2['type']}  Semester={r2['semester']}")
        print()


def cmd_delete_resource(args):
    """Delete (archive) one or more resources."""
    ids_to_delete = []

    if args.batch:
        ids_to_delete = [x.strip() for x in args.batch.split(",") if x.strip()]
    elif args.id:
        ids_to_delete = [args.id]
    else:
        print("Error: Provide a resource ID or --batch ID1,ID2,ID3", file=sys.stderr)
        sys.exit(1)

    print(f"Will archive {len(ids_to_delete)} resource(s):")
    for rid in ids_to_delete:
        # Fetch title for display
        try:
            page = _api_request("GET", f"/pages/{rid}")
            title = _get_title(page, "Title") or _get_title(page, "Name") or "(untitled)"
            print(f"  - {title}  (ID: {rid})")
        except Exception:
            print(f"  - (could not fetch)  (ID: {rid})")

    if not args.confirm:
        print("\nDry run. Add --confirm to execute.", file=sys.stderr)
        return

    print("\nArchiving...")
    for rid in ids_to_delete:
        try:
            _api_request("PATCH", f"/pages/{rid}", {"archived": True})
            print(f"  Archived: {rid}")
            time.sleep(0.34)
        except Exception as e:
            print(f"  FAILED: {rid} ({e})")


def cmd_merge_courses(args):
    """Move all resources from source course to target, then mark source as Merged."""
    source_id = args.source_id
    target_id = args.target_id

    print("Loading source and target course details...")
    try:
        source_page = _api_request("GET", f"/pages/{source_id}")
        target_page = _api_request("GET", f"/pages/{target_id}")
    except Exception:
        print("Error: Could not fetch one or both course pages.", file=sys.stderr)
        sys.exit(1)

    source_name = _get_title(source_page, "Name") or _get_title(source_page, "Title") or "(untitled)"
    target_name = _get_title(target_page, "Name") or _get_title(target_page, "Title") or "(untitled)"

    print(f"  Source: {source_name} ({source_id})")
    print(f"  Target: {target_name} ({target_id})")

    # Find resources linked to source course
    print("\nScanning resources linked to source course...")
    all_resources = load_all_resources()
    linked = [r for r in all_resources if source_id in r["course_ids"]]
    print(f"  Found {len(linked)} resource(s) linked to source course.")

    for r in linked:
        print(f"    - {r['title']}")

    if not args.confirm:
        print("\nDry run. Add --confirm to execute.", file=sys.stderr)
        return

    # Move each resource: replace source_id with target_id in its Courses relation
    print("\nMoving resources to target course...")
    for r in linked:
        new_ids = [cid for cid in r["course_ids"] if cid != source_id]
        if target_id not in new_ids:
            new_ids.append(target_id)
        relation_payload = [{"id": cid} for cid in new_ids]
        try:
            _api_request("PATCH", f"/pages/{r['id']}", {
                "properties": {
                    "Courses": {"relation": relation_payload}
                }
            })
            print(f"  Moved: {r['title']}")
            time.sleep(0.34)
        except Exception as e:
            print(f"  FAILED to move {r['title']}: {e}")

    # Mark source course as Merged with note
    print(f"\nMarking source course as 'Merged'...")
    update_props = {}
    # Try to set status — may be select or status type
    update_props["Status"] = {"select": {"name": "Merged"}}

    # Append to Former Names
    existing_former = _get_rich_text(source_page, "Former Names") or _get_rich_text(source_page, "Former Course Name") or ""
    merge_note = f"Merged into: {target_name}"
    new_former = f"{existing_former}; {merge_note}" if existing_former else merge_note

    # Try the most likely property name
    for prop_name in ["Former Names", "Former Course Name", "Former Name"]:
        if prop_name in source_page.get("properties", {}):
            update_props[prop_name] = {"rich_text": [{"text": {"content": new_former}}]}
            break

    try:
        _api_request("PATCH", f"/pages/{source_id}", {"properties": update_props})
        print("  Done.")
    except Exception as e:
        print(f"  Warning: Could not update source course status: {e}")
        # Try with status type instead of select
        try:
            update_props["Status"] = {"status": {"name": "Merged"}}
            _api_request("PATCH", f"/pages/{source_id}", {"properties": update_props})
            print("  Done (used status property type).")
        except Exception as e2:
            print(f"  Could not set status even as status type: {e2}")


def cmd_merge_resources(args):
    """Keep one resource and delete the other, merging course relations."""
    keep_id = args.keep_id
    delete_id = args.delete_id

    print("Loading resource details...")
    try:
        keep_page = _api_request("GET", f"/pages/{keep_id}")
        delete_page = _api_request("GET", f"/pages/{delete_id}")
    except Exception:
        print("Error: Could not fetch one or both resource pages.", file=sys.stderr)
        sys.exit(1)

    keep_title = _get_title(keep_page, "Title") or _get_title(keep_page, "Name") or "(untitled)"
    delete_title = _get_title(delete_page, "Title") or _get_title(delete_page, "Name") or "(untitled)"
    keep_courses = _get_relation_ids(keep_page, "Courses")
    delete_courses = _get_relation_ids(delete_page, "Courses")

    # Find courses in delete that aren't in keep
    new_courses = [cid for cid in delete_courses if cid not in keep_courses]

    print(f"  KEEP:   {keep_title} (ID: {keep_id})")
    print(f"  DELETE: {delete_title} (ID: {delete_id})")
    if new_courses:
        print(f"  Will add {len(new_courses)} course relation(s) from deleted to kept resource.")
    else:
        print(f"  No additional course relations to merge.")

    if not args.confirm:
        print("\nDry run. Add --confirm to execute.", file=sys.stderr)
        return

    # Add missing course relations to kept resource
    if new_courses:
        merged_courses = keep_courses + new_courses
        relation_payload = [{"id": cid} for cid in merged_courses]
        try:
            _api_request("PATCH", f"/pages/{keep_id}", {
                "properties": {
                    "Courses": {"relation": relation_payload}
                }
            })
            print(f"  Updated course relations on kept resource.")
        except Exception as e:
            print(f"  Warning: Could not update relations: {e}")

    # Archive the duplicate
    try:
        _api_request("PATCH", f"/pages/{delete_id}", {"archived": True})
        print(f"  Archived: {delete_title}")
    except Exception as e:
        print(f"  FAILED to archive: {e}")


def cmd_update_resource(args):
    """Update fields on a resource."""
    rid = args.id

    print(f"Loading resource {rid}...")
    try:
        page = _api_request("GET", f"/pages/{rid}")
    except Exception:
        print("Error: Could not fetch resource.", file=sys.stderr)
        sys.exit(1)

    current_title = _get_title(page, "Title") or _get_title(page, "Name") or "(untitled)"
    print(f"  Current title: {current_title}")

    updates = {}
    changes_desc = []

    if args.title:
        updates["Title"] = {"title": [{"text": {"content": args.title}}]}
        changes_desc.append(f"  title -> {args.title}")

    if args.author:
        updates["Author(s)"] = {"rich_text": [{"text": {"content": args.author}}]}
        changes_desc.append(f"  author -> {args.author}")

    if args.type:
        updates["Type"] = {"select": {"name": args.type}}
        changes_desc.append(f"  type -> {args.type}")

    if args.semester:
        updates["Semester"] = {"select": {"name": args.semester}}
        changes_desc.append(f"  semester -> {args.semester}")

    if not updates:
        print("No updates specified. Use --title, --author, --type, or --semester.")
        return

    print("Planned changes:")
    for desc in changes_desc:
        print(desc)

    if not args.confirm:
        print("\nDry run. Add --confirm to execute.", file=sys.stderr)
        return

    try:
        _api_request("PATCH", f"/pages/{rid}", {"properties": updates})
        print("  Updated successfully.")
    except Exception as e:
        print(f"  FAILED: {e}")


def cmd_stats(args):
    """Print summary statistics about the Resources database."""
    print("Loading resources...", file=sys.stderr)
    resources = load_all_resources()
    print("Loading courses...", file=sys.stderr)
    course_map = _build_course_id_map()

    total = len(resources)
    print(f"\n{'='*60}")
    print(f" Resources Database Statistics")
    print(f"{'='*60}")
    print(f"\n Total resources: {total}\n")

    # By type
    by_type = {}
    for r in resources:
        t = r["type"] or "(no type)"
        by_type[t] = by_type.get(t, 0) + 1

    print(" By Type:")
    for t in sorted(by_type, key=lambda x: by_type[x], reverse=True):
        print(f"   {t:<25} {by_type[t]:>4}")

    # By semester
    by_semester = {}
    for r in resources:
        s = r["semester"] or "(no semester)"
        by_semester[s] = by_semester.get(s, 0) + 1

    print(f"\n By Semester:")
    for s in sorted(by_semester, key=lambda x: by_semester[x], reverse=True):
        print(f"   {s:<25} {by_semester[s]:>4}")

    # By course
    by_course = {}
    orphaned = 0
    for r in resources:
        if not r["course_ids"]:
            orphaned += 1
        for cid in r["course_ids"]:
            cname = course_map.get(cid, cid)
            by_course[cname] = by_course.get(cname, 0) + 1

    print(f"\n By Course:")
    for c in sorted(by_course, key=lambda x: by_course[x], reverse=True):
        print(f"   {c:<50} {by_course[c]:>4}")

    print(f"\n Orphaned (no course link): {orphaned}")
    print(f"{'='*60}\n")


# ── CLI argument parsing ──────────────────────────────────────────────────────

def build_parser():
    parser = argparse.ArgumentParser(
        description="Notion Data Hygiene Toolkit for ID Codex",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # list-resources
    p_lr = subparsers.add_parser("list-resources", help="List all resources")
    p_lr.add_argument("--course", type=str, default=None, help="Filter by course name (substring match)")
    p_lr.add_argument("--format", type=str, choices=["table", "csv"], default="table", help="Output format")

    # list-courses
    subparsers.add_parser("list-courses", help="List all courses")

    # find-duplicates
    p_fd = subparsers.add_parser("find-duplicates", help="Find potential duplicate resources")
    p_fd.add_argument("--threshold", type=float, default=0.85, help="Similarity threshold (0.0-1.0, default 0.85)")

    # delete-resource
    p_dr = subparsers.add_parser("delete-resource", help="Archive a resource by ID")
    p_dr.add_argument("id", nargs="?", default=None, help="Resource page ID to delete")
    p_dr.add_argument("--batch", type=str, default=None, help="Comma-separated list of IDs to delete")
    p_dr.add_argument("--confirm", action="store_true", help="Actually execute the deletion")

    # merge-courses
    p_mc = subparsers.add_parser("merge-courses", help="Move resources from one course to another")
    p_mc.add_argument("source_id", help="Source course ID (will be marked Merged)")
    p_mc.add_argument("target_id", help="Target course ID (receives resources)")
    p_mc.add_argument("--confirm", action="store_true", help="Actually execute the merge")

    # merge-resources
    p_mr = subparsers.add_parser("merge-resources", help="Merge two resources, keeping one")
    p_mr.add_argument("keep_id", help="ID of resource to keep")
    p_mr.add_argument("delete_id", help="ID of resource to delete")
    p_mr.add_argument("--confirm", action="store_true", help="Actually execute the merge")

    # update-resource
    p_ur = subparsers.add_parser("update-resource", help="Update fields on a resource")
    p_ur.add_argument("id", help="Resource page ID")
    p_ur.add_argument("--title", type=str, default=None, help="New title")
    p_ur.add_argument("--author", type=str, default=None, help="New author")
    p_ur.add_argument("--type", type=str, default=None, help="New type (e.g., Book, Paper, Article)")
    p_ur.add_argument("--semester", type=str, default=None, help="New semester (e.g., Fall 2024)")
    p_ur.add_argument("--confirm", action="store_true", help="Actually execute the update")

    # stats
    subparsers.add_parser("stats", help="Print summary statistics")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    dispatch = {
        "list-resources": cmd_list_resources,
        "list-courses": cmd_list_courses,
        "find-duplicates": cmd_find_duplicates,
        "delete-resource": cmd_delete_resource,
        "merge-courses": cmd_merge_courses,
        "merge-resources": cmd_merge_resources,
        "update-resource": cmd_update_resource,
        "stats": cmd_stats,
    }

    handler = dispatch.get(args.command)
    if handler:
        handler(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
