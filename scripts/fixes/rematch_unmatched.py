#!/usr/bin/env python3
"""
Improved matcher for the 86 unmatched Resources in the ID Codex.

Strategy (vs. previous strict fuzzy filename matcher):
  - Token overlap (Jaccard) on alphanumeric tokens after stopword removal
  - Substring match on distinctive words (>4 chars)
  - Course affinity: boost files whose folder path mentions the linked course
  - Author match: boost files where "(Author)" or "- Author" appears in filename
  - Weighted score; >=0.55 = upload, 0.40-0.54 = ambiguous (save for review)

Does NOT repeat previous weak matches. Produces:
  - /Users/idstuart/Projects/idcodex/data/rematch_results.json (detailed)
  - /Users/idstuart/Projects/idcodex/data/ambiguous_matches.json (needs review)

Usage:
  python3 rematch_unmatched.py                 # match + upload high-confidence
  python3 rematch_unmatched.py --match-only    # match only, no uploads
  python3 rematch_unmatched.py --dry-run       # match + print, no uploads
"""

import json
import math
import os
import re
import ssl
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

# ── Configuration ──────────────────────────────────────────────────────────

API_KEY = os.environ.get("NOTION_API_KEY")
RESOURCES_DB = "dd4ea6d9-92b4-4f28-b75c-ecb7f6b851be"
NOTION_VERSION = "2022-06-28"
NOTION_VERSION_UPLOAD = "2026-03-11"

RATE_LIMIT = 0.35
# Notion single-part limit ~100MB; multi-part supports up to ~5GB.
# We enforce per-upload caps separately:
MAX_FILE_SIZE_SINGLE = 100 * 1024 * 1024   # 100 MB single-part
MAX_FILE_SIZE_MULTI = 5 * 1024 * 1024 * 1024  # 5 GB multi-part
MULTI_PART_THRESHOLD = 20 * 1024 * 1024
PART_SIZE = 20 * 1024 * 1024
# Overall cap: files over this are skipped entirely (to avoid huge uploads taking forever).
MAX_FILE_SIZE = MAX_FILE_SIZE_MULTI

# Thresholds
UPLOAD_THRESHOLD = 0.55
AMBIGUOUS_THRESHOLD = 0.40

# SSL (macOS workaround)
SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

# Scan roots & exclusions
SCAN_DIRS = [
    "/Volumes/LaCie/Anurag@ID/Foundation Semester",
    "/Volumes/LaCie/Anurag@ID/Semester 1",
    "/Volumes/LaCie/Anurag@ID/Semester 2",
    "/Volumes/LaCie/Anurag@ID/Semester 3",
    "/Volumes/LaCie/Anurag@ID/Semester 4",
    "/Volumes/LaCie/Anurag@ID/Summer'25",
    "/Volumes/LaCie/Anurag@ID/ID GDrive Backup",
    "/Volumes/LaCie/ID Complete Course Material",
]

# Explicit non-ID folder paths to exclude (match as path substring)
EXCLUDE_PATH_SUBSTRS = [
    "/Semester 1/Optimization in Policy and Administration(PA-568-01)",
    "/Semester 1/Strategic Management",
    "/Semester 2/Policy forecasting and evaluation",
    "/Semester 3/Human Resource Management",
    "/Semester 3/Organizational Behavior",
    "/Summer'25/ProjectManagement",
]

# Useless / student-work folder names
EXCLUDE_DIR_NAMES = {
    "Working Documents", "Evaluation Sheets", "Class Photos",
    "Project Photos", "Presentation Assets", "Morph 3D Models",
    "IDSA", "Takeout", "Milan_Immersion",
}

# Skip macOS resource-fork (._file) artefacts; skip obvious student-author files
EXCLUDE_FILENAME_SUBSTRINGS = ["samanthac", "samantha_"]

# Extensions
ALLOWED_EXTS = {".pdf", ".pptx", ".docx", ".doc", ".ppt", ".key", ".mp4", ".mov", ".png", ".jpg", ".jpeg"}

MAP_FILE = "/Users/idstuart/Projects/idcodex/data/file_upload_map.json"
RESULTS_FILE = "/Users/idstuart/Projects/idcodex/data/rematch_results.json"
AMBIGUOUS_FILE = "/Users/idstuart/Projects/idcodex/data/ambiguous_matches.json"
# Persistent list of file paths we've uploaded in *any* prior rematch session.
# Prevents re-proposing the same file to another resource on a second pass.
UPLOADED_PATHS_FILE = "/Users/idstuart/Projects/idcodex/data/rematch_uploaded_paths.json"

# Stopwords and junk tokens
STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "for", "of", "to", "in", "on", "at", "by", "with", "from",
    "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
    "this", "that", "these", "those", "it", "its", "as", "into", "about",
    # noise / common-in-filename
    "week", "wk", "w", "class", "lecture", "session", "chapter", "ch", "intro", "introduction",
    "final", "draft", "v1", "v2", "v3", "f2024", "f2023", "s2024", "s2023",
    "slides", "slide", "deck", "presentation", "pres", "reading", "readings",
    "notes", "handout", "assignment", "brief", "instructions", "copy", "pdf",
    "part", "no", "vol", "ver", "version",
}

