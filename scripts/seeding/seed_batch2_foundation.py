#!/usr/bin/env python3
"""
Seed Batch 2: Foundation Semester resources from Anurag's archive
into the Notion Resources database via the API.

Faculty-created instruction materials only.
No student work, no student names, no feedback.
"""

import os
import json
import ssl
import time
import urllib.request

# ── Config ──────────────────────────────────────────────────────────────────
API_KEY = os.environ.get("NOTION_API_KEY")
RESOURCES_DB = "dd4ea6d9-92b4-4f28-b75c-ecb7f6b851be"
NOTION_VERSION = "2022-06-28"
BASE_URL = "https://api.notion.com/v1/pages"
RATE_LIMIT = 0.35

# SSL context (bypass cert verification)
ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

# ── Course page IDs ─────────────────────────────────────────────────────────
COURSE_IDS = {
    "IDP":   "31a89b8f-3cf1-81e4-83cf-dc7de5599c47",  # Intro to Design Practice
    "IxD":   "31a89b8f-3cf1-8193-8073-d45670faf32a",  # Intro to Interaction
    "Photo": "31a89b8f-3cf1-8178-b484-f24485376d2a",  # Intro to Photography
    "VC":    "31a89b8f-3cf1-8141-b9ed-c6cb02db8e0c",  # Fundamentals of Visual Comm
    "OA":    "31a89b8f-3cf1-818c-b507-cae59efa6c68",  # Intro to Objects & Artifacts
    "SE":    "34b89b8f-3cf1-81f8-85c1-f77157c28a8c",  # Social Entrepreneurship
}


def make_resource(title, author, rtype, semester, course_key, tags=None):
    """Build a resource dict."""
    return {
        "title": title,
        "author": author,
        "type": rtype,
        "semester": semester,
        "course_id": COURSE_IDS[course_key],
        "tags": tags or [],
    }


def build_payload(r):
    """Build Notion API payload for a resource."""
    props = {
        "Title": {"title": [{"text": {"content": r["title"]}}]},
        "Author(s)": {"rich_text": [{"text": {"content": r["author"]}}]},
        "Type": {"select": {"name": r["type"]}},
        "Semester": {"select": {"name": r["semester"]}},
        "Courses": {"relation": [{"id": r["course_id"]}]},
    }
    if r["tags"]:
        props["Tags"] = {"multi_select": [{"name": t} for t in r["tags"]]}
    return {"parent": {"database_id": RESOURCES_DB}, "properties": props}


def create_page(payload, idx, total, title):
    """POST to Notion API to create a page."""
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(BASE_URL, data=data, method="POST")
    req.add_header("Authorization", f"Bearer {API_KEY}")
    req.add_header("Content-Type", "application/json")
    req.add_header("Notion-Version", NOTION_VERSION)
    try:
        resp = urllib.request.urlopen(req, context=ssl_ctx)
        result = json.loads(resp.read())
        print(f"  [{idx}/{total}] OK: {title}", flush=True)
        return True
    except Exception as e:
        print(f"  [{idx}/{total}] FAIL: {title} -- {e}", flush=True)
        return False


# ═══════════════════════════════════════════════════════════════════════════
#  BUILD THE FULL RESOURCE LIST
# ═══════════════════════════════════════════════════════════════════════════

resources = []
SEM = "Fall 2023"

# ─────────────────────────────────────────────────────────────────────────
#  1. INTRODUCTION TO DESIGN PRACTICE  (~95 readings)
# ─────────────────────────────────────────────────────────────────────────

# Class 1 — Introduction
resources += [
    make_resource("She-Ji Design Competencies", "", "Paper", SEM, "IDP", ["Class 1 - Introduction"]),
    make_resource("IIT-ID Pathways Report 2020", "IIT Institute of Design", "PDF", SEM, "IDP", ["Class 1 - Introduction"]),
]

# Class 2 — Craft
resources += [
    make_resource("Transportation", "", "PDF", SEM, "IDP", ["Class 2 - Craft"]),
    make_resource("Architecture", "", "PDF", SEM, "IDP", ["Class 2 - Craft"]),
    make_resource("Community", "", "PDF", SEM, "IDP", ["Class 2 - Craft"]),
    make_resource("Historical Product Portfolio", "", "PDF", SEM, "IDP", ["Class 2 - Craft"]),
    make_resource("Joy in Labour", "", "PDF", SEM, "IDP", ["Class 2 - Craft"]),
]

