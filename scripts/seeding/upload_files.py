#!/usr/bin/env python3
"""
Upload PDF files from LaCie external drive to Notion Resources DB.

Two-phase approach:
  Phase 1: Build a mapping of Notion resources → local PDF files
  Phase 2: Upload matched files and attach them via the File property

Usage:
  python3 upload_files.py              # Run both phases (map then upload first 50)
  python3 upload_files.py --map-only   # Phase 1 only: build mapping, print stats
  python3 upload_files.py --upload N   # Phase 2 only: upload N files from existing map
  python3 upload_files.py --upload all # Upload all matched files
"""

import json
import os
import ssl
import sys
import time
import math
import urllib.request
import urllib.error
from difflib import SequenceMatcher
from pathlib import Path

# ── Configuration ──────────────────────────────────────────────────────────

API_KEY = os.environ.get("NOTION_API_KEY")
RESOURCES_DB = "dd4ea6d9-92b4-4f28-b75c-ecb7f6b851be"
NOTION_VERSION = "2022-06-28"          # Standard version for queries
NOTION_VERSION_UPLOAD = "2026-03-11"   # Required for file uploads
MAP_FILE = "/Users/idstuart/Projects/idcodex/data/file_upload_map.json"

# SSL context (macOS Python workaround)
SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

# Directories to scan for PDFs
SCAN_DIRS = [
    "/Volumes/LaCie/Anurag@ID/Foundation Semester/",
    "/Volumes/LaCie/Anurag@ID/ID GDrive Backup/",
    "/Volumes/LaCie/Anurag@ID/Semester 1/",
    "/Volumes/LaCie/Anurag@ID/Semester 2/",
    "/Volumes/LaCie/Anurag@ID/Semester 3/",
    "/Volumes/LaCie/Anurag@ID/Semester 4/",
    "/Volumes/LaCie/Anurag@ID/Summer'25/",
    "/Volumes/LaCie/ID Complete Course Material/Contributions/SC Archive/",
]

# Directories to EXCLUDE entirely
EXCLUDE_DIR_NAMES = {
    "Working Documents", "Evaluation Sheets", "Class Photos",
    "Project Photos", "Presentation Assets", "Morph 3D Models",
    "IDSA", "Takeout", "Milan_Immersion",
}

# Filename substrings that indicate student work (case-insensitive)
EXCLUDE_FILENAME_SUBSTRINGS = ["anurag", "samantha", "samanthac"]

# Fuzzy match threshold
FUZZY_THRESHOLD = 0.67

# Rate limit between API calls (seconds)
RATE_LIMIT = 0.5

# Max file size for upload (100 MB)
MAX_FILE_SIZE = 100 * 1024 * 1024

# Multi-part threshold (20 MB)
MULTI_PART_THRESHOLD = 20 * 1024 * 1024

# Part size for multi-part uploads (20 MB)
PART_SIZE = 20 * 1024 * 1024


# ── Notion API Helpers ─────────────────────────────────────────────────────

def notion_request(method, url, body=None, content_type="application/json", use_upload_version=False):
    """Make a request to the Notion API."""
    version = NOTION_VERSION_UPLOAD if use_upload_version else NOTION_VERSION
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Notion-Version": version,
    }
    if content_type:
        headers["Content-Type"] = content_type

    data = None
    if body is not None and content_type == "application/json":
        data = json.dumps(body).encode()
    elif body is not None:
        data = body

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, context=SSL_CTX) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"  API ERROR ({e.code}): {error_body[:300]}", flush=True)
        raise


def fetch_all_resources():
    """Paginate through the entire Resources DB and return all entries."""
    resources = []
    has_more = True
    start_cursor = None

    while has_more:
        body = {"page_size": 100}
        if start_cursor:
            body["start_cursor"] = start_cursor

        data = notion_request(
            "POST",
            f"https://api.notion.com/v1/databases/{RESOURCES_DB}/query",
            body=body,
        )

        for page in data["results"]:
            title_arr = page["properties"]["Title"]["title"]
            title = title_arr[0]["plain_text"] if title_arr else ""

            type_prop = page["properties"]["Type"]["select"]
            resource_type = type_prop["name"] if type_prop else ""

            courses_prop = page["properties"]["Courses"]["relation"]
            course_ids = [c["id"] for c in courses_prop]

            file_prop = page["properties"]["File"]["files"]
            has_file = len(file_prop) > 0

            resources.append({
                "page_id": page["id"],
                "title": title,
                "type": resource_type,
                "course_ids": course_ids,
                "has_file": has_file,
            })

        has_more = data.get("has_more", False)
        start_cursor = data.get("next_cursor")
        print(f"  Fetched {len(resources)} resources so far...", flush=True)
        time.sleep(RATE_LIMIT)

    return resources


