#!/usr/bin/env python3
"""Seed Notion Resources DB — Batch 2: Anurag archive unique materials."""

import os
import json
import ssl
import time
import urllib.request
import urllib.error

# SSL config per instructions
SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

API_KEY = os.environ.get("NOTION_API_KEY")
RESOURCES_DB = "dd4ea6d9-92b4-4f28-b75c-ecb7f6b851be"
NOTION_VERSION = "2022-06-28"

# Course page IDs
COURSES = {
    "Systems and Systems Theory in Design": "31a89b8f-3cf1-81cc-b87c-ef50e55eb681",
    "Building and Understanding Context":   "31a89b8f-3cf1-8170-ac72-e3efbbbcb627",
    "Analysis + Synthesis in Design":       "31a89b8f-3cf1-8109-8805-f80dfd51eec1",
    "Innovation Methods":                   "31a89b8f-3cf1-8130-bd2d-d7d7cae88b81",
    "Innovation Frontiers":                 "31a89b8f-3cf1-8149-a35b-d2917e6c6eca",
    "Design for Digital Technology":        "34b89b8f-3cf1-818c-9fc2-ebca76ea1c16",
    "Implementing Innovation":              "34b89b8f-3cf1-812c-8bcf-ef479a0b5fde",
    "Decision Quality":                     "34b89b8f-3cf1-814a-a857-e449ed3907c8",
}

