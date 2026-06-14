#!/usr/bin/env python3
"""
Resource Coverage Audit for ID Codex.

Queries the live Notion Courses and Resources databases, cross-references them,
and produces a graded tracking table showing which courses need more resources.

Grading:
  - Workshop/Studio (14 weeks): target ~14 resources minimum
  - Seminar (7 weeks): target ~7 resources minimum
  - A = >=100% of target, B = 50-99%, C = 1-49%, F = 0 resources

Output: RESOURCE-GAPS.md
"""

import os
import json
import ssl
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime

# ── Configuration ─────────────────────────────────────────────────────────────

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

# Target resources per course type
TARGETS = {
    "Workshop": 14,
    "Studio": 14,
    "Seminar": 7,
}
DEFAULT_TARGET = 14

OUTPUT_FILE = "/Users/idstuart/Projects/idcodex/reports/RESOURCE-GAPS.md"


# ── API helpers ───────────────────────────────────────────────────────────────

def _api_request(method, path, body=None):
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


def _query_database(database_id, filter_obj=None):
    all_pages = []
    start_cursor = None
    while True:
        body = {}
        if filter_obj:
            body["filter"] = filter_obj
        if start_cursor:
            body["start_cursor"] = start_cursor

        result = _api_request("POST", f"/databases/{database_id}/query", body)
        all_pages.extend(result.get("results", []))

        if result.get("has_more"):
            start_cursor = result.get("next_cursor")
            time.sleep(0.34)
        else:
            break
    return all_pages


# ── Property extractors ───────────────────────────────────────────────────────

def _get_title(page, prop_name="Title"):
    prop = page.get("properties", {}).get(prop_name, {})
    title_arr = prop.get("title", [])
    return "".join(t.get("plain_text", "") for t in title_arr) if title_arr else ""


def _get_rich_text(page, prop_name):
    prop = page.get("properties", {}).get(prop_name, {})
    arr = prop.get("rich_text", [])
    return "".join(t.get("plain_text", "") for t in arr) if arr else ""


def _get_select(page, prop_name):
    prop = page.get("properties", {}).get(prop_name, {})
    sel = prop.get("select")
    return sel.get("name", "") if sel else ""


def _get_status(page, prop_name):
    prop = page.get("properties", {}).get(prop_name, {})
    st = prop.get("status")
    return st.get("name", "") if st else ""


def _get_multi_select(page, prop_name):
    prop = page.get("properties", {}).get(prop_name, {})
    return [s.get("name", "") for s in prop.get("multi_select", [])]


def _get_relation_ids(page, prop_name):
    prop = page.get("properties", {}).get(prop_name, {})
    return [r.get("id", "") for r in prop.get("relation", [])]


def _get_number(page, prop_name):
    prop = page.get("properties", {}).get(prop_name, {})
    return prop.get("number")


# ── Data loading ──────────────────────────────────────────────────────────────

def load_courses():
    print("Loading courses from Notion...", file=sys.stderr)
    pages = _query_database(COURSES_DB)
    courses = []
    for p in pages:
        if p.get("archived"):
            continue
        title = _get_title(p, "Name") or _get_title(p, "Title") or _get_title(p, "Course Name")
        course_type = _get_select(p, "Type")
        status = _get_select(p, "Status") or _get_status(p, "Status")
        category = _get_select(p, "Category")
        number = _get_rich_text(p, "Course Number") or _get_rich_text(p, "Number")
        credits = _get_number(p, "Credits")
        former_names = _get_rich_text(p, "Former Names") or _get_rich_text(p, "Former Course Name")
        programs = _get_relation_ids(p, "Programs")
        semesters = _get_multi_select(p, "Semester Offered")

        courses.append({
            "id": p["id"],
            "name": title,
            "number": number,
            "type": course_type,
            "status": status,
            "category": category,
            "credits": credits,
            "former_names": former_names,
            "programs": programs,
            "semesters": semesters,
            "url": p.get("url", ""),
        })
    print(f"  Loaded {len(courses)} courses.", file=sys.stderr)
    return courses