# ── File Scanning ──────────────────────────────────────────────────────────

def should_exclude_dir(dirpath):
    """Check if a directory should be excluded from scanning."""
    parts = Path(dirpath).parts
    for part in parts:
        if part in EXCLUDE_DIR_NAMES:
            return True
    return False


def should_exclude_file(filename):
    """Check if a filename indicates student work."""
    lower = filename.lower()
    for substr in EXCLUDE_FILENAME_SUBSTRINGS:
        if substr in lower:
            return True
    # Skip macOS resource fork files
    if filename.startswith("._"):
        return True
    return False


def scan_pdfs():
    """Recursively scan all configured directories for PDF files."""
    pdfs = []
    seen_paths = set()

    for scan_dir in SCAN_DIRS:
        if not os.path.isdir(scan_dir):
            print(f"  WARNING: Directory not found: {scan_dir}", flush=True)
            continue

        for root, dirs, files in os.walk(scan_dir):
            # Skip excluded directories (modify dirs in-place to prevent descent)
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIR_NAMES]

            if should_exclude_dir(root):
                continue

            for f in files:
                if not f.lower().endswith(".pdf"):
                    continue
                if should_exclude_file(f):
                    continue

                full_path = os.path.join(root, f)

                # Deduplicate by resolved path
                resolved = os.path.realpath(full_path)
                if resolved in seen_paths:
                    continue
                seen_paths.add(resolved)

                try:
                    size = os.path.getsize(full_path)
                except OSError:
                    continue

                pdfs.append({
                    "path": full_path,
                    "filename": f,
                    "stem": Path(f).stem,  # filename without extension
                    "size": size,
                })

    return pdfs


# ── Matching Logic ─────────────────────────────────────────────────────────

def clean_for_matching(text):
    """Normalize text for fuzzy matching."""
    import re
    text = text.lower().strip()
    # Remove leading numbers, dashes, underscores, dots
    text = re.sub(r'^[\d\s\.\-_]+', '', text)
    # Normalize separators
    text = re.sub(r'[_\-—]+', ' ', text)
    # Remove punctuation (colons, parens, brackets, etc.) but keep alphanumerics and spaces
    text = re.sub(r'[^\w\s]', '', text)
    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def is_generic_filename(stem):
    """Check if a filename is too generic to match reliably."""
    import re
    clean = stem.lower().strip()
    # Pure "Week N" or "Lecture N" type filenames
    if re.match(r'^(week|lecture|class|session|w)\s*\d+$', clean):
        return True
    # Single word or very short
    if len(clean) <= 3:
        return True
    return False