# Class 3 — Time
resources += [
    make_resource("Behrens", "", "PDF", SEM, "IDP", ["Class 3 - Time"]),
    make_resource("World History of Design Ch 17", "", "PDF", SEM, "IDP", ["Class 3 - Time"]),
    make_resource("Scientific Management", "", "PDF", SEM, "IDP", ["Class 3 - Time"]),
    make_resource("Education", "", "PDF", SEM, "IDP", ["Class 3 - Time"]),
    make_resource("Bauhaus Futures Ch 1", "", "PDF", SEM, "IDP", ["Class 3 - Time"]),
]

# Class 4 — Space
resources += [
    make_resource("Teaching", "", "PDF", SEM, "IDP", ["Class 4 - Space"]),
    make_resource("Advertising", "", "PDF", SEM, "IDP", ["Class 4 - Space"]),
    make_resource("From Vienna to Frankfurt Inside Core-House Type 7: A History of Scarcity through the Modern Kitchen", "Hochhaeusl", "Paper", SEM, "IDP", ["Class 4 - Space"]),
    make_resource("Kitchen", "", "PDF", SEM, "IDP", ["Class 4 - Space"]),
    make_resource("Light Modulator", "", "PDF", SEM, "IDP", ["Class 4 - Space"]),
    make_resource("Loewy", "", "PDF", SEM, "IDP", ["Class 4 - Space"]),
    make_resource("Vision in Motion", "Laszlo Moholy-Nagy", "Book", SEM, "IDP", ["Class 4 - Space"]),
    make_resource("Vision in Motion (Reading Excerpt)", "Laszlo Moholy-Nagy", "PDF", SEM, "IDP", ["Class 4 - Space"]),
]

# Class 5 — Psychology
resources += [
    make_resource("As We May Think", "Vannevar Bush", "Paper", SEM, "IDP", ["Class 5 - Psychology"]),
    make_resource("RAND: Creative Thinking", "RAND Corporation", "PDF", SEM, "IDP", ["Class 5 - Psychology"]),
    make_resource("RAND P3558", "RAND Corporation", "PDF", SEM, "IDP", ["Class 5 - Psychology"]),
    make_resource("RAND TR392", "RAND Corporation", "PDF", SEM, "IDP", ["Class 5 - Psychology"]),
    make_resource("RAND IT Summer 2004", "RAND Corporation", "PDF", SEM, "IDP", ["Class 5 - Psychology"]),
    make_resource("P6681", "", "PDF", SEM, "IDP", ["Class 5 - Psychology"]),
    make_resource("McLuhan Playboy Interview 1969", "Marshall McLuhan", "Article", SEM, "IDP", ["Class 5 - Psychology"]),
    make_resource("The Medium is the Message", "Marshall McLuhan", "PDF", SEM, "IDP", ["Class 5 - Psychology"]),
    make_resource("Visualizations", "", "PDF", SEM, "IDP", ["Class 5 - Psychology"]),
    make_resource("HFG Ulm", "", "PDF", SEM, "IDP", ["Class 5 - Psychology"]),
]

# Class 6 — Methods (skip SC duplicates: dsgnmeth, managing_complexity_design,
#   Langrish, Cross History of Design Methodology)
resources += [
    make_resource("Wicked Problems", "", "Paper", SEM, "IDP", ["Class 6 - Methods"]),
    make_resource("Hospital Beds by Design", "", "Paper", SEM, "IDP", ["Class 6 - Methods"]),
    make_resource("DDR Archer Memoirs 2004", "Bruce Archer", "PDF", SEM, "IDP", ["Class 6 - Methods"]),
    make_resource("A Historical Survey of Unimark International", "", "Paper", SEM, "IDP", ["Class 6 - Methods"]),
    make_resource("Exploring Consumers' Brand Image Perceptions with Collages", "Herz", "Paper", SEM, "IDP", ["Class 6 - Methods"]),
    make_resource("Design Thinking (MIT)", "", "Paper", SEM, "IDP", ["Class 6 - Methods"]),
    make_resource("Koskinen", "Ilpo Koskinen", "Paper", SEM, "IDP", ["Class 6 - Methods"]),
]