# Words that shouldn't count as "distinctive" even if >4 chars
GENERIC_DISTINCTIVE_BLACKLIST = {
    "design", "research", "course",
    "class", "lecture", "chapter", "introduction", "template", "worksheet",
    # Note: "readme" kept OUT of blacklist so "Weekly README" matches "READ ME".
    # "week"/"weekly" still filtered via week_hit/week_mismatch logic.
}

# Whitelist of course -> keywords that may appear in path/filename
COURSE_KEYWORD_MAP = {
    "Design for Climate Leadership": ["climate", "cl-01", "cl-02", "cl-", "sustainability"],
    "Behavioral Design": ["behavioral", "behavior", "bd-"],
    "Design Planning": ["planning", "dp-", "shaping"],
    "Design Methods": ["methods", "dm-", "method"],
    "Design Research Methods": ["research", "drm", "interviews", "observation", "ethnograph"],
    "Observing Users": ["observing", "users", "goodman"],
    "Shaping Strategic Change": ["strategic", "change", "shaping"],
    "Design Analytics": ["analytics", "data", "mast"],
    "Computational Research": ["computational", "spider", "mast", "sensors"],
    "Power & Politics in Design": ["politics", "power", "rittel", "winner", "feminist"],
    "Systems Design": ["systems", "geels", "multi-level", "mlp"],
    "Design for Digital Technology": ["digital", "hci", "interaction"],
    "Intro to Design Practice": ["idp", "intro", "practice"],
    "Design Elements": ["elements", "principles"],
    "Objects": ["objects", "artemide", "hertzian"],
    "Communication Design": ["communication", "visual", "graphic"],
    "Product Strategy": ["product", "strategy"],
    "Foundation Studio": ["foundation", "studio"],
    "History and Theory of Design": ["history", "theory"],
    "Mapping": ["mapping", "map", "lynch"],
    "Design for Social Change": ["social", "change"],
    "Innovation Frontiers": ["innovation", "frontiers"],
    "Adaptive Leadership": ["adaptive", "leadership"],
}


# ── Notion API ─────────────────────────────────────────────────────────────

def api_call(method, url, body=None, content_type="application/json",
             notion_version=NOTION_VERSION, raw_body=False):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Notion-Version": notion_version,
    }
    if content_type:
        headers["Content-Type"] = content_type
    data = None
    if body is not None:
        if raw_body:
            data = body
        elif content_type == "application/json":
            data = json.dumps(body).encode()
        else:
            data = body
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, context=SSL_CTX) as resp:
            raw = resp.read()
            if not raw:
                return {}
            return json.loads(raw)
    except urllib.error.HTTPError as e:
        body_err = e.read().decode()
        print(f"  API ERROR ({e.code}): {body_err[:300]}", flush=True)
        raise


def fetch_unmatched_resources():
    """Fetch all resources where File is empty; include course relation ids."""
    results = []
    cursor = None
    while True:
        body = {"page_size": 100, "filter": {"property": "File", "files": {"is_empty": True}}}
        if cursor:
            body["start_cursor"] = cursor
        d = api_call("POST",
                     f"https://api.notion.com/v1/databases/{RESOURCES_DB}/query",
                     body)
        for page in d["results"]:
            props = page["properties"]
            title_arr = props["Title"]["title"]
            title = title_arr[0]["plain_text"] if title_arr else ""
            type_prop = props.get("Type", {}).get("select") or {}
            resource_type = type_prop.get("name", "")
            authors_arr = props.get("Author(s)", {}).get("rich_text", []) or []
            authors_text = "".join(a.get("plain_text", "") for a in authors_arr)
            course_ids = [c["id"] for c in props.get("Courses", {}).get("relation", [])]
            results.append({
                "page_id": page["id"],
                "title": title,
                "type": resource_type,
                "authors": authors_text,
                "course_ids": course_ids,
                "course_names": [],  # filled in later
            })
        if not d.get("has_more"):
            break
        cursor = d["next_cursor"]
        time.sleep(RATE_LIMIT)
    return results


def fetch_course_names(course_ids):
    """Resolve course page ids to titles."""
    out = {}
    for cid in course_ids:
        try:
            p = api_call("GET", f"https://api.notion.com/v1/pages/{cid}")
            title_prop = p["properties"].get("Title") or p["properties"].get("Name") or {}
            arr = title_prop.get("title") or []
            out[cid] = arr[0]["plain_text"] if arr else ""
        except Exception as e:
            out[cid] = ""
        time.sleep(RATE_LIMIT)
    return out


# ── File scanning ──────────────────────────────────────────────────────────

def _is_excluded_path(path):
    for sub in EXCLUDE_PATH_SUBSTRS:
        if sub in path:
            return True
    parts = Path(path).parts
    for part in parts:
        if part in EXCLUDE_DIR_NAMES:
            return True
    return False