def load_resources():
    print("Loading resources from Notion...", file=sys.stderr)
    pages = _query_database(RESOURCES_DB)
    resources = []
    for p in pages:
        if p.get("archived"):
            continue
        title = _get_title(p, "Title") or _get_title(p, "Name")
        res_type = _get_select(p, "Type")
        semester = _get_select(p, "Semester")
        course_ids = _get_relation_ids(p, "Courses")

        resources.append({
            "id": p["id"],
            "title": title,
            "type": res_type,
            "semester": semester,
            "course_ids": course_ids,
        })
    print(f"  Loaded {len(resources)} resources.", file=sys.stderr)
    return resources


# ── Analysis ──────────────────────────────────────────────────────────────────

def analyze(courses, resources):
    # Build course_id -> list of resources
    course_resources = {}
    orphan_resources = []

    for r in resources:
        if not r["course_ids"]:
            orphan_resources.append(r)
            continue
        for cid in r["course_ids"]:
            course_resources.setdefault(cid, []).append(r)

    results = []
    for c in courses:
        cid = c["id"]
        linked = course_resources.get(cid, [])
        count = len(linked)

        # Determine target
        ctype = c["type"]
        target = TARGETS.get(ctype, DEFAULT_TARGET)

        # Calculate percentage and grade
        if count == 0:
            pct = 0
            grade = "F"
        else:
            pct = round(count / target * 100)
            if pct >= 100:
                grade = "A"
            elif pct >= 50:
                grade = "B"
            else:
                grade = "C"

        # Resource type breakdown
        type_counts = {}
        for r in linked:
            rt = r["type"] or "Unknown"
            type_counts[rt] = type_counts.get(rt, 0) + 1

        # Semesters covered
        semesters_with_resources = set()
        for r in linked:
            if r["semester"]:
                semesters_with_resources.add(r["semester"])

        gap = max(0, target - count)

        results.append({
            "name": c["name"],
            "number": c["number"],
            "type": ctype or "—",
            "status": c["status"] or "—",
            "category": c["category"] or "—",
            "credits": c["credits"],
            "count": count,
            "target": target,
            "pct": pct,
            "grade": grade,
            "gap": gap,
            "type_breakdown": type_counts,
            "semesters_covered": sorted(semesters_with_resources),
            "former_names": c["former_names"],
            "url": c["url"],
        })

    # Sort: F first, then C, B, A. Within same grade, sort by count ascending
    grade_order = {"F": 0, "C": 1, "B": 2, "A": 3}
    results.sort(key=lambda r: (grade_order.get(r["grade"], 99), r["count"], r["name"]))

    return results, orphan_resources


# ── Output generation ─────────────────────────────────────────────────────────