# Class 7 — Sociology
resources += [
    make_resource("A Social Impact Assessment", "", "Paper", SEM, "IDP", ["Class 7 - Sociology"]),
    make_resource("A Short Grandiose Theory of Design", "", "Paper", SEM, "IDP", ["Class 7 - Sociology"]),
    make_resource("The Reflective Practitioner", "Donald Schon", "PDF", SEM, "IDP", ["Class 7 - Sociology"]),
    make_resource("Papanek", "Victor Papanek", "PDF", SEM, "IDP", ["Class 7 - Sociology"]),
    make_resource("Eames India Report", "Charles & Ray Eames", "PDF", SEM, "IDP", ["Class 7 - Sociology"]),
]

# Class 8 — Design Thinking (skip SC dupes: Belmont Report, Design Thinking is
#   Conservative, Why Design Thinking Works, On Design Thinking, Liedtka, Juul)
resources += [
    make_resource("Participant Worksheet", "", "PDF", SEM, "IDP", ["Class 8 - Design Thinking"]),
    make_resource("Design Thinking Overview", "", "PDF", SEM, "IDP", ["Class 8 - Design Thinking"]),
]

# Class 9 — Globalization
resources += [
    make_resource("Make it New", "Barry Katz", "Paper", SEM, "IDP", ["Class 9 - Globalization"]),
    make_resource("Experience Map Exercise", "", "PDF", SEM, "IDP", ["Class 9 - Globalization"]),
    make_resource("The Rise of the Service Economy", "Witt-Gross", "Paper", SEM, "IDP", ["Class 9 - Globalization"]),
    make_resource("Fourth Order Thinking", "", "Paper", SEM, "IDP", ["Class 9 - Globalization"]),
    make_resource("How Competitive Forces Shape Strategy", "Michael Porter", "Paper", SEM, "IDP", ["Class 9 - Globalization"]),
    make_resource("The Experience Economy", "", "Paper", SEM, "IDP", ["Class 9 - Globalization"]),
]

# Class 10 — Service Design (skip SC dupes: Designing Services, Service Positioning)
resources += [
    make_resource("Product Service Systems", "", "Paper", SEM, "IDP", ["Class 10 - Service Design"]),
    make_resource("Customer Involvement", "", "Paper", SEM, "IDP", ["Class 10 - Service Design"]),
    make_resource("Storytelling Group", "", "PDF", SEM, "IDP", ["Class 10 - Service Design"]),
]

# Class 11 — Behavior
resources += [
    make_resource("Connected Products", "", "PDF", SEM, "IDP", ["Class 11 - Behavior"]),
    make_resource("Iterative Prototyping", "", "PDF", SEM, "IDP", ["Class 11 - Behavior"]),
    make_resource("Erantilonkila", "", "PDF", SEM, "IDP", ["Class 11 - Behavior"]),
    make_resource("ec_current", "", "PDF", SEM, "IDP", ["Class 11 - Behavior"]),
    make_resource("NTT DoCoMo i-mode: Value Innovation at DoCoMo", "", "Paper", SEM, "IDP", ["Class 11 - Behavior"]),
    make_resource("No. 1 Mari Matsunaga — Designer i-mode Editor-in-Chief", "", "Article", SEM, "IDP", ["Class 11 - Behavior"]),
]

# Class 12 — User Experience (skip SC dupe: Elements of Value / R1609C)
resources += [
    make_resource("Elements of UX", "", "PDF", SEM, "IDP", ["Class 12 - User Experience"]),
]

# Class 13 — Post-Human (skip SC dupe: Belmont Report already in Class 8 skips)
resources += [
    make_resource("A.I. Is Mastering Language. Should We Trust What It Says?", "", "Article", SEM, "IDP", ["Class 13 - Post-Human"]),
    make_resource("Anthropocene Economics", "", "Paper", SEM, "IDP", ["Class 13 - Post-Human"]),
    make_resource("Posthumanism and Design", "", "Paper", SEM, "IDP", ["Class 13 - Post-Human"]),
    make_resource("Designing the Smart House", "", "Paper", SEM, "IDP", ["Class 13 - Post-Human"]),
    make_resource("The Economics of Biodiversity: The Dasgupta Review", "Partha Dasgupta", "PDF", SEM, "IDP", ["Class 13 - Post-Human"]),
    make_resource("Long-term Timeline of Technology", "", "Link", SEM, "IDP", ["Class 13 - Post-Human"]),
]

# Class 14 — Final Class
resources += [
    make_resource("Global Knowledge Futures 2013", "Jennifer Gidley", "Paper", SEM, "IDP", ["Class 14 - Final Class"]),
    make_resource("IDEO AI Ethics Cards", "IDEO", "Tool", SEM, "IDP", ["Class 14 - Final Class"]),
]