def _is_excluded_file(filename):
    if filename.startswith("._"):
        return True
    low = filename.lower()
    for sub in EXCLUDE_FILENAME_SUBSTRINGS:
        if sub in low:
            return True
    return False


def scan_files(excluded_paths):
    """
    Walk SCAN_DIRS; return list of dicts with {path, filename, stem, ext, size}.
    Skip already-matched paths (excluded_paths set).
    """
    files = []
    seen = set()
    for root_dir in SCAN_DIRS:
        if not os.path.isdir(root_dir):
            print(f"  WARN missing dir: {root_dir}", flush=True)
            continue
        for root, dirs, fnames in os.walk(root_dir):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIR_NAMES]
            if _is_excluded_path(root):
                continue
            for fn in fnames:
                if _is_excluded_file(fn):
                    continue
                ext = os.path.splitext(fn)[1].lower()
                if ext not in ALLOWED_EXTS:
                    continue
                full = os.path.join(root, fn)
                if full in excluded_paths:
                    continue
                try:
                    real = os.path.realpath(full)
                except Exception:
                    real = full
                if real in seen:
                    continue
                seen.add(real)
                try:
                    sz = os.path.getsize(full)
                except OSError:
                    continue
                files.append({
                    "path": full,
                    "filename": fn,
                    "stem": Path(fn).stem,
                    "ext": ext,
                    "size": sz,
                })
    return files


# ── Matching ───────────────────────────────────────────────────────────────