def match_resources_to_files(resources, pdfs):
    """
    Match Notion resources to PDF files using a two-pass approach:
    Pass 1: Exact matches (filename == title, case-insensitive)
    Pass 2: Fuzzy matches with 1-to-1 constraint (each PDF used at most once)

    Returns: (matched, unmatched_resources, unmatched_files)
    """
    import re

    matched = []
    unmatched_resources = []

    # Build lookup indices for PDFs
    stem_index = {}  # lowercase stem -> list of pdf entries
    for pdf in pdfs:
        key = pdf["stem"].lower().strip()
        stem_index.setdefault(key, []).append(pdf)

    # Track which PDFs and resources have been matched
    matched_pdf_paths = set()
    matched_resource_ids = set()

    # Resources that need files
    resources_needing = [r for r in resources if not r["has_file"] and r["title"]]
    resources_skip = [r for r in resources if r["has_file"] or not r["title"]]

    # ── Pass 1: Exact matches ──
    for resource in resources_needing:
        title = resource["title"]
        title_lower = title.lower().strip()
        title_clean = clean_for_matching(title)

        best_pdf = None

        # Check exact stem match
        if title_lower in stem_index:
            candidates = [c for c in stem_index[title_lower] if c["path"] not in matched_pdf_paths]
            if candidates:
                best_pdf = candidates[0]

        # Check exact match on cleaned versions
        if not best_pdf:
            for pdf in pdfs:
                if pdf["path"] in matched_pdf_paths:
                    continue
                if clean_for_matching(pdf["stem"]) == title_clean:
                    best_pdf = pdf
                    break

        if best_pdf:
            matched.append({
                "page_id": resource["page_id"],
                "title": resource["title"],
                "type": resource["type"],
                "file_path": best_pdf["path"],
                "file_name": best_pdf["filename"],
                "file_size": best_pdf["size"],
                "match_type": "exact",
                "match_score": 1.0,
            })
            matched_pdf_paths.add(best_pdf["path"])
            matched_resource_ids.add(resource["page_id"])

    # ── Pass 2: Fuzzy matches (1-to-1, best score wins) ──
    remaining_resources = [r for r in resources_needing if r["page_id"] not in matched_resource_ids]
    remaining_pdfs = [p for p in pdfs if p["path"] not in matched_pdf_paths]

    # Score all (resource, pdf) pairs
    candidates = []
    for resource in remaining_resources:
        title_clean = clean_for_matching(resource["title"])
        if not title_clean:
            continue

        for pdf in remaining_pdfs:
            stem_clean = clean_for_matching(pdf["stem"])
            if not stem_clean:
                continue

            # Skip generic filenames for fuzzy matching
            if is_generic_filename(pdf["stem"]):
                continue

            # Compute fuzzy score
            score = SequenceMatcher(None, title_clean, stem_clean).ratio()

            # Bonus: if one contains the other (strong signal)
            if title_clean in stem_clean or stem_clean in title_clean:
                score = max(score, 0.85)

            # Bonus: if key words overlap significantly
            title_words = set(title_clean.split())
            stem_words = set(stem_clean.split())
            if len(title_words) > 1 and len(stem_words) > 1:
                overlap = title_words & stem_words
                if len(overlap) >= 2:
                    word_score = len(overlap) / max(len(title_words), len(stem_words))
                    score = max(score, 0.5 + word_score * 0.4)

            if score >= FUZZY_THRESHOLD:
                candidates.append((score, resource, pdf))

    # Sort by score descending — greedily assign best matches
    candidates.sort(key=lambda x: x[0], reverse=True)

    for score, resource, pdf in candidates:
        if resource["page_id"] in matched_resource_ids:
            continue
        if pdf["path"] in matched_pdf_paths:
            continue

        matched.append({
            "page_id": resource["page_id"],
            "title": resource["title"],
            "type": resource["type"],
            "file_path": pdf["path"],
            "file_name": pdf["filename"],
            "file_size": pdf["size"],
            "match_type": "fuzzy",
            "match_score": round(score, 3),
        })
        matched_pdf_paths.add(pdf["path"])
        matched_resource_ids.add(resource["page_id"])

    # ── Collect unmatched ──
    for resource in resources_needing:
        if resource["page_id"] in matched_resource_ids:
            continue

        # Find best candidate for reporting
        title_clean = clean_for_matching(resource["title"])
        best_score = 0.0
        best_candidate = None
        for pdf in pdfs:
            stem_clean = clean_for_matching(pdf["stem"])
            if not stem_clean:
                continue
            s = SequenceMatcher(None, title_clean, stem_clean).ratio()
            if s > best_score:
                best_score = s
                best_candidate = pdf["filename"]

        unmatched_resources.append({
            "page_id": resource["page_id"],
            "title": resource["title"],
            "type": resource["type"],
            "best_candidate": best_candidate,
            "best_score": round(best_score, 3),
        })

    # Unmatched files
    unmatched_files = []
    for pdf in pdfs:
        if pdf["path"] not in matched_pdf_paths:
            unmatched_files.append({
                "path": pdf["path"],
                "filename": pdf["filename"],
                "size": pdf["size"],
            })

    return matched, unmatched_resources, unmatched_files


# ── Upload Logic ───────────────────────────────────────────────────────────