def generate_report(results, orphan_resources, total_courses, total_resources):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Summary stats
    grade_counts = {"F": 0, "C": 0, "B": 0, "A": 0}
    for r in results:
        grade_counts[r["grade"]] = grade_counts.get(r["grade"], 0) + 1

    # Filter out Merged courses for the main table
    active_results = [r for r in results if r["status"] != "Merged"]
    merged_results = [r for r in results if r["status"] == "Merged"]

    lines = []
    lines.append("# ID Codex — Resource Coverage Gap Analysis")
    lines.append("")
    lines.append(f"**Generated:** {now}")
    lines.append(f"**Total courses in DB:** {total_courses}")
    lines.append(f"**Total resources in DB:** {total_resources}")
    lines.append(f"**Orphan resources** (not linked to any course): {len(orphan_resources)}")
    lines.append("")

    lines.append("## Summary")
    lines.append("")
    lines.append("| Grade | Meaning | Count |")
    lines.append("|-------|---------|-------|")
    lines.append(f"| **F** | No resources at all | {grade_counts['F']} |")
    lines.append(f"| **C** | Minimal (1–49% of target) | {grade_counts['C']} |")
    lines.append(f"| **B** | Partial (50–99% of target) | {grade_counts['B']} |")
    lines.append(f"| **A** | Full coverage (≥100% of target) | {grade_counts['A']} |")
    lines.append("")

    lines.append("**Targets:** Workshop/Studio = 14 resources (14 weeks), Seminar = 7 resources (7 weeks)")
    lines.append("")

    # ── Priority: F-graded courses (NOTHING) ──────────────────────────────────
    f_courses = [r for r in active_results if r["grade"] == "F"]
    if f_courses:
        lines.append("---")
        lines.append("")
        lines.append("## Grade F — No Resources (Priority: Critical)")
        lines.append("")
        lines.append("These courses have **zero** resources. Any contribution helps.")
        lines.append("")
        lines.append("| # | Course | Number | Type | Status | Category | Target | Action Needed |")
        lines.append("|---|--------|--------|------|--------|----------|--------|---------------|")
        for i, r in enumerate(f_courses, 1):
            lines.append(
                f"| {i} | {r['name']} | {r['number'] or '—'} | {r['type']} | {r['status']} | {r['category']} | {r['target']} | Need {r['target']}+ resources |"
            )
        lines.append("")

    # ── C-graded courses (MINIMAL) ────────────────────────────────────────────
    c_courses = [r for r in active_results if r["grade"] == "C"]
    if c_courses:
        lines.append("---")
        lines.append("")
        lines.append("## Grade C — Minimal Coverage (Priority: High)")
        lines.append("")
        lines.append("These courses have some resources but are well below target.")
        lines.append("")
        lines.append("| # | Course | Number | Type | Status | Have | Target | Gap | % | Breakdown |")
        lines.append("|---|--------|--------|------|--------|------|--------|-----|---|-----------|")
        for i, r in enumerate(c_courses, 1):
            breakdown = ", ".join(f"{v} {k}" for k, v in sorted(r["type_breakdown"].items(), key=lambda x: -x[1]))
            lines.append(
                f"| {i} | {r['name']} | {r['number'] or '—'} | {r['type']} | {r['status']} | {r['count']} | {r['target']} | {r['gap']} | {r['pct']}% | {breakdown} |"
            )
        lines.append("")

    # ── B-graded courses (PARTIAL) ────────────────────────────────────────────
    b_courses = [r for r in active_results if r["grade"] == "B"]
    if b_courses:
        lines.append("---")
        lines.append("")
        lines.append("## Grade B — Partial Coverage (Priority: Medium)")
        lines.append("")
        lines.append("These courses are making progress but still have gaps.")
        lines.append("")
        lines.append("| # | Course | Number | Type | Status | Have | Target | Gap | % | Breakdown |")
        lines.append("|---|--------|--------|------|--------|------|--------|-----|---|-----------|")
        for i, r in enumerate(b_courses, 1):
            breakdown = ", ".join(f"{v} {k}" for k, v in sorted(r["type_breakdown"].items(), key=lambda x: -x[1]))
            lines.append(
                f"| {i} | {r['name']} | {r['number'] or '—'} | {r['type']} | {r['status']} | {r['count']} | {r['target']} | {r['gap']} | {r['pct']}% | {breakdown} |"
            )
        lines.append("")

    # ── A-graded courses (FULL) ───────────────────────────────────────────────
    a_courses = [r for r in active_results if r["grade"] == "A"]
    if a_courses:
        lines.append("---")
        lines.append("")
        lines.append("## Grade A — Full Coverage")
        lines.append("")
        lines.append("These courses meet or exceed the target. Well done!")
        lines.append("")
        lines.append("| # | Course | Number | Type | Status | Have | Target | % | Breakdown |")
        lines.append("|---|--------|--------|------|--------|------|--------|---|-----------|")
        for i, r in enumerate(a_courses, 1):
            breakdown = ", ".join(f"{v} {k}" for k, v in sorted(r["type_breakdown"].items(), key=lambda x: -x[1]))
            lines.append(
                f"| {i} | {r['name']} | {r['number'] or '—'} | {r['type']} | {r['status']} | {r['count']} | {r['target']} | {r['pct']}% | {breakdown} |"
            )
        lines.append("")

    # ── Merged courses (informational) ────────────────────────────────────────
    if merged_results:
        lines.append("---")
        lines.append("")
        lines.append("## Merged Courses (Informational)")
        lines.append("")
        lines.append("These courses have been consolidated into other courses. Resources should be on the target course.")
        lines.append("")
        lines.append("| Course | Number | Resources | Former Names |")
        lines.append("|--------|--------|-----------|--------------|")
        for r in merged_results:
            lines.append(
                f"| {r['name']} | {r['number'] or '—'} | {r['count']} | {r['former_names'] or '—'} |"
            )
        lines.append("")

    # ── Orphan resources ──────────────────────────────────────────────────────
    if orphan_resources:
        lines.append("---")
        lines.append("")
        lines.append("## Orphan Resources (No Course Link)")
        lines.append("")
        lines.append("These resources exist in the DB but aren't linked to any course.")
        lines.append("")
        lines.append("| Title | Type | Semester |")
        lines.append("|-------|------|----------|")
        for r in sorted(orphan_resources, key=lambda x: x["title"].lower()):
            lines.append(f"| {r['title']} | {r['type'] or '—'} | {r['semester'] or '—'} |")
        lines.append("")

    # ── Contribution request template ─────────────────────────────────────────
    lines.append("---")
    lines.append("")
    lines.append("## How to Contribute")
    lines.append("")
    lines.append("If you have materials (syllabi, lecture slides, readings, project briefs, videos) for any course listed above:")
    lines.append("")
    lines.append("1. Check the **Grade** column — F and C courses are the highest priority")
    lines.append("2. Share files via Google Drive, Dropbox, or email to the ID Codex admin")
    lines.append("3. Include the **course name** and **semester** you took it")
    lines.append("4. Any format accepted: PDF, PPTX, DOCX, links, videos")
    lines.append("")
    lines.append("Every contribution helps preserve ID's collective knowledge for future students.")
    lines.append("")

    return "\n".join(lines)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60, file=sys.stderr)
    print("  ID Codex — Resource Coverage Audit", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    print("", file=sys.stderr)

    # Load data
    courses = load_courses()
    resources = load_resources()

    # Analyze
    print("\nAnalyzing coverage...", file=sys.stderr)
    results, orphans = analyze(courses, resources)

    # Generate report
    report = generate_report(results, orphans, len(courses), len(resources))

    # Write output
    with open(OUTPUT_FILE, "w") as f:
        f.write(report)
    print(f"\nReport written to {OUTPUT_FILE}", file=sys.stderr)

    # Print summary to stderr
    grade_counts = {}
    for r in results:
        grade_counts[r["grade"]] = grade_counts.get(r["grade"], 0) + 1

    print(f"\n  Grade F (nothing):  {grade_counts.get('F', 0)}", file=sys.stderr)
    print(f"  Grade C (minimal):  {grade_counts.get('C', 0)}", file=sys.stderr)
    print(f"  Grade B (partial):  {grade_counts.get('B', 0)}", file=sys.stderr)
    print(f"  Grade A (full):     {grade_counts.get('A', 0)}", file=sys.stderr)
    print(f"  Orphan resources:   {len(orphans)}", file=sys.stderr)
    print("", file=sys.stderr)

    # Also dump raw JSON for further processing
    json_output = "/Users/idstuart/Projects/idcodex/data/audit_results.json"
    with open(json_output, "w") as f:
        json.dump({
            "generated": datetime.now().isoformat(),
            "total_courses": len(courses),
            "total_resources": len(resources),
            "orphan_count": len(orphans),
            "grade_counts": grade_counts,
            "results": results,
            "orphans": [{"id": o["id"], "title": o["title"], "type": o["type"]} for o in orphans],
        }, f, indent=2)
    print(f"  Raw data: {json_output}", file=sys.stderr)


if __name__ == "__main__":
    main()