# Misc Articles — notable selections
resources += [
    make_resource("Design and Futures", "", "Paper", SEM, "IDP", ["Misc Articles"]),
    make_resource("Understanding Media", "Marshall McLuhan", "Book", SEM, "IDP", ["Misc Articles"]),
    make_resource("Augmenting Human Intellect: A Conceptual Framework", "Douglas Engelbart", "Paper", SEM, "IDP", ["Misc Articles"]),
    make_resource("The Limits to Growth", "Club of Rome", "Book", SEM, "IDP", ["Misc Articles"]),
]

# ─────────────────────────────────────────────────────────────────────────
#  2. INTRODUCTION TO INTERACTION  (~68 new)
# ─────────────────────────────────────────────────────────────────────────

# Textbooks (Type: Book) — skip After Universal Design (Guffey)
ixd_books = [
    ("Designing Interactions", "Bill Moggridge"),
    ("Plans and Situated Actions", "Lucy Suchman"),
    ("Enchanted Objects", "David Rose"),
    ("Data Feminism", "Catherine D'Ignazio"),
    ("The Computer for the 21st Century", "Mark Weiser"),
    ("Mismatch: How Inclusion Shapes Design", "Kat Holmes"),
    ("Computational Thinking", "Peter Denning"),
    ("Decolonizing Design", "Dori Tunstall"),
    ("Race After Technology", "Ruha Benjamin"),
    ("The Alignment Problem", "Brian Christian"),
    ("Computing: A Concise History", "Paul Ceruzzi"),
    ("The Materiality of Interaction", "Martin Wiberg"),
    ("Computing Machinery and Intelligence", "Alan Turing"),
    ("The Annotated Turing", "Alan Turing & Charles Petzold"),
    ("Make It So: Interaction Design Lessons from Sci-Fi", "Nathan Shedroff"),
    ("Mediating the Human Body", "James Katz"),
    ("The Civic Technologist's Practice Guide", "Cyd Harrell"),
    ("Inclusive Design for a Digital World", "Regine Gilbert"),
    ("Design as Future-Making", "Bloomsbury"),
    ("Accessible America", "Bess Williamson"),
]
for title, author in ixd_books:
    resources.append(make_resource(title, author, "Book", SEM, "IxD", ["Textbook"]))

# Lectures (Type: Slide Deck)
ixd_lectures = [
    "Intro to Interaction Kickoff",
    "Analog = Digital",
    "Information Architecture",
    "Arduino Intro",
]
for title in ixd_lectures:
    resources.append(make_resource(title, "Anurag Duddukuru", "Slide Deck", SEM, "IxD", ["Lecture"]))

# ─────────────────────────────────────────────────────────────────────────
#  3. INTRODUCTION TO PHOTOGRAPHY  (7 lectures)
# ─────────────────────────────────────────────────────────────────────────

photo_lectures = [
    "WK1 IDN487 Fall 2023",
    "WK2 IDN487 Fall 2023",
    "WK3 IDN487 Fall 2023",
    "WK4 Exposure Choices",
    "WK4 Output in Color",
    "WK4 Photo Sequencing",
    "WK5 Portraits",
]
for title in photo_lectures:
    resources.append(make_resource(title, "Anurag Duddukuru", "Slide Deck", SEM, "Photo", ["Lecture"]))

# ─────────────────────────────────────────────────────────────────────────
#  4. FUNDAMENTALS OF VISUAL COMMUNICATION  (~27 lectures + assignments)
# ─────────────────────────────────────────────────────────────────────────

# Weekly lectures (Slide Deck)
vc_lectures = [
    ("Week 1: Intro & Typography", "1 Intro Type 2023"),
    ("Week 2: Composition + Contrast", "2 Composition Contrast 23F"),
    ("Week 3: Graphic Elements", "3 Graphic Elements 23F"),
    # Week 4: no lecture file found, only PM
    ("Week 5: Imagery", "Imagery 2023F"),
    ("Week 6: Context of Use", "6 Context of Use 23F v2"),
    ("Week 7: Comparison", "7 Comparison 23"),
    ("Week 8: Info Types", "8 Info Types 2023F"),
    ("Week 9: Physical Comparison", "9 Physical Comparison 23F"),
    ("Week 10: Process", "10 Process 23F"),
    # Week 11: no folder exists
    ("Week 12: Context of Use", "12 Context of Use 23F"),
    ("Week 13: Context of Use (cont'd)", "13 Context of Use 23F"),
    ("Week 14: Final Presentation", "14 Final Presentation 23F"),
]
for title, _ in vc_lectures:
    resources.append(make_resource(title, "Anurag Duddukuru", "Slide Deck", SEM, "VC", ["Lecture"]))