# ── All resources to seed ──
RESOURCES = [
    # ═══════════════════════════════════════════════════════════════
    # Systems and Systems Theory in Design — Spring 2024
    # (Already seeded: Overfishing, Emergent Strategy, What Happened
    #  To You, Thinking in Systems, Healing Dignity)
    # ═══════════════════════════════════════════════════════════════

    # 8 weekly lecture decks
    {"title": "Week 1 — Intro to Systems",
     "author": "Anurag Radhakrishnan", "type": "Slide Deck",
     "semester": "Spring 2024",
     "course": "Systems and Systems Theory in Design"},
    {"title": "Week 2 — Family Systems & Trauma Informed Design",
     "author": "Anurag Radhakrishnan", "type": "Slide Deck",
     "semester": "Spring 2024",
     "course": "Systems and Systems Theory in Design"},
    {"title": "Week 3 — Tools and Concepts",
     "author": "Anurag Radhakrishnan", "type": "Slide Deck",
     "semester": "Spring 2024",
     "course": "Systems and Systems Theory in Design"},
    {"title": "Week 4 — Systems of Oppression",
     "author": "Anurag Radhakrishnan", "type": "Slide Deck",
     "semester": "Spring 2024",
     "course": "Systems and Systems Theory in Design"},
    {"title": "Week 5 — Power Dynamics & Economics",
     "author": "Anurag Radhakrishnan", "type": "Slide Deck",
     "semester": "Spring 2024",
     "course": "Systems and Systems Theory in Design"},
    {"title": "Week 5 Part 2 — Economic Systems",
     "author": "Anurag Radhakrishnan", "type": "Slide Deck",
     "semester": "Spring 2024",
     "course": "Systems and Systems Theory in Design"},
    {"title": "Week 6 — Tactical Design for Systems Change",
     "author": "Anurag Radhakrishnan", "type": "Slide Deck",
     "semester": "Spring 2024",
     "course": "Systems and Systems Theory in Design"},
    {"title": "Week 7 — Career Pathways",
     "author": "Anurag Radhakrishnan", "type": "Slide Deck",
     "semester": "Spring 2024",
     "course": "Systems and Systems Theory in Design"},

    # Syllabus
    {"title": "Systems & Systems Theory Syllabus — Spring 2024",
     "author": "Anurag Radhakrishnan", "type": "PDF",
     "semester": "Spring 2024",
     "course": "Systems and Systems Theory in Design"},

    # Readings (new, not already seeded)
    {"title": "Invisible Women: Data Bias in a World Designed for Men",
     "author": "Caroline Criado-Perez", "type": "Book",
     "semester": "Spring 2024",
     "course": "Systems and Systems Theory in Design"},
    {"title": "Impact With Integrity — Ch 4",
     "author": "Margiotta", "type": "Book",
     "semester": "Spring 2024",
     "course": "Systems and Systems Theory in Design"},
    {"title": "Multi-Level Perspective on System Innovation (Geels 2006)",
     "author": "Frank W. Geels", "type": "Paper",
     "semester": "Spring 2024",
     "course": "Systems and Systems Theory in Design"},

    # Assignment descriptions
    {"title": "Personal Worldview Essay — Assignment Brief",
     "author": "Anurag Radhakrishnan", "type": "PDF",
     "semester": "Spring 2024",
     "course": "Systems and Systems Theory in Design"},
    {"title": "Trauma Informed Design Assignment — Brief",
     "author": "Anurag Radhakrishnan", "type": "PDF",
     "semester": "Spring 2024",
     "course": "Systems and Systems Theory in Design"},
    {"title": "Mapping Project Brief",
     "author": "Anurag Radhakrishnan", "type": "PDF",
     "semester": "Spring 2024",
     "course": "Systems and Systems Theory in Design"},

    # ═══════════════════════════════════════════════════════════════
    # Building and Understanding Context — Spring 2024
    # (Already seeded: 14 lectures, 3 templates, 1 reading)
    # ═══════════════════════════════════════════════════════════════
    {"title": "101 Design Methods",
     "author": "Vijay Kumar", "type": "Book",
     "semester": "Spring 2024",
     "course": "Building and Understanding Context"},
    {"title": "The Craft of Research (4th Edition)",
     "author": "Booth, Colomb, Williams, Bizup", "type": "Book",
     "semester": "Spring 2024",
     "course": "Building and Understanding Context"},
    {"title": "Sensemaking — Introduction Ch 1",
     "author": "Unknown", "type": "Book",
     "semester": "Spring 2024",
     "course": "Building and Understanding Context"},
    {"title": "IDX 550 Syllabus — Spring 2024",
     "author": "Anurag Radhakrishnan", "type": "PDF",
     "semester": "Spring 2024",
     "course": "Building and Understanding Context"},

    # ═══════════════════════════════════════════════════════════════
    # Analysis + Synthesis in Design — Spring 2024
    # (Already seeded: textbook deck, Double Diamond, Covering User Needs)
    # ═══════════════════════════════════════════════════════════════
    {"title": "The McKinsey Mind",
     "author": "Ethan Rasiel, Paul Friga", "type": "Book",
     "semester": "Spring 2024",
     "course": "Analysis + Synthesis in Design"},
    {"title": "Gift Giving Facilitator Guide",
     "author": "Anurag Radhakrishnan", "type": "Tool",
     "semester": "Spring 2024",
     "course": "Analysis + Synthesis in Design"},
    {"title": "Bonus Class Slides",
     "author": "Anurag Radhakrishnan", "type": "Slide Deck",
     "semester": "Spring 2024",
     "course": "Analysis + Synthesis in Design"},
    {"title": "Exercise Templates — Solving Business Problems",
     "author": "Anurag Radhakrishnan", "type": "Tool",
     "semester": "Spring 2024",
     "course": "Analysis + Synthesis in Design"},

    # ═══════════════════════════════════════════════════════════════
    # Innovation Methods — Spring 2024
    # ═══════════════════════════════════════════════════════════════
    {"title": "IM Spring 2024 — Full Course Lecture Deck (133 slides)",
     "author": "Anurag Radhakrishnan", "type": "Slide Deck",
     "semester": "Spring 2024",
     "course": "Innovation Methods"},
    {"title": "Innovation Methods Syllabus — Spring 2024",
     "author": "Anurag Radhakrishnan", "type": "PDF",
     "semester": "Spring 2024",
     "course": "Innovation Methods"},
    {"title": "Naked Innovation",
     "author": "Paradis, McGaw", "type": "Book",
     "semester": "Spring 2024",
     "course": "Innovation Methods"},
    {"title": "Experimentation Fieldbook Preview",
     "author": "Unknown", "type": "Book",
     "semester": "Spring 2024",
     "course": "Innovation Methods"},
    {"title": "Haas EMBA — Test and Shape 2023",
     "author": "Unknown", "type": "Slide Deck",
     "semester": "Spring 2024",
     "course": "Innovation Methods"},
    {"title": "Social Contract Video",
     "author": "Unknown", "type": "Video",
     "semester": "Spring 2024",
     "course": "Innovation Methods"},
    {"title": "Make Prototype Guide",
     "author": "Unknown", "type": "PDF",
     "semester": "Spring 2024",
     "course": "Innovation Methods"},
    {"title": "Hyatt Toolkit",
     "author": "Unknown", "type": "Tool",
     "semester": "Spring 2024",
     "course": "Innovation Methods"},
    {"title": "Thanks to AI (WSJ)",
     "author": "WSJ", "type": "Article",
     "semester": "Spring 2024",
     "course": "Innovation Methods"},
    {"title": "Why We Risk Cartoon Version of Capitalism (WSJ)",
     "author": "WSJ", "type": "Article",
     "semester": "Spring 2024",
     "course": "Innovation Methods"},
    {"title": "Jump Payback on Purpose",
     "author": "Unknown", "type": "Article",
     "semester": "Spring 2024",
     "course": "Innovation Methods"},

    # ═══════════════════════════════════════════════════════════════
    # Innovation Frontiers (IDN 530) — Spring 2025
    # ═══════════════════════════════════════════════════════════════
    {"title": "IDN 530 Integrated Syllabus 2025",
     "author": "Anurag Radhakrishnan", "type": "PDF",
     "semester": "Spring 2025",
     "course": "Innovation Frontiers"},
    {"title": "IDN 530 Video Lecture Links",
     "author": "Anurag Radhakrishnan", "type": "PDF",
     "semester": "Spring 2025",
     "course": "Innovation Frontiers"},
    {"title": "Lecture 1 — March 2025",
     "author": "Anurag Radhakrishnan", "type": "Slide Deck",
     "semester": "Spring 2025",
     "course": "Innovation Frontiers"},
    {"title": "Lecture 2 — April 2025",
     "author": "Anurag Radhakrishnan", "type": "Slide Deck",
     "semester": "Spring 2025",
     "course": "Innovation Frontiers"},
    {"title": "Lecture 3 — April 2025",
     "author": "Anurag Radhakrishnan", "type": "Slide Deck",
     "semester": "Spring 2025",
     "course": "Innovation Frontiers"},
    {"title": "Supplemental Ecosystems Protocols — April 2025",
     "author": "Anurag Radhakrishnan", "type": "Tool",
     "semester": "Spring 2025",
     "course": "Innovation Frontiers"},
    {"title": "IDN 530 Platform Protocols — April 2025",
     "author": "Anurag Radhakrishnan", "type": "Tool",
     "semester": "Spring 2025",
     "course": "Innovation Frontiers"},

    # ═══════════════════════════════════════════════════════════════
    # Design for Digital Technology — Spring 2024
    # 26 readings
    # ═══════════════════════════════════════════════════════════════
    {"title": "Into Ambient Intelligence",
     "author": "Aarts, Encarnacao", "type": "Book",
     "semester": "Spring 2024",
     "course": "Design for Digital Technology"},
    {"title": "AI Wants Communication-First Design",
     "author": "Unknown", "type": "Paper",
     "semester": "Spring 2024",
     "course": "Design for Digital Technology"},
    {"title": "The Nature of Technology — Ch 1",
     "author": "W. Brian Arthur", "type": "Book",
     "semester": "Spring 2024",
     "course": "Design for Digital Technology"},
    {"title": "The Nature of Technology — Ch 2",
     "author": "W. Brian Arthur", "type": "Book",
     "semester": "Spring 2024",
     "course": "Design for Digital Technology"},
    {"title": "The Nature of Technology — Ch 6",
     "author": "W. Brian Arthur", "type": "Book",
     "semester": "Spring 2024",
     "course": "Design for Digital Technology"},
    {"title": "The Internet of Things",
     "author": "Bruce Sterling", "type": "Book",
     "semester": "Spring 2024",
     "course": "Design for Digital Technology"},
    {"title": "Women's Assessment of Technology",
     "author": "Bush", "type": "Paper",
     "semester": "Spring 2024",
     "course": "Design for Digital Technology"},
    {"title": "Platforms and Ecosystems",
     "author": "Cain", "type": "Paper",
     "semester": "Spring 2024",
     "course": "Design for Digital Technology"},
    {"title": "Three Models of Strategy",
     "author": "Chaffee", "type": "Paper",
     "semester": "Spring 2024",
     "course": "Design for Digital Technology"},
    {"title": "Creating Creativity",
     "author": "Unknown", "type": "Paper",
     "semester": "Spring 2024",
     "course": "Design for Digital Technology"},
    {"title": "Exercise: Mapping Strategic Context",
     "author": "Unknown", "type": "Paper",
     "semester": "Spring 2024",
     "course": "Design for Digital Technology"},
    {"title": "Two Dimensions of Uncertainty",
     "author": "Fox, Ulkumen", "type": "Paper",
     "semester": "Spring 2024",
     "course": "Design for Digital Technology"},
    {"title": "Homo Ludens",
     "author": "Gaver", "type": "Paper",
     "semester": "Spring 2024",
     "course": "Design for Digital Technology"},
    {"title": "Affordances",
     "author": "Gibson", "type": "Paper",
     "semester": "Spring 2024",
     "course": "Design for Digital Technology"},
    {"title": "The Medium Is the Message",
     "author": "Marshall McLuhan", "type": "Book",
     "semester": "Spring 2024",
     "course": "Design for Digital Technology"},
    {"title": "Navigating Design, Data, and Decision (She Ji 2023)",
     "author": "Unknown", "type": "Paper",
     "semester": "Spring 2024",
     "course": "Design for Digital Technology"},
    {"title": "Alternative Design",
     "author": "Nieusma", "type": "Paper",
     "semester": "Spring 2024",
     "course": "Design for Digital Technology"},
    {"title": "Design Thinking — Ch 4",
     "author": "Nigel Cross", "type": "Book",
     "semester": "Spring 2024",
     "course": "Design for Digital Technology"},
    {"title": "Design Thinking — Ch 7",
     "author": "Nigel Cross", "type": "Book",
     "semester": "Spring 2024",
     "course": "Design for Digital Technology"},
    {"title": "What Is Technology?",
     "author": "Nightingale", "type": "Paper",
     "semester": "Spring 2024",
     "course": "Design for Digital Technology"},
    {"title": "Pipelines, Platforms, and the New Rules of Strategy (HBR)",
     "author": "Van Alstyne, Parker, Choudary", "type": "Article",
     "semester": "Spring 2024",
     "course": "Design for Digital Technology"},
    {"title": "How Smart, Connected Products Are Transforming Competition (HBR)",
     "author": "Michael E. Porter, James E. Heppelmann", "type": "Article",
     "semester": "Spring 2024",
     "course": "Design for Digital Technology"},
    {"title": "The Reasoning of Designers",
     "author": "Rittel", "type": "Paper",
     "semester": "Spring 2024",
     "course": "Design for Digital Technology"},
    {"title": "Capitalism, Socialism and Democracy (Excerpt)",
     "author": "Joseph Schumpeter", "type": "Book",
     "semester": "Spring 2024",
     "course": "Design for Digital Technology"},
    {"title": "The Sciences of the Artificial — Ch 1",
     "author": "Herbert A. Simon", "type": "Book",
     "semester": "Spring 2024",
     "course": "Design for Digital Technology"},
    {"title": "Steel Axes for Stone-Age Australians",
     "author": "Unknown", "type": "Paper",
     "semester": "Spring 2024",
     "course": "Design for Digital Technology"},
    {"title": "Plans and Situated Actions",
     "author": "Lucy Suchman", "type": "Book",
     "semester": "Spring 2024",
     "course": "Design for Digital Technology"},
    {"title": "The Dark Patterns Side of UX Design",
     "author": "Unknown", "type": "Paper",
     "semester": "Spring 2024",
     "course": "Design for Digital Technology"},
    {"title": "What if LLMs Were Interesting",
     "author": "Unknown", "type": "Paper",
     "semester": "Spring 2024",
     "course": "Design for Digital Technology"},
    {"title": "Writing the Implosion (Cultural Anthropology)",
     "author": "Unknown", "type": "Paper",
     "semester": "Spring 2024",
     "course": "Design for Digital Technology"},

    # ═══════════════════════════════════════════════════════════════
    # Implementing Innovation — Fall 2024
    # SKIP — nothing new beyond SC archive
    # ═══════════════════════════════════════════════════════════════

    # ═══════════════════════════════════════════════════════════════
    # Decision Quality — Spring 2025
    # ═══════════════════════════════════════════════════════════════
    {"title": "DQ for Design Manual",
     "author": "Anurag Radhakrishnan", "type": "Tool",
     "semester": "Spring 2025",
     "course": "Decision Quality"},
    {"title": "Deployment Exploration Manual",
     "author": "Anurag Radhakrishnan", "type": "Tool",
     "semester": "Spring 2025",
     "course": "Decision Quality"},
]