def create_multipart_form(fields, file_field_name, file_path, file_content_type, part_data=None):
    """
    Build a multipart/form-data body manually (no requests library).
    fields: dict of {name: value} for text fields
    file_field_name: name of the file field
    file_path: path to read from (ignored if part_data is provided)
    file_content_type: MIME type for the file
    part_data: if provided, use this bytes instead of reading from file_path
    Returns: (body_bytes, content_type_header)
    """
    boundary = f"----NotionUpload{int(time.time()*1000)}"
    lines = []

    # Add text fields
    for name, value in fields.items():
        lines.append(f"--{boundary}".encode())
        lines.append(f'Content-Disposition: form-data; name="{name}"'.encode())
        lines.append(b"")
        lines.append(str(value).encode())

    # Add file field
    filename = os.path.basename(file_path)
    lines.append(f"--{boundary}".encode())
    lines.append(
        f'Content-Disposition: form-data; name="{file_field_name}"; filename="{filename}"'.encode()
    )
    lines.append(f"Content-Type: {file_content_type}".encode())
    lines.append(b"")

    if part_data is not None:
        file_data = part_data
    else:
        with open(file_path, "rb") as f:
            file_data = f.read()

    # Build final body
    body = b"\r\n".join(lines) + b"\r\n" + file_data + f"\r\n--{boundary}--\r\n".encode()
    content_type = f"multipart/form-data; boundary={boundary}"
    return body, content_type


def upload_single_part(file_path, filename, file_size):
    """Upload a file <20MB using single-part flow."""
    # Step 1: Create file upload
    upload_resp = notion_request("POST", "https://api.notion.com/v1/file_uploads", {
        "mode": "single_part",
        "filename": filename,
        "content_type": "application/pdf",
    }, use_upload_version=True)
    upload_id = upload_resp["id"]
    time.sleep(RATE_LIMIT)

    # Step 2: Send the file
    body, content_type = create_multipart_form(
        fields={},
        file_field_name="file",
        file_path=file_path,
        file_content_type="application/pdf",
    )

    url = f"https://api.notion.com/v1/file_uploads/{upload_id}/send"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Notion-Version": NOTION_VERSION_UPLOAD,
        "Content-Type": content_type,
    }
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, context=SSL_CTX) as resp:
            result = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"    SEND ERROR ({e.code}): {error_body[:300]}", flush=True)
        raise

    time.sleep(RATE_LIMIT)
    return upload_id


def upload_multi_part(file_path, filename, file_size):
    """Upload a file 20-100MB using multi-part flow."""
    num_parts = math.ceil(file_size / PART_SIZE)

    # Step 1: Create multi-part file upload
    upload_resp = notion_request("POST", "https://api.notion.com/v1/file_uploads", {
        "mode": "multi_part",
        "filename": filename,
        "content_type": "application/pdf",
        "number_of_parts": num_parts,
    }, use_upload_version=True)
    upload_id = upload_resp["id"]
    time.sleep(RATE_LIMIT)

    # Step 2: Send each part
    with open(file_path, "rb") as f:
        for part_num in range(1, num_parts + 1):
            chunk = f.read(PART_SIZE)
            if not chunk:
                break

            body, content_type = create_multipart_form(
                fields={"part_number": part_num},
                file_field_name="file",
                file_path=file_path,
                file_content_type="application/pdf",
                part_data=chunk,
            )

            url = f"https://api.notion.com/v1/file_uploads/{upload_id}/send"
            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Notion-Version": NOTION_VERSION_UPLOAD,
                "Content-Type": content_type,
            }
            req = urllib.request.Request(url, data=body, headers=headers, method="POST")
            try:
                with urllib.request.urlopen(req, context=SSL_CTX) as resp:
                    json.loads(resp.read())
            except urllib.error.HTTPError as e:
                error_body = e.read().decode()
                print(f"    SEND PART {part_num} ERROR ({e.code}): {error_body[:300]}", flush=True)
                raise

            print(f"    Sent part {part_num}/{num_parts}", flush=True)
            time.sleep(RATE_LIMIT)

    # Step 3: Complete the upload
    url = f"https://api.notion.com/v1/file_uploads/{upload_id}/complete"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Notion-Version": NOTION_VERSION_UPLOAD,
        "Content-Type": "application/json",
    }
    req = urllib.request.Request(url, data=b"{}", headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, context=SSL_CTX) as resp:
            json.loads(resp.read())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"    COMPLETE ERROR ({e.code}): {error_body[:300]}", flush=True)
        raise

    time.sleep(RATE_LIMIT)
    return upload_id