# Weekly PM (assignment) files (PDF)
vc_pms = [
    "IDN483-F23-Week01-PM: Typography",
    "IDN483-F23-Week02-PM: Composition + Contrast",
    "IDN483-F23-Week03-PM: Graphic Elements",
    "IDN483-F23-Week04-PM: Tabs + Anchor Objects",
    "IDN483-F23-Week05-PM: Imagery",
    "IDN483-F23-Week07-PM: Comparison",
    "IDN483-F23-Week08-PM: Info Types",
    "IDN483-F23-Week09-PM: Physical Comparison",
    "IDN483-F23-Week10-PM: Process",
    "IDN483-F23-Week12-PM: Context of Use",
]
for title in vc_pms:
    resources.append(make_resource(title, "Anurag Duddukuru", "PDF", SEM, "VC", ["Assignment Brief"]))

# ─────────────────────────────────────────────────────────────────────────
#  5. INTRODUCTION TO OBJECTS & ARTIFACTS
# ─────────────────────────────────────────────────────────────────────────

# Lectures (Slide Deck)
oa_lectures = [
    ("Begin LPV", "Anurag Duddukuru"),
    ("Objects: Week 13 Fall Review", "Anurag Duddukuru"),
    ("2023 Fall Plan: Future of Work", "Anurag Duddukuru"),
    ("Fall 2022 Introduction to Product", "Anurag Duddukuru"),
    ("Criteria for File Folder", "Anurag Duddukuru"),
    ("File Folder Presentation and Critique", "Anurag Duddukuru"),
    ("Future of Work Concepts", "Anurag Duddukuru"),
]
for title, author in oa_lectures:
    resources.append(make_resource(title, author, "Slide Deck", SEM, "OA", ["Lecture"]))

# Lighting refs
oa_lighting = [
    ("Introduction to Lighting", "Anurag Duddukuru", "Slide Deck"),
    ("Artemide Reference", "", "PDF"),
    ("Light Book", "", "PDF"),
    ("How to Design a Light", "", "Slide Deck"),
]
for title, author, rtype in oa_lighting:
    resources.append(make_resource(title, author, rtype, SEM, "OA", ["Lighting"]))

# Tutorials (Video)
resources += [
    make_resource("Chipboard Tutorial Video", "Anurag Duddukuru", "Video", SEM, "OA", ["Tutorial"]),
    make_resource("Photoshop & Sketching Tutorial", "Anurag Duddukuru", "Video", SEM, "OA", ["Tutorial"]),
]

# Textbook
resources.append(
    make_resource("Rapid Viz", "Kurt Hanks & Larry Belliston", "Book", SEM, "OA", ["Textbook"])
)

# ─────────────────────────────────────────────────────────────────────────
#  6. SOCIAL ENTREPRENEURSHIP  (6 case studies)
# ─────────────────────────────────────────────────────────────────────────

se_cases = [
    ("GramVikas Case", "Article"),
    ("Cooks First or Tules First", "Article"),
    ("Ebony Magazine", "Article"),
    ("Kommon Goods", "Article"),
    ("Lemonade Stand", "Article"),
    ("iThrive", "Article"),
]
for title, rtype in se_cases:
    resources.append(make_resource(title, "", rtype, SEM, "SE", ["Case Study"]))


# ═══════════════════════════════════════════════════════════════════════════
#  EXECUTE: Create all resources in Notion
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    total = len(resources)
    print(f"\n{'='*60}", flush=True)
    print(f"  Seeding {total} resources into Notion Resources DB", flush=True)
    print(f"  DB: {RESOURCES_DB}", flush=True)
    print(f"{'='*60}\n", flush=True)

    ok = 0
    fail = 0
    for i, r in enumerate(resources, 1):
        payload = build_payload(r)
        if create_page(payload, i, total, r["title"]):
            ok += 1
        else:
            fail += 1
        time.sleep(RATE_LIMIT)

    print(f"\n{'='*60}", flush=True)
    print(f"  DONE: {ok} created, {fail} failed out of {total}", flush=True)
    print(f"{'='*60}\n", flush=True)