def create_resource(r: dict) -> dict:
    """Build Notion page-create payload for one resource."""
    course_id = COURSES[r["course"]]
    return {
        "parent": {"database_id": RESOURCES_DB},
        "properties": {
            "Title": {
                "title": [{"text": {"content": r["title"]}}]
            },
            "Author(s)": {
                "rich_text": [{"text": {"content": r["author"]}}]
            },
            "Type": {
                "select": {"name": r["type"]}
            },
            "Semester": {
                "select": {"name": r["semester"]}
            },
            "Courses": {
                "relation": [{"id": course_id}]
            },
        },
    }


def post_page(payload: dict) -> str:
    """POST to Notion pages endpoint. Returns page ID or error string."""
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        "https://api.notion.com/v1/pages",
        data=data,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
            "Notion-Version": NOTION_VERSION,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, context=SSL_CTX) as resp:
            body = json.loads(resp.read())
            return body["id"]
    except urllib.error.HTTPError as e:
        err_body = e.read().decode()
        return f"ERROR {e.code}: {err_body}"


def main():
    total = len(RESOURCES)
    ok = 0
    fail = 0
    print(f"Seeding {total} resources into Notion Resources DB...", flush=True)
    print("=" * 60, flush=True)

    for i, r in enumerate(RESOURCES, 1):
        payload = create_resource(r)
        result = post_page(payload)
        if result.startswith("ERROR"):
            fail += 1
            print(f"[{i}/{total}] FAIL  {r['title']}", flush=True)
            print(f"         {result[:200]}", flush=True)
        else:
            ok += 1
            print(f"[{i}/{total}] OK    {r['title']}", flush=True)
        time.sleep(0.35)

    print("=" * 60, flush=True)
    print(f"Done. {ok} succeeded, {fail} failed out of {total}.", flush=True)


if __name__ == "__main__":
    main()