def attach_file_to_page(page_id, upload_id, filename):
    """Attach an uploaded file to a Notion page's File property."""
    notion_request("PATCH", f"https://api.notion.com/v1/pages/{page_id}", {
        "properties": {
            "File": {
                "files": [{
                    "name": filename,
                    "type": "file_upload",
                    "file_upload": {"id": upload_id},
                }]
            }
        }
    }, use_upload_version=True)
    time.sleep(RATE_LIMIT)


def upload_file(entry):
    """
    Upload a single file and attach it to its Notion page.
    Returns True on success, False on failure.
    """
    file_path = entry["file_path"]
    file_name = entry["file_name"]
    file_size = entry["file_size"]
    page_id = entry["page_id"]

    if file_size > MAX_FILE_SIZE:
        print(f"    SKIPPED: File too large ({file_size / 1024 / 1024:.1f} MB > 100 MB)", flush=True)
        return False

    try:
        if file_size < MULTI_PART_THRESHOLD:
            upload_id = upload_single_part(file_path, file_name, file_size)
        else:
            upload_id = upload_multi_part(file_path, file_name, file_size)

        attach_file_to_page(page_id, upload_id, file_name)
        return True

    except Exception as e:
        print(f"    FAILED: {e}", flush=True)
        return False


# ── Phase 1: Build Mapping ────────────────────────────────────────────────

def build_mapping():
    """Phase 1: Fetch resources, scan PDFs, match, save mapping."""
    print("=" * 60, flush=True)
    print("PHASE 1: Building file mapping", flush=True)
    print("=" * 60, flush=True)

    # Fetch all resources from Notion
    print("\n1. Fetching all resources from Notion...", flush=True)
    resources = fetch_all_resources()
    print(f"   Found {len(resources)} resources in Notion", flush=True)

    already_have_file = sum(1 for r in resources if r["has_file"])
    need_file = sum(1 for r in resources if not r["has_file"])
    print(f"   {already_have_file} already have files, {need_file} need files", flush=True)

    # Scan for PDFs
    print("\n2. Scanning LaCie drive for PDFs...", flush=True)
    pdfs = scan_pdfs()
    print(f"   Found {len(pdfs)} PDF files on disk", flush=True)

    total_size = sum(p["size"] for p in pdfs)
    print(f"   Total size: {total_size / 1024 / 1024 / 1024:.2f} GB", flush=True)

    # Match resources to files
    print("\n3. Matching resources to files...", flush=True)
    matched, unmatched_resources, unmatched_files = match_resources_to_files(resources, pdfs)

    # Sort matched by file size (smallest first)
    matched.sort(key=lambda x: x["file_size"])

    # Print statistics
    print("\n" + "=" * 60, flush=True)
    print("MATCHING RESULTS", flush=True)
    print("=" * 60, flush=True)
    print(f"Total Notion resources:     {len(resources)}", flush=True)
    print(f"Already have files:         {already_have_file}", flush=True)
    print(f"Need files:                 {need_file}", flush=True)
    print(f"Matched to PDFs:            {len(matched)}", flush=True)

    exact = sum(1 for m in matched if m["match_type"] == "exact")
    fuzzy = sum(1 for m in matched if m["match_type"] == "fuzzy")
    print(f"  - Exact matches:          {exact}", flush=True)
    print(f"  - Fuzzy matches:          {fuzzy}", flush=True)

    print(f"Unmatched resources:        {len(unmatched_resources)}", flush=True)
    print(f"Unmatched files on disk:    {len(unmatched_files)}", flush=True)

    matched_size = sum(m["file_size"] for m in matched)
    print(f"Total upload size:          {matched_size / 1024 / 1024:.1f} MB", flush=True)

    over_limit = [m for m in matched if m["file_size"] > MAX_FILE_SIZE]
    if over_limit:
        print(f"Files over 100MB (skipped): {len(over_limit)}", flush=True)
        for m in over_limit:
            print(f"  - {m['title']} ({m['file_size'] / 1024 / 1024:.1f} MB)", flush=True)

    # Show sample matches
    print("\nSample matches:", flush=True)
    for m in matched[:15]:
        score_str = f"{m['match_score']:.2f}" if m["match_type"] == "fuzzy" else "1.00"
        size_str = f"{m['file_size'] / 1024:.0f}KB" if m["file_size"] < 1024*1024 else f"{m['file_size']/1024/1024:.1f}MB"
        print(f"  [{m['match_type']:5s} {score_str}] \"{m['title']}\" -> {m['file_name']} ({size_str})", flush=True)

    # Show near-misses (unmatched with best candidates)
    near_misses = [u for u in unmatched_resources if u.get("best_score", 0) >= 0.5]
    if near_misses:
        print(f"\nNear misses ({len(near_misses)} resources with score 0.5-0.7):", flush=True)
        for u in sorted(near_misses, key=lambda x: x["best_score"], reverse=True)[:15]:
            print(f"  [{u['best_score']:.2f}] \"{u['title']}\" ~ {u.get('best_candidate', 'N/A')}", flush=True)

    # Save mapping
    mapping = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "stats": {
            "total_resources": len(resources),
            "already_have_files": already_have_file,
            "need_files": need_file,
            "matched": len(matched),
            "exact_matches": exact,
            "fuzzy_matches": fuzzy,
            "unmatched_resources": len(unmatched_resources),
            "unmatched_files": len(unmatched_files),
            "total_upload_size_mb": round(matched_size / 1024 / 1024, 1),
        },
        "matched": matched,
        "unmatched_resources": unmatched_resources,
        "unmatched_files": unmatched_files[:200],  # Limit to first 200 for readability
    }

    with open(MAP_FILE, "w") as f:
        json.dump(mapping, f, indent=2)
    print(f"\nMapping saved to {MAP_FILE}", flush=True)

    return mapping