def _tokenize(text):
    text = text.lower()
    # Normalise "read me" -> "readme"
    text = re.sub(r"\bread[\s_]+me\b", "readme", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    tokens = [t for t in text.split() if len(t) > 1 and t not in STOPWORDS]
    # Strip trailing/leading digits-only tokens? keep numbers (useful for ch 6 etc.)
    return tokens


def _distinctive_tokens(tokens):
    """Tokens >= 5 chars not in generic blacklist."""
    return [t for t in tokens if len(t) >= 5 and t not in GENERIC_DISTINCTIVE_BLACKLIST]


def _author_names(author_text):
    """Rough split of authors into lastname tokens."""
    if not author_text:
        return []
    parts = re.split(r"[,&/;]|\band\b", author_text, flags=re.IGNORECASE)
    out = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        # If form "Last, First" or "First Last", take capitalised words as surnames
        words = re.findall(r"[A-Za-z][A-Za-z\-']+", p)
        if words:
            # take the longest word (usually surname) & tokens >= 4 chars
            longest = max(words, key=len)
            if len(longest) >= 4:
                out.append(longest.lower())
    return out


_COMMON_WORDS_NOT_AUTHORS = {
    "online", "shopping", "sample", "framework", "tool", "template", "draft",
    "paper", "article", "book", "slide", "deck", "reading", "worksheet",
    "doblin", "copy", "final", "notes", "brief", "handout", "summary",
    "the", "and", "with", "from", "about",
    # Context words: e.g. "(Framework)" in "Value Disciplines (Framework)"
    "behavioral", "design", "scenario", "questionnaire", "video",
    # "(Fall 2025)" etc.
    "fall", "spring", "summer", "winter",
}


def _parenthetical_author(title):
    """Extract names from trailing '(Author)' or '(Bardzell)' patterns.
    Only captures patterns that look like surnames (single capitalized word,
    not in common-words list, not all caps like acronyms)."""
    out = []
    # (Name) — single capitalised word not in common-words list
    for chunk in re.findall(r"\(([A-Za-z][A-Za-z\- ]*?)\)", title):
        words = [w for w in re.findall(r"[A-Za-z]+", chunk) if len(w) >= 4]
        # Only keep if: exactly one word, capitalised in original, not common
        if len(words) == 1:
            w = words[0]
            if w.lower() not in _COMMON_WORDS_NOT_AUTHORS and not w.isupper():
                # check the original chunk starts with capital
                out.append(w.lower())
        elif len(words) == 2:
            # "(Geels 2006)" — first word is the author
            w = words[0]
            if w.lower() not in _COMMON_WORDS_NOT_AUTHORS and not w.isupper():
                out.append(w.lower())
    # em-dash author: 'Some Title — Dunne' (last word on line)
    m2 = re.findall(r"[—\-–]\s*([A-Z][a-z]+)\s*$", title)
    for w in m2:
        if len(w) >= 4 and w.lower() not in _COMMON_WORDS_NOT_AUTHORS:
            out.append(w.lower())
    return out


def _acronyms(title):
    """Extract ALL-CAPS acronyms (2-5 chars) from the title.
    Includes combined codes like 'BD-01' so BD-01 != BD-02 in matching."""
    out = []
    # Course-code style: XX-NN (e.g., BD-01, CL-02, DP-03)
    for m in re.findall(r"\b([A-Z]{2,5})[-_](\d{1,3})\b", title):
        out.append(f"{m[0].lower()}-{m[1]}")
    # Plain acronyms
    for m in re.findall(r"\b([A-Z]{2,5})\b", title):
        out.append(m.lower())
    return out


def score_match(resource, file_entry):
    """
    Compute a composite match score in [0, 1+] for a resource-file pair.
    Returns (score, breakdown_dict).
    """
    title = resource["title"]
    title_tokens = _tokenize(title)
    title_tokens_set = set(title_tokens)
    title_distinct = set(_distinctive_tokens(title_tokens))
    # Acronyms from title (e.g. "ASQ", "MAST", "WSJ")
    title_acronyms = set(_acronyms(title))

    stem = file_entry["stem"]
    stem_tokens = _tokenize(stem)
    stem_tokens_set = set(stem_tokens)
    stem_distinct = set(_distinctive_tokens(stem_tokens))

    # Skip degenerate cases
    if not title_tokens or not stem_tokens:
        return 0.0, {}

    # 1. Jaccard on tokens
    inter = title_tokens_set & stem_tokens_set
    union = title_tokens_set | stem_tokens_set
    jaccard = (len(inter) / len(union)) if union else 0.0

    # 2. Distinctive overlap: count how many distinctive (>=5 char) title tokens are in stem
    d_overlap_count = len(title_distinct & stem_distinct)
    d_overlap_ratio = d_overlap_count / max(1, len(title_distinct)) if title_distinct else 0.0

    # Substring check — any distinctive token is substring in stem (lowercased)
    # Also accept matches in the immediate parent folder name (catches files in
    # e.g. "Week 1 Typography/1 Intro Type.pdf" — file name omits "Typography"
    # but parent folder includes it).
    stem_lower = stem.lower()
    parent_folder = os.path.basename(os.path.dirname(file_entry.get("path", ""))).lower()
    combined = stem_lower + " " + parent_folder
    substring_hits = sum(1 for w in title_distinct if w in combined)
    substring_ratio = substring_hits / max(1, len(title_distinct)) if title_distinct else 0.0

    # Distinctive hits counting either overlap or substring (take max per-token)
    # Use best-of: max(d_overlap_ratio, substring_ratio)
    distinctive_hits = max(d_overlap_count, substring_hits)
    distinctive_ratio = max(d_overlap_ratio, substring_ratio)

    # 3. Course affinity: does any course-keyword appear in the folder path?
    path_lower = file_entry["path"].lower()
    course_hit = 0
    course_keywords_hit = []
    for cname in resource.get("course_names", []):
        # direct course name words in path
        cwords = [w.lower() for w in re.findall(r"[A-Za-z]{4,}", cname)]
        for w in cwords:
            if w in path_lower:
                course_hit = 1
                course_keywords_hit.append(w)
                break
        if course_hit:
            continue
        # explicit keyword map
        for key, kws in COURSE_KEYWORD_MAP.items():
            if key.lower() == cname.lower():
                for kw in kws:
                    if kw.lower() in path_lower:
                        course_hit = 1
                        course_keywords_hit.append(kw)
                        break
                if course_hit:
                    break

    # 4. Author match
    author_tokens = set(_author_names(resource.get("authors", "")))
    author_tokens |= set(_parenthetical_author(title))
    author_hit = 0
    matched_author_tokens = set()
    if author_tokens:
        for a in author_tokens:
            if a in stem.lower():
                author_hit = 1
                matched_author_tokens.add(a)

    # Count non-author distinctive hits: these are the "subject" matches
    non_author_distinct_hits = 0
    for t in title_distinct:
        # Is t matched by the stem (either word-overlap or substring), or in parent folder name?
        if (t in stem_tokens_set or t in combined):
            # Only count if not solely an author match
            if t not in matched_author_tokens:
                non_author_distinct_hits += 1

    # 5. Chapter/number match bonus & penalty
    # e.g. title "Ch 9" / "Ch. 9" / "Chapter 9" should align with chapter numbers in stem.
    chapter_hit = 0
    chapter_mismatch = 0
    title_ch = None
    # Match Ch N, Ch. N, Chapter N
    m_title = re.search(r"\b(?:ch|chapter|ch\.)\s*(\d{1,2})\b", title.lower())
    if m_title:
        title_ch = int(m_title.group(1))
    # Look for chapter numbers in stem — try several forms
    stem_chs = []
    for m in re.finditer(r"(?:chapter|ch\.?)\s*0*(\d{1,2})", stem.lower()):
        stem_chs.append(int(m.group(1)))
    # CHAPTER10ActPolitical style — digits immediately after word
    for m in re.finditer(r"chapter0*(\d{1,2})", stem.lower()):
        stem_chs.append(int(m.group(1)))
    # ch10, ch_10, ch-10 style
    for m in re.finditer(r"(?<![a-z])ch0*(\d{1,2})(?![a-z0-9])", stem.lower()):
        stem_chs.append(int(m.group(1)))
    # "Ch 1, 2, 6" style lists — after finding the first Ch N, capture subsequent
    # digit tokens separated by commas/ands
    m_ch_list = re.search(r"ch(?:apter)?\.?\s*0*(\d{1,2})((?:\s*[,&]\s*0*\d{1,2})+)", stem.lower())
    if m_ch_list:
        tail = m_ch_list.group(2)
        for m in re.finditer(r"(\d{1,2})", tail):
            stem_chs.append(int(m.group(1)))
    stem_chs = list(set(stem_chs))
    if title_ch is not None:
        if title_ch in stem_chs:
            chapter_hit = 1
        elif stem_chs:
            # stem clearly mentions a chapter, and it's a DIFFERENT one
            chapter_mismatch = 1

    # 5b. Week number match: "Week 4", "W4", "Wk 4" in title should align with
    # Week 4 / W4 / Wk 4 in filename.
    week_hit = 0
    week_mismatch = 0
    title_wk = None
    m_wk = re.search(r"\b(?:week|wk|w)\s*(\d{1,2})\b", title.lower())
    if m_wk:
        title_wk = int(m_wk.group(1))
    stem_wks = []
    for pat in (
        r"(?:week|wk)\s*0*(\d{1,2})",        # "Week 4", "Week4", "Wk 4"
        r"week0*(\d{1,2})",                   # "Week4" concatenated
        r"(?<![a-z])w0*(\d{1,2})(?![a-z0-9])",  # "W4" but not "w2024"
    ):
        for m in re.finditer(pat, stem.lower()):
            stem_wks.append(int(m.group(1)))
    stem_wks = list(set(stem_wks))
    if title_wk is not None and stem_wks:
        if title_wk in stem_wks:
            week_hit = 1
        else:
            week_mismatch = 1

    # 5c. "Intro to X" bonus: if title has "intro" before a word and filename
    # also has "intro_to" or "introduction to" (case-insensitive), strong hit.
    intro_hit = 0
    if re.search(r"\bintro(?:duction)?\s+to\b", title.lower()) and \
       re.search(r"intro[_\s]*to|introduction[_\s]*to", stem.lower()):
        intro_hit = 1

    # 5d. Acronym hit: ALL-CAPS token in title (2-5 chars) appears in stem.
    # For combined codes like 'bd-01' we require the full code in the stem.
    acronym_hit = 0
    acronym_mismatch = 0
    # Prefer combined codes (e.g., bd-01) — if title has one, require full match.
    combined_codes = [a for a in title_acronyms if "-" in a]
    simple_acronyms = [a for a in title_acronyms if "-" not in a]
    stem_l = stem.lower()
    if combined_codes:
        # If a stem has "bd-" but different number, that's a mismatch (not just no hit).
        for code in combined_codes:
            pat = rf"(?<![a-z0-9]){re.escape(code)}(?![a-z0-9])"
            if re.search(pat, stem_l):
                acronym_hit = 1
                break
        if not acronym_hit:
            # Is there an alternate code in stem that shares the prefix?
            prefix = combined_codes[0].split("-")[0]
            if re.search(rf"(?<![a-z0-9]){re.escape(prefix)}-\d+", stem_l):
                acronym_mismatch = 1
    if not acronym_hit and not acronym_mismatch:
        for acr in simple_acronyms:
            if re.search(rf"(?<![a-z0-9]){re.escape(acr)}(?![a-z0-9])", stem_l):
                acronym_hit = 1
                break

    # 6. Weighted composite
    # Two scoring modes, take max:
    #  (a) ratio-based: good for long titles with many overlaps
    #  (b) hits-based: good for short titles where one distinctive hit is a strong signal
    ratio_score = 0.45 * distinctive_ratio + 0.20 * jaccard
    # hits-based: 1 hit -> 0.35, 2 -> 0.55, 3 -> 0.65, cap 0.70
    hit_score_map = {0: 0.0, 1: 0.35, 2: 0.55, 3: 0.65}
    hit_score = hit_score_map.get(distinctive_hits, 0.70)
    # Also reward jaccard regardless
    hit_score += 0.15 * jaccard
    # Acronym-only matches deserve a decent base too
    acronym_base = 0.25 if acronym_hit else 0.0
    # Strong author match on very short titles: treat like a solid hit
    author_only_base = 0.0
    if author_hit and len(title_distinct) <= 2 and distinctive_hits == 0:
        author_only_base = 0.25
    base = max(ratio_score, hit_score, acronym_base, author_only_base)
    # Bonuses (additive, capped)
    bonuses = 0.0
    if course_hit:
        bonuses += 0.08
    # Author bonus only counts if there is also a non-author subject overlap,
    # OR the title is very short (<=2 distinct tokens) so that author+course is strong.
    # Otherwise author match alone is too weak (different papers by same author).
    if author_hit and (non_author_distinct_hits >= 1 or len(title_distinct) <= 2):
        bonuses += 0.15
    elif author_hit:
        # Weak author-only — small bonus
        bonuses += 0.03
    if chapter_hit:
        bonuses += 0.15
    if week_hit:
        bonuses += 0.12
    if intro_hit:
        bonuses += 0.10
    if acronym_hit:
        # Acronyms are a very strong signal (e.g. "ASQ", "MAST", "WSJ", "HCI").
        # If this is the only signal, we still want to push into high-confidence.
        bonuses += 0.35
    # Strong signal: if non-author distinctive hits >= 2 AND file path matches course
    if non_author_distinct_hits >= 2 and course_hit:
        bonuses += 0.05

    # Chapter mismatch is fatal — the title wants a specific chapter and
    # the file is a different chapter.
    if chapter_mismatch:
        return 0.0, {"reason": f"chapter mismatch (title={title_ch}, file={stem_chs})"}
    # Week mismatch is a strong negative but not fatal (some weeks map to multiple files)
    if week_mismatch:
        # penalize heavily
        return 0.0, {"reason": f"week mismatch (title={title_wk}, file={stem_wks})"}
    # Combined-code mismatch (e.g., title 'BD-02' but stem 'BD-01') — fatal
    if acronym_mismatch:
        return 0.0, {"reason": f"code mismatch (title codes={combined_codes})"}

    # Penalty: if zero distinctive overlap, cap very low
    if distinctive_hits == 0 and not author_hit and not acronym_hit:
        if jaccard < 0.4:
            return 0.0, {"reason": "no distinctive overlap"}

    score = min(1.0, base + bonuses)

    # Hard requirements: at least 1 distinctive hit OR acronym hit OR strong author match
    if distinctive_hits == 0 and author_hit == 0 and acronym_hit == 0:
        return 0.0, {"reason": "no distinctive / acronym / author match"}

    breakdown = {
        "jaccard": round(jaccard, 3),
        "distinctive_hits": distinctive_hits,
        "non_author_distinctive_hits": non_author_distinct_hits,
        "distinctive_ratio": round(distinctive_ratio, 3),
        "substring_hits": substring_hits,
        "course_hit": course_hit,
        "course_keywords": course_keywords_hit,
        "author_hit": author_hit,
        "chapter_hit": chapter_hit,
        "week_hit": week_hit,
        "intro_hit": intro_hit,
        "acronym_hit": acronym_hit,
    }
    return round(score, 3), breakdown


# ── Uploads (mirror of upload_files.py) ────────────────────────────────────

def _content_type(ext):
    return {
        ".pdf": "application/pdf",
        ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        ".ppt": "application/vnd.ms-powerpoint",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".doc": "application/msword",
        ".key": "application/x-iwork-keynote-sffkey",
        ".mp4": "video/mp4",
        ".mov": "video/quicktime",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
    }.get(ext.lower(), "application/octet-stream")


def _multipart_body(fields, file_field_name, file_path, content_type, part_data=None):
    boundary = f"----NotionUpload{int(time.time()*1000)}"
    lines = []
    for name, value in fields.items():
        lines.append(f"--{boundary}".encode())
        lines.append(f'Content-Disposition: form-data; name="{name}"'.encode())
        lines.append(b"")
        lines.append(str(value).encode())
    filename = os.path.basename(file_path)
    lines.append(f"--{boundary}".encode())
    lines.append(
        f'Content-Disposition: form-data; name="{file_field_name}"; filename="{filename}"'.encode()
    )
    lines.append(f"Content-Type: {content_type}".encode())
    lines.append(b"")
    if part_data is not None:
        data = part_data
    else:
        with open(file_path, "rb") as f:
            data = f.read()
    body = b"\r\n".join(lines) + b"\r\n" + data + f"\r\n--{boundary}--\r\n".encode()
    return body, f"multipart/form-data; boundary={boundary}"


def upload_file_single(file_path, filename, size, mime):
    r = api_call("POST", "https://api.notion.com/v1/file_uploads",
                 {"mode": "single_part", "filename": filename, "content_type": mime},
                 notion_version=NOTION_VERSION_UPLOAD)
    upload_id = r["id"]
    time.sleep(RATE_LIMIT)
    body, ct = _multipart_body({}, "file", file_path, mime)
    api_call("POST",
             f"https://api.notion.com/v1/file_uploads/{upload_id}/send",
             body=body, content_type=ct, notion_version=NOTION_VERSION_UPLOAD, raw_body=True)
    time.sleep(RATE_LIMIT)
    return upload_id


def upload_file_multi(file_path, filename, size, mime):
    num_parts = math.ceil(size / PART_SIZE)
    r = api_call("POST", "https://api.notion.com/v1/file_uploads",
                 {"mode": "multi_part", "filename": filename, "content_type": mime,
                  "number_of_parts": num_parts},
                 notion_version=NOTION_VERSION_UPLOAD)
    upload_id = r["id"]
    time.sleep(RATE_LIMIT)
    with open(file_path, "rb") as f:
        for i in range(1, num_parts + 1):
            chunk = f.read(PART_SIZE)
            if not chunk:
                break
            body, ct = _multipart_body({"part_number": i}, "file", file_path, mime, part_data=chunk)
            api_call("POST",
                     f"https://api.notion.com/v1/file_uploads/{upload_id}/send",
                     body=body, content_type=ct, notion_version=NOTION_VERSION_UPLOAD, raw_body=True)
            time.sleep(RATE_LIMIT)
    api_call("POST", f"https://api.notion.com/v1/file_uploads/{upload_id}/complete",
             body={}, notion_version=NOTION_VERSION_UPLOAD)
    time.sleep(RATE_LIMIT)
    return upload_id


def attach_file(page_id, upload_id, filename):
    # Notion enforces name length <= 100
    display_name = filename
    if len(display_name) > 100:
        stem, ext = os.path.splitext(display_name)
        keep = 100 - len(ext) - 3  # room for ext + "..."
        display_name = stem[:keep] + "..." + ext
    api_call("PATCH", f"https://api.notion.com/v1/pages/{page_id}",
             body={
                 "properties": {
                     "File": {
                         "files": [{
                             "name": display_name,
                             "type": "file_upload",
                             "file_upload": {"id": upload_id},
                         }]
                     }
                 }
             }, notion_version=NOTION_VERSION_UPLOAD)
    time.sleep(RATE_LIMIT)


def upload_and_attach(match):
    path = match["file_path"]
    name = match["file_name"]
    size = match["file_size"]
    ext = os.path.splitext(name)[1].lower()
    mime = _content_type(ext)
    if size > MAX_FILE_SIZE:
        return False, f"too_large ({size/1024/1024:.0f}MB > {MAX_FILE_SIZE/1024/1024:.0f}MB)"
    if not os.path.exists(path):
        return False, "missing"
    try:
        if size < MULTI_PART_THRESHOLD:
            upload_id = upload_file_single(path, name, size, mime)
        else:
            upload_id = upload_file_multi(path, name, size, mime)
        attach_file(match["page_id"], upload_id, name)
        return True, "ok"
    except Exception as e:
        return False, str(e)[:200]


# ── Main matching loop ─────────────────────────────────────────────────────

def main(args):
    match_only = "--match-only" in args
    dry_run = "--dry-run" in args

    # Load existing map to get already-matched AND uploaded paths.
    # We only exclude paths that were actually uploaded (not merely matched) —
    # an over-100MB file might be "matched" but never uploaded, and needs
    # to be available in the pool so we can list it as a candidate for review.
    with open(MAP_FILE) as f:
        existing_map = json.load(f)
    used_paths = {
        m["file_path"] for m in existing_map.get("matched", [])
        if m.get("uploaded")  # only exclude if actually uploaded
    }
    # Also include paths uploaded by any previous rematch session.
    if os.path.exists(UPLOADED_PATHS_FILE):
        try:
            with open(UPLOADED_PATHS_FILE) as f:
                rematch_prior = json.load(f)
            used_paths.update(rematch_prior.get("paths", []))
        except Exception:
            pass
    print(f"Previously-uploaded file paths to exclude: {len(used_paths)}", flush=True)

    # Fetch unmatched resources
    print("Fetching unmatched resources from Notion...", flush=True)
    resources = fetch_unmatched_resources()
    print(f"  {len(resources)} resources with no file", flush=True)

    # Gather course ids to resolve names
    all_course_ids = set()
    for r in resources:
        all_course_ids.update(r["course_ids"])
    print(f"Resolving {len(all_course_ids)} course names...", flush=True)
    course_name_map = fetch_course_names(sorted(all_course_ids))
    for r in resources:
        r["course_names"] = [course_name_map.get(cid, "") for cid in r["course_ids"] if course_name_map.get(cid)]

    # Scan files
    print("Scanning candidate files...", flush=True)
    files = scan_files(used_paths)
    print(f"  {len(files)} candidate files in the pool", flush=True)

    # Score all resource-file pairs; per resource keep top 5
    print("Scoring...", flush=True)
    per_resource_top = []
    for r in resources:
        scored = []
        for fe in files:
            s, bd = score_match(r, fe)
            if s > 0:
                scored.append((s, fe, bd))
        scored.sort(key=lambda x: x[0], reverse=True)
        top5 = [{
            "file_path": f["path"],
            "file_name": f["filename"],
            "file_size": f["size"],
            "score": s,
            "breakdown": bd,
        } for (s, f, bd) in scored[:5]]
        per_resource_top.append({
            "page_id": r["page_id"],
            "title": r["title"],
            "type": r["type"],
            "authors": r["authors"],
            "course_names": r["course_names"],
            "top_candidates": top5,
        })

    # Assign 1-to-1: sort all (resource, candidate) pairs by score desc,
    # greedily take the best non-conflicting ones for BOTH upload and ambiguous lists.
    assignments = []  # list of (score, resource_idx, candidate_dict)
    for ri, rec in enumerate(per_resource_top):
        for c in rec["top_candidates"]:
            assignments.append((c["score"], ri, c))
    assignments.sort(key=lambda x: x[0], reverse=True)

    chosen_resource = {}   # ri -> assigned candidate
    chosen_paths = set()
    ambiguous = {}         # ri -> ambiguous candidate (if none above threshold)
    for score, ri, cand in assignments:
        if ri in chosen_resource:
            continue
        if cand["file_path"] in chosen_paths:
            continue
        if score >= UPLOAD_THRESHOLD:
            chosen_resource[ri] = cand
            chosen_paths.add(cand["file_path"])
        elif score >= AMBIGUOUS_THRESHOLD and ri not in ambiguous:
            ambiguous[ri] = cand

    # Collect results
    matches_to_upload = []
    amb_list = []
    unresolved = []
    for ri, rec in enumerate(per_resource_top):
        base = {
            "page_id": rec["page_id"],
            "title": rec["title"],
            "type": rec["type"],
            "course_names": rec["course_names"],
        }
        if ri in chosen_resource:
            c = chosen_resource[ri]
            matches_to_upload.append({
                **base,
                "file_path": c["file_path"],
                "file_name": c["file_name"],
                "file_size": c["file_size"],
                "score": c["score"],
                "breakdown": c["breakdown"],
                "top_candidates": rec["top_candidates"],
            })
        elif ri in ambiguous:
            c = ambiguous[ri]
            amb_list.append({
                **base,
                "best_file_path": c["file_path"],
                "best_file_name": c["file_name"],
                "best_score": c["score"],
                "breakdown": c["breakdown"],
                "top_candidates": rec["top_candidates"],
            })
        else:
            unresolved.append({
                **base,
                "top_candidates": rec["top_candidates"][:3],
            })

    # Save detailed results
    results_out = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "stats": {
            "total_unmatched": len(resources),
            "upload_threshold": UPLOAD_THRESHOLD,
            "ambiguous_threshold": AMBIGUOUS_THRESHOLD,
            "high_confidence_matches": len(matches_to_upload),
            "ambiguous_matches": len(amb_list),
            "unresolved": len(unresolved),
        },
        "high_confidence_matches": matches_to_upload,
        "ambiguous_matches": amb_list,
        "unresolved_resources": unresolved,
    }
    with open(RESULTS_FILE, "w") as f:
        json.dump(results_out, f, indent=2)
    print(f"\nResults saved to {RESULTS_FILE}", flush=True)

    with open(AMBIGUOUS_FILE, "w") as f:
        json.dump({
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "note": "Review these manually; score between {:.2f} and {:.2f}.".format(
                AMBIGUOUS_THRESHOLD, UPLOAD_THRESHOLD - 0.001),
            "matches": amb_list,
        }, f, indent=2)
    print(f"Ambiguous saved to {AMBIGUOUS_FILE}", flush=True)

    print("\n── Summary ─────────────────────────────", flush=True)
    print(f"Total unmatched: {len(resources)}", flush=True)
    print(f"High-confidence (>= {UPLOAD_THRESHOLD}): {len(matches_to_upload)}", flush=True)
    print(f"Ambiguous ({AMBIGUOUS_THRESHOLD} - {UPLOAD_THRESHOLD}): {len(amb_list)}", flush=True)
    print(f"Unresolved: {len(unresolved)}", flush=True)

    if matches_to_upload:
        print("\nHigh-confidence matches:", flush=True)
        for m in matches_to_upload:
            print(f"  [{m['score']:.2f}] {m['title']!r}", flush=True)
            print(f"         -> {m['file_path']}", flush=True)

    if amb_list:
        print("\nAmbiguous (not uploaded):", flush=True)
        for m in amb_list:
            print(f"  [{m['best_score']:.2f}] {m['title']!r}", flush=True)
            print(f"         -> {m['best_file_name']}", flush=True)

    # Upload
    if match_only or dry_run:
        print("\n(skipping uploads)", flush=True)
        return

    if not matches_to_upload:
        print("\nNo high-confidence matches to upload.", flush=True)
        return

    print(f"\nUploading {len(matches_to_upload)} high-confidence matches...", flush=True)
    # Load existing persistent uploaded-paths
    uploaded_paths = set()
    if os.path.exists(UPLOADED_PATHS_FILE):
        try:
            with open(UPLOADED_PATHS_FILE) as f:
                uploaded_paths = set(json.load(f).get("paths", []))
        except Exception:
            pass

    ok = 0
    fail = 0
    for i, m in enumerate(matches_to_upload, 1):
        size_mb = m["file_size"] / 1024 / 1024
        print(f"[{i}/{len(matches_to_upload)}] {m['title']!r} -> {m['file_name']} ({size_mb:.1f} MB, score={m['score']:.2f})", flush=True)
        success, info = upload_and_attach(m)
        if success:
            ok += 1
            m["uploaded"] = True
            m["uploaded_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
            uploaded_paths.add(m["file_path"])
            # Persist uploaded paths
            with open(UPLOADED_PATHS_FILE, "w") as f:
                json.dump({"paths": sorted(uploaded_paths),
                           "last_updated": time.strftime("%Y-%m-%d %H:%M:%S")}, f, indent=2)
            print(f"  OK", flush=True)
        else:
            fail += 1
            m["upload_error"] = info
            print(f"  FAILED: {info}", flush=True)
        # Persist after each
        results_out["stats"]["uploaded"] = ok
        results_out["stats"]["upload_failed"] = fail
        with open(RESULTS_FILE, "w") as f:
            json.dump(results_out, f, indent=2)

    print(f"\n── Upload results ──────────────────────", flush=True)
    print(f"Uploaded: {ok}", flush=True)
    print(f"Failed:   {fail}", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