# ── Phase 2: Upload Files ─────────────────────────────────────────────────

def run_uploads(limit=50):
    """Phase 2: Upload matched files to Notion."""
    # Load mapping
    if not os.path.exists(MAP_FILE):
        print("ERROR: No mapping file found. Run with --map-only first.", flush=True)
        return

    with open(MAP_FILE) as f:
        mapping = json.load(f)

    matched = mapping["matched"]
    if not matched:
        print("No matched files to upload.", flush=True)
        return

    # Filter out already-uploaded entries (check for upload_id)
    to_upload = [m for m in matched if "upload_id" not in m]

    if limit != "all":
        limit = int(limit)
        to_upload = to_upload[:limit]

    print("=" * 60, flush=True)
    print(f"PHASE 2: Uploading {len(to_upload)} files to Notion", flush=True)
    print("=" * 60, flush=True)

    success = 0
    failed = 0
    skipped = 0

    for i, entry in enumerate(to_upload, 1):
        size_mb = entry["file_size"] / 1024 / 1024
        print(f"\n[{i}/{len(to_upload)}] Uploading: {entry['title']} ({size_mb:.1f} MB) -> {entry['page_id']}", flush=True)

        if entry["file_size"] > MAX_FILE_SIZE:
            print(f"  SKIPPED: Over 100MB limit", flush=True)
            skipped += 1
            continue

        # Verify file still exists on disk
        if not os.path.exists(entry["file_path"]):
            print(f"  SKIPPED: File not found on disk", flush=True)
            skipped += 1
            continue

        ok = upload_file(entry)
        if ok:
            success += 1
            # Mark as uploaded in mapping
            entry["uploaded"] = True
            entry["uploaded_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
            print(f"  OK", flush=True)
        else:
            failed += 1
            entry["upload_error"] = True

        # Save progress after each upload
        with open(MAP_FILE, "w") as f:
            json.dump(mapping, f, indent=2)

    print("\n" + "=" * 60, flush=True)
    print(f"UPLOAD RESULTS: {success} uploaded, {failed} failed, {skipped} skipped", flush=True)
    print("=" * 60, flush=True)


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]

    if "--map-only" in args:
        build_mapping()
    elif "--upload" in args:
        idx = args.index("--upload")
        limit = args[idx + 1] if idx + 1 < len(args) else "50"
        run_uploads(limit)
    else:
        # Default: build mapping, then upload first 50
        mapping = build_mapping()
        if mapping["matched"]:
            print("\n\n", flush=True)
            run_uploads(50)
        else:
            print("\nNo matches found. Nothing to upload.", flush=True)


if __name__ == "__main__":
    main()
