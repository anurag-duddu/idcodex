#!/usr/bin/env python3
"""Seed the Notion Resources DB with reference materials from SC Archive."""

import os
import json
import ssl
import time
import urllib.request
import urllib.error

# Fix macOS Python SSL certificate issue
SSL_CTX = ssl.create_default_context()
try:
    import certifi
    SSL_CTX.load_verify_locations(certifi.where())
except ImportError:
    SSL_CTX.check_hostname = False
    SSL_CTX.verify_mode = ssl.CERT_NONE

API_KEY = os.environ.get("NOTION_API_KEY")
RESOURCES_DB = "dd4ea6d9-92b4-4f28-b75c-ecb7f6b851be"
NOTION_VERSION = "2022-06-28"

# Course name → Notion page ID mapping
COURSES = {
    "Introduction to Design Practice": "31a89b8f-3cf1-81e4-83cf-dc7de5599c47",
    "Introduction to Interaction": "31a89b8f-3cf1-8193-8073-d45670faf32a",
    "Introduction to Photography": "31a89b8f-3cf1-8178-b484-f24485376d2a",
    "Fundamentals of Visual Communication": "31a89b8f-3cf1-8141-b9ed-c6cb02db8e0c",
    "Introduction to Objects & Artifacts": "31a89b8f-3cf1-818c-b507-cae59efa6c68",
    "Modes of Human Experience": "31a89b8f-3cf1-8138-89ff-f2731a0fb795",
    "Introduction to Systems Theory": "31a89b8f-3cf1-8107-9dea-e72bda1275ad",
    "Systems and Systems Theory in Design": "31a89b8f-3cf1-81cc-b87c-ef50e55eb681",
    "Building and Understanding Context": "31a89b8f-3cf1-8170-ac72-e3efbbbcb627",
    "Design for Climate Leadership": "31a89b8f-3cf1-818d-a6e8-e4a3c38b1c66",
    "Analysis + Synthesis in Design": "31a89b8f-3cf1-8109-8805-f80dfd51eec1",
    "Behavioral Design for Organizational Leadership": "31a89b8f-3cf1-81ab-b129-c03f6f0c9c61",
    "Introduction to Product Strategy": "31a89b8f-3cf1-819b-9fc3-e2d2a911c954",
    "Product Design Workshop": "31a89b8f-3cf1-81d5-a928-df6595fcb396",
    "Principles & Methods of User Research": "31a89b8f-3cf1-8105-a67e-fb8a332d5283",
    "Adaptive Leadership": "31a89b8f-3cf1-8154-80bb-ea52378636f7",
    "Strategic Communication": "31a89b8f-3cf1-8151-83af-f5de01880c11",
    "Innovation Methods": "31a89b8f-3cf1-8130-bd2d-d7d7cae88b81",
}

# All reference materials from SC Archive, organized by course
RESOURCES = [
    # ── Introduction to Design Practice ── (Fall 2023)
    {"title": "The Belmont Report", "author": "National Commission for the Protection of Human Subjects", "type": "Paper", "semester": "Fall 2023", "course": "Introduction to Design Practice"},
    {"title": "The Elements of Value", "author": "Eric Almquist, John Senior, Nicolas Bloch", "type": "Article", "semester": "Fall 2023", "course": "Introduction to Design Practice"},
    {"title": "Juul and the Business of Addiction", "author": "Unknown", "type": "Article", "semester": "Fall 2023", "course": "Introduction to Design Practice"},
    {"title": "Designing Services", "author": "Unknown", "type": "Paper", "semester": "Fall 2023", "course": "Introduction to Design Practice"},
    {"title": "Things That Make Us Smart: Power of Representation (Ch. 3)", "author": "Don Norman", "type": "Book", "semester": "Fall 2023", "course": "Introduction to Design Practice"},
    {"title": "Service Positioning", "author": "Unknown", "type": "Paper", "semester": "Fall 2023", "course": "Introduction to Design Practice"},
    {"title": "Design Thinking is Conservative", "author": "Unknown", "type": "Paper", "semester": "Fall 2023", "course": "Introduction to Design Practice"},
    {"title": "Design Methods", "author": "Unknown", "type": "Paper", "semester": "Fall 2023", "course": "Introduction to Design Practice"},
    {"title": "Why Design Thinking Works", "author": "Jeanne Liedtka", "type": "Article", "semester": "Fall 2023", "course": "Introduction to Design Practice"},
    {"title": "Design Methods (Langrish)", "author": "J. Langrish", "type": "Paper", "semester": "Fall 2023", "course": "Introduction to Design Practice"},
    {"title": "Managing Complexity in Design", "author": "Unknown", "type": "Paper", "semester": "Fall 2023", "course": "Introduction to Design Practice"},
    {"title": "Evaluating the Impact of Design Thinking", "author": "Jeanne Liedtka", "type": "Paper", "semester": "Fall 2023", "course": "Introduction to Design Practice"},
    {"title": "Design Thinking (Overview)", "author": "Unknown", "type": "Paper", "semester": "Fall 2023", "course": "Introduction to Design Practice"},
    {"title": "A History of Design Methodology", "author": "Nigel Cross", "type": "Paper", "semester": "Fall 2023", "course": "Introduction to Design Practice"},
    {"title": "On Design Thinking", "author": "Unknown", "type": "Paper", "semester": "Fall 2023", "course": "Introduction to Design Practice"},

    # ── Introduction to Interaction ── (Fall 2023)
    {"title": "After Universal Design", "author": "Elizabeth Guffey", "type": "Paper", "semester": "Fall 2023", "course": "Introduction to Interaction"},
    {"title": "Making Disability Modern", "author": "Elizabeth Guffey", "type": "Paper", "semester": "Fall 2023", "course": "Introduction to Interaction"},

    # ── Modes of Human Experience ── (Spring 2024)
    {"title": "Common People", "author": "Kit De Waal", "type": "Book", "semester": "Spring 2024", "course": "Modes of Human Experience"},
    {"title": "Race After Technology", "author": "Ruha Benjamin", "type": "Book", "semester": "Spring 2024", "course": "Modes of Human Experience"},
    {"title": "About Us", "author": "Catapano", "type": "Article", "semester": "Spring 2024", "course": "Modes of Human Experience"},
    {"title": "The Beiging of America: Personal Narrative", "author": "Cathy J. Schlund-Vials", "type": "Article", "semester": "Spring 2024", "course": "Modes of Human Experience"},
    {"title": "Non-Binary Lives Anthology", "author": "Various", "type": "Book", "semester": "Spring 2024", "course": "Modes of Human Experience"},
    {"title": "The Disability Studies Reader", "author": "Lennard J. Davis", "type": "Book", "semester": "Spring 2024", "course": "Modes of Human Experience"},
    {"title": "Accessible America: A History of Disability and Design", "author": "Bess Williamson", "type": "Book", "semester": "Spring 2024", "course": "Modes of Human Experience"},

    # ── Introduction to Systems Theory / Systems and Systems Theory ── (Spring 2024)
    {"title": "Addressing the Problem of Overfishing", "author": "Cuadernos73", "type": "Paper", "semester": "Spring 2024", "course": "Systems and Systems Theory in Design"},
    {"title": "Emergent Strategy: Shaping Change, Changing Worlds", "author": "adrienne maree brown", "type": "Book", "semester": "Spring 2024", "course": "Systems and Systems Theory in Design"},
    {"title": "What Happened To You? (Excerpt)", "author": "Bruce D. Perry, Oprah Winfrey", "type": "Book", "semester": "Spring 2024", "course": "Systems and Systems Theory in Design"},
    {"title": "Thinking in Systems: A Primer", "author": "Donella Meadows", "type": "Book", "semester": "Spring 2024", "course": "Systems and Systems Theory in Design"},
    {"title": "Designing for Healing, Dignity, and Joy", "author": "Unknown", "type": "Paper", "semester": "Spring 2024", "course": "Systems and Systems Theory in Design"},

    # ── Building and Understanding Context ── (Spring 2024)
    {"title": "Backcasting Template", "author": "ID Faculty", "type": "Tool", "semester": "Spring 2024", "course": "Building and Understanding Context"},
    {"title": "Backcasting Prompts", "author": "ID Faculty", "type": "Tool", "semester": "Spring 2024", "course": "Building and Understanding Context"},
    {"title": "Future Concepts Template", "author": "ID Faculty", "type": "Tool", "semester": "Spring 2024", "course": "Building and Understanding Context"},
    {"title": "Backcasting (Reading)", "author": "Unknown", "type": "Paper", "semester": "Spring 2024", "course": "Building and Understanding Context"},
    {"title": "BUC Week 1 Lecture", "author": "ID Faculty", "type": "Slide Deck", "semester": "Spring 2024", "course": "Building and Understanding Context"},
    {"title": "BUC Week 2 Lecture", "author": "ID Faculty", "type": "Slide Deck", "semester": "Spring 2024", "course": "Building and Understanding Context"},
    {"title": "BUC Week 3 Lecture", "author": "ID Faculty", "type": "Slide Deck", "semester": "Spring 2024", "course": "Building and Understanding Context"},
    {"title": "BUC Week 4 Lecture", "author": "ID Faculty", "type": "Slide Deck", "semester": "Spring 2024", "course": "Building and Understanding Context"},
    {"title": "BUC Week 5 Lecture", "author": "ID Faculty", "type": "Slide Deck", "semester": "Spring 2024", "course": "Building and Understanding Context"},
    {"title": "BUC Week 6 Lecture", "author": "ID Faculty", "type": "Slide Deck", "semester": "Spring 2024", "course": "Building and Understanding Context"},
    {"title": "BUC Week 7 Lecture", "author": "ID Faculty", "type": "Slide Deck", "semester": "Spring 2024", "course": "Building and Understanding Context"},
    {"title": "BUC Week 8 Lecture", "author": "ID Faculty", "type": "Slide Deck", "semester": "Spring 2024", "course": "Building and Understanding Context"},
    {"title": "BUC Week 9 Lecture", "author": "ID Faculty", "type": "Slide Deck", "semester": "Spring 2024", "course": "Building and Understanding Context"},
    {"title": "BUC Week 10 Lecture", "author": "ID Faculty", "type": "Slide Deck", "semester": "Spring 2024", "course": "Building and Understanding Context"},
    {"title": "BUC Week 11 Lecture", "author": "ID Faculty", "type": "Slide Deck", "semester": "Spring 2024", "course": "Building and Understanding Context"},
    {"title": "BUC Week 12 Lecture", "author": "ID Faculty", "type": "Slide Deck", "semester": "Spring 2024", "course": "Building and Understanding Context"},
    {"title": "BUC Week 13 Lecture", "author": "ID Faculty", "type": "Slide Deck", "semester": "Spring 2024", "course": "Building and Understanding Context"},
    {"title": "BUC Week 14 Lecture", "author": "ID Faculty", "type": "Slide Deck", "semester": "Spring 2024", "course": "Building and Understanding Context"},

    # ── Design for Climate Leadership ── (Spring 2024)
    {"title": "Infrastructural Speculations", "author": "Unknown", "type": "Paper", "semester": "Spring 2024", "course": "Design for Climate Leadership"},
    {"title": "Closing the Loop: Mapping Forces (Ch. 6)", "author": "Sheryl Cababa", "type": "Book", "semester": "Spring 2024", "course": "Design for Climate Leadership"},
    {"title": "Four Sociotechnical Imaginaries for Future Food Systems", "author": "Unknown", "type": "Paper", "semester": "Spring 2024", "course": "Design for Climate Leadership"},

    # ── Analysis + Synthesis in Design ── (Spring 2024)
    {"title": "Double Diamond Framework", "author": "Design Council", "type": "Tool", "semester": "Spring 2024", "course": "Analysis + Synthesis in Design"},
    {"title": "Analysis and Synthesis Textbook Deck", "author": "ID Faculty", "type": "Slide Deck", "semester": "Spring 2024", "course": "Analysis + Synthesis in Design"},
    {"title": "Covering User Needs", "author": "Charles Owen", "type": "Paper", "semester": "Spring 2024", "course": "Analysis + Synthesis in Design"},

    # ── Behavioral Design ── (Fall 2024)
    {"title": "Behavioral Design Toolkit: Cards", "author": "Irrational Labs", "type": "Tool", "semester": "Fall 2024", "course": "Behavioral Design for Organizational Leadership"},
    {"title": "Behavioral Design Toolkit: User Guide", "author": "Irrational Labs", "type": "Tool", "semester": "Fall 2024", "course": "Behavioral Design for Organizational Leadership"},
    {"title": "Behavioral Design Toolkit: Spider Diagrams", "author": "Irrational Labs", "type": "Tool", "semester": "Fall 2024", "course": "Behavioral Design for Organizational Leadership"},
    {"title": "BD Lecture 1: Introduction", "author": "ID Faculty", "type": "Slide Deck", "semester": "Fall 2024", "course": "Behavioral Design for Organizational Leadership"},
    {"title": "BD Lecture 2: Cognitive Effort", "author": "ID Faculty", "type": "Slide Deck", "semester": "Fall 2024", "course": "Behavioral Design for Organizational Leadership"},
    {"title": "BD Lecture 3: Uncertainty", "author": "ID Faculty", "type": "Slide Deck", "semester": "Fall 2024", "course": "Behavioral Design for Organizational Leadership"},
    {"title": "BD Lecture 4: Action", "author": "ID Faculty", "type": "Slide Deck", "semester": "Fall 2024", "course": "Behavioral Design for Organizational Leadership"},
    {"title": "BD Lecture 5: Time and Social Norms", "author": "ID Faculty", "type": "Slide Deck", "semester": "Fall 2024", "course": "Behavioral Design for Organizational Leadership"},
    {"title": "BD Lecture 5 (2023): Literature Review", "author": "ID Faculty", "type": "Slide Deck", "semester": "Fall 2024", "course": "Behavioral Design for Organizational Leadership"},
    {"title": "BD Lecture 6: Full Class Case", "author": "ID Faculty", "type": "Slide Deck", "semester": "Fall 2024", "course": "Behavioral Design for Organizational Leadership"},
    {"title": "BD Lecture 7: Final Presentation Guidelines", "author": "ID Faculty", "type": "Slide Deck", "semester": "Fall 2024", "course": "Behavioral Design for Organizational Leadership"},
    {"title": "Me-We-Tools-Rules Framework", "author": "ID Faculty", "type": "Tool", "semester": "Fall 2024", "course": "Behavioral Design for Organizational Leadership"},
    {"title": "5As + Me-We-Tools-Rules Framework", "author": "ID Faculty", "type": "Tool", "semester": "Fall 2024", "course": "Behavioral Design for Organizational Leadership"},
    {"title": "Nudge for Good", "author": "Unknown", "type": "Paper", "semester": "Fall 2024", "course": "Behavioral Design for Organizational Leadership"},
    {"title": "Choice Infrastructure: Looking Beyond Choice Architecture", "author": "Unknown", "type": "Paper", "semester": "Fall 2024", "course": "Behavioral Design for Organizational Leadership"},
    {"title": "Literature Review 101", "author": "Irrational Labs", "type": "Paper", "semester": "Fall 2024", "course": "Behavioral Design for Organizational Leadership"},
    {"title": "Why Consumers Don't Buy", "author": "John Gourville", "type": "Article", "semester": "Fall 2024", "course": "Behavioral Design for Organizational Leadership"},
    {"title": "The Behavioral Tyranny of Automation", "author": "Unknown", "type": "Paper", "semester": "Fall 2024", "course": "Behavioral Design for Organizational Leadership"},
    {"title": "Anticipating Unintended Consequences (IN CASE)", "author": "Unknown", "type": "Paper", "semester": "Fall 2024", "course": "Behavioral Design for Organizational Leadership"},
    {"title": "Strange Bedfellows: Design Research and Behavioral Design", "author": "Unknown", "type": "Paper", "semester": "Fall 2024", "course": "Behavioral Design for Organizational Leadership"},
    {"title": "Hemophilia Case Study", "author": "Unknown", "type": "Article", "semester": "Fall 2024", "course": "Behavioral Design for Organizational Leadership"},
    {"title": "The New Science of Designing for Humans", "author": "SSIR", "type": "Article", "semester": "Fall 2024", "course": "Behavioral Design for Organizational Leadership"},
    {"title": "Mental Accounting Matters", "author": "Richard Thaler", "type": "Paper", "semester": "Fall 2024", "course": "Behavioral Design for Organizational Leadership"},
    {"title": "A Review of Behavioral Economics in Design", "author": "Unknown", "type": "Paper", "semester": "Fall 2024", "course": "Behavioral Design for Organizational Leadership"},

    # ── Implementing Innovation (no Notion course yet — will skip relation) ──
    {"title": "ID540 Lecture 1: Intro to Core Frameworks", "author": "ID Faculty", "type": "Slide Deck", "semester": "Fall 2024", "course": None},
    {"title": "ID540 Lecture 2: Building a Strategic Roadmap", "author": "ID Faculty", "type": "Slide Deck", "semester": "Fall 2024", "course": None},
    {"title": "ID540 Lecture 3: De-Risking the Business Model", "author": "ID Faculty", "type": "Slide Deck", "semester": "Fall 2024", "course": None},
    {"title": "ID540 Lecture 4: Designing Experiments", "author": "ID Faculty", "type": "Slide Deck", "semester": "Fall 2024", "course": None},
    {"title": "ID540 Lecture 5: Building the Business Case", "author": "ID Faculty", "type": "Slide Deck", "semester": "Fall 2024", "course": None},
    {"title": "ID540 Lecture 6: Communicating a Case for Change", "author": "ID Faculty", "type": "Slide Deck", "semester": "Fall 2024", "course": None},

    # ── Introduction to Product Strategy ── (Fall 2024)
    {"title": "Launching Strategy", "author": "Henry Mintzberg", "type": "Paper", "semester": "Fall 2024", "course": "Introduction to Product Strategy"},
    {"title": "Quest for Right Portfolio Management Process", "author": "Robert Cooper", "type": "Paper", "semester": "Fall 2024", "course": "Introduction to Product Strategy"},
    {"title": "Discipline of Market Leaders", "author": "Michael Treacy", "type": "Book", "semester": "Fall 2024", "course": "Introduction to Product Strategy"},
    {"title": "Identifying Target Customers", "author": "Alexander Chernev", "type": "Paper", "semester": "Fall 2024", "course": "Introduction to Product Strategy"},
    {"title": "What Customers Want", "author": "Anthony Ulwick", "type": "Book", "semester": "Fall 2024", "course": "Introduction to Product Strategy"},
    {"title": "Why Consumers Don't Buy", "author": "John Gourville", "type": "Article", "semester": "Fall 2024", "course": "Introduction to Product Strategy"},
    {"title": "Creating a New Market Space", "author": "W. Chan Kim", "type": "Article", "semester": "Fall 2024", "course": "Introduction to Product Strategy"},
    {"title": "Mapping Your Competitive Position", "author": "Richard D'Aveni", "type": "Article", "semester": "Fall 2024", "course": "Introduction to Product Strategy"},
    {"title": "Different", "author": "Youngme Moon", "type": "Book", "semester": "Fall 2024", "course": "Introduction to Product Strategy"},
    {"title": "Skate to Where the Money Will Be", "author": "Clayton Christensen", "type": "Article", "semester": "Fall 2024", "course": "Introduction to Product Strategy"},
    {"title": "Planning as Learning", "author": "Arie de Geus", "type": "Article", "semester": "Fall 2024", "course": "Introduction to Product Strategy"},
    {"title": "Playing to Win (Ch. 1)", "author": "Roger Martin", "type": "Book", "semester": "Fall 2024", "course": "Introduction to Product Strategy"},
    {"title": "Knowing a Business Idea", "author": "W. Chan Kim", "type": "Paper", "semester": "Fall 2024", "course": "Introduction to Product Strategy"},
    {"title": "Darwin and the Demon", "author": "Geoffrey Moore", "type": "Book", "semester": "Fall 2024", "course": "Introduction to Product Strategy"},
    {"title": "Exploiting Analogy", "author": "Roger Martin", "type": "Paper", "semester": "Fall 2024", "course": "Introduction to Product Strategy"},
    {"title": "Is it Worth Doing?", "author": "George Day", "type": "Paper", "semester": "Fall 2024", "course": "Introduction to Product Strategy"},
    {"title": "Portfolio Management (Ch. 5)", "author": "Robert Cooper", "type": "Book", "semester": "Fall 2024", "course": "Introduction to Product Strategy"},
    {"title": "Portfolio Management (Full)", "author": "Robert Cooper", "type": "Book", "semester": "Fall 2024", "course": "Introduction to Product Strategy"},
    {"title": "Conquering a Culture of Indecision", "author": "Ram Charan", "type": "Article", "semester": "Fall 2024", "course": "Introduction to Product Strategy"},
    {"title": "Interpretive Management", "author": "Richard Lester", "type": "Paper", "semester": "Fall 2024", "course": "Introduction to Product Strategy"},
    {"title": "Levels of Innovation", "author": "Unknown", "type": "Paper", "semester": "Fall 2024", "course": "Introduction to Product Strategy"},
    {"title": "Market Lifecycle", "author": "Unknown", "type": "Paper", "semester": "Fall 2024", "course": "Introduction to Product Strategy"},
    {"title": "Value Disciplines (Framework)", "author": "Unknown", "type": "Tool", "semester": "Fall 2024", "course": "Introduction to Product Strategy"},
    {"title": "One Pager Template", "author": "ID Faculty", "type": "Tool", "semester": "Fall 2024", "course": "Introduction to Product Strategy"},

    # ── Principles & Methods of User Research ── (Fall 2024)
    # Lectures
    {"title": "PMUR Week 1: Introduction", "author": "ID Faculty", "type": "Slide Deck", "semester": "Fall 2024", "course": "Principles & Methods of User Research"},
    {"title": "PMUR Week 2: Ethnography", "author": "ID Faculty", "type": "Slide Deck", "semester": "Fall 2024", "course": "Principles & Methods of User Research"},
    {"title": "PMUR Week 3: Interviews + Intercepts", "author": "ID Faculty", "type": "Slide Deck", "semester": "Fall 2024", "course": "Principles & Methods of User Research"},
    {"title": "PMUR Week 4: Contextual Inquiry", "author": "ID Faculty", "type": "Slide Deck", "semester": "Fall 2024", "course": "Principles & Methods of User Research"},
    {"title": "PMUR Week 5: Object-Based Techniques", "author": "ID Faculty", "type": "Slide Deck", "semester": "Fall 2024", "course": "Principles & Methods of User Research"},
    {"title": "PMUR Week 6: Experience Sampling", "author": "ID Faculty", "type": "Slide Deck", "semester": "Fall 2024", "course": "Principles & Methods of User Research"},
    {"title": "PMUR Week 7: Surveys", "author": "ID Faculty", "type": "Slide Deck", "semester": "Fall 2024", "course": "Principles & Methods of User Research"},
    {"title": "PMUR Week 8: Research Planning", "author": "ID Faculty", "type": "Slide Deck", "semester": "Fall 2024", "course": "Principles & Methods of User Research"},
    {"title": "PMUR Week 9: Usability", "author": "ID Faculty", "type": "Slide Deck", "semester": "Fall 2024", "course": "Principles & Methods of User Research"},
    {"title": "PMUR Week 10: Analysis", "author": "ID Faculty", "type": "Slide Deck", "semester": "Fall 2024", "course": "Principles & Methods of User Research"},
    {"title": "PMUR Week 11: Synthesis", "author": "ID Faculty", "type": "Slide Deck", "semester": "Fall 2024", "course": "Principles & Methods of User Research"},
    {"title": "PMUR Week 12: Framing + Narrative", "author": "ID Faculty", "type": "Slide Deck", "semester": "Fall 2024", "course": "Principles & Methods of User Research"},
    {"title": "PMUR Week 13: Guerrilla Research", "author": "ID Faculty", "type": "Slide Deck", "semester": "Fall 2024", "course": "Principles & Methods of User Research"},
    # Readings
    {"title": "Ethnography in the Field of Design", "author": "Christina Wasson", "type": "Paper", "semester": "Fall 2024", "course": "Principles & Methods of User Research"},
    {"title": "What to Do with a Human Factor", "author": "Rick Robinson", "type": "Paper", "semester": "Fall 2024", "course": "Principles & Methods of User Research"},
    {"title": "Observing the UX: Ch. 9", "author": "Elizabeth Goodman", "type": "Book", "semester": "Fall 2024", "course": "Principles & Methods of User Research"},
    {"title": "Watching Closely (Ch. 3)", "author": "Christena Nippert-Eng", "type": "Book", "semester": "Fall 2024", "course": "Principles & Methods of User Research"},
    {"title": "Interviewing Users (Ch. 5-6)", "author": "Steve Portigal", "type": "Book", "semester": "Fall 2024", "course": "Principles & Methods of User Research"},
    {"title": "Contextual Design", "author": "Karen Holtzblatt", "type": "Book", "semester": "Fall 2024", "course": "Principles & Methods of User Research"},
    {"title": "Card Sorting", "author": "Aamna Nawaz", "type": "Paper", "semester": "Fall 2024", "course": "Principles & Methods of User Research"},
    {"title": "Observing the UX: Ch. 8", "author": "Elizabeth Goodman", "type": "Book", "semester": "Fall 2024", "course": "Principles & Methods of User Research"},
    {"title": "Experience Sampling (Ch. 10, Larson)", "author": "Reed Larson", "type": "Book", "semester": "Fall 2024", "course": "Principles & Methods of User Research"},
    {"title": "Observing the UX: Ch. 10", "author": "Elizabeth Goodman", "type": "Book", "semester": "Fall 2024", "course": "Principles & Methods of User Research"},
    {"title": "Observing the UX: Ch. 12 (Surveys)", "author": "Elizabeth Goodman", "type": "Book", "semester": "Fall 2024", "course": "Principles & Methods of User Research"},
    {"title": "Practical Ethnography (Research Planning)", "author": "Unknown", "type": "Book", "semester": "Fall 2024", "course": "Principles & Methods of User Research"},
    {"title": "Research Planning (Ch. 4)", "author": "Elizabeth Goodman", "type": "Book", "semester": "Fall 2024", "course": "Principles & Methods of User Research"},
    {"title": "Beyond 5-User Sample Size", "author": "Laura Faulkner", "type": "Paper", "semester": "Fall 2024", "course": "Principles & Methods of User Research"},
    {"title": "Observing the UX: Ch. 11 (Usability)", "author": "Elizabeth Goodman", "type": "Book", "semester": "Fall 2024", "course": "Principles & Methods of User Research"},
    {"title": "Grounded Theory", "author": "Strauss and Corbin", "type": "Paper", "semester": "Fall 2024", "course": "Principles & Methods of User Research"},
    {"title": "Miles and Huberman (Analysis)", "author": "Matthew Miles, A. Michael Huberman", "type": "Book", "semester": "Fall 2024", "course": "Principles & Methods of User Research"},
    {"title": "Observing the UX: Ch. 17 (Deliverables)", "author": "Elizabeth Goodman", "type": "Book", "semester": "Fall 2024", "course": "Principles & Methods of User Research"},
    {"title": "Research for Beginners (Ch. 4-5)", "author": "Unknown", "type": "Book", "semester": "Fall 2024", "course": "Principles & Methods of User Research"},
    {"title": "A More Beautiful Question (pp. 11-28)", "author": "Warren Berger", "type": "Book", "semester": "Fall 2024", "course": "Principles & Methods of User Research"},
    {"title": "The Value of Codesign", "author": "Unknown", "type": "Paper", "semester": "Fall 2024", "course": "Principles & Methods of User Research"},
    {"title": "ASQ (After-Scenario Questionnaire)", "author": "Unknown", "type": "Tool", "semester": "Fall 2024", "course": "Principles & Methods of User Research"},
    # Best Practice Examples
    {"title": "Patient Interview Guide (Sample)", "author": "Unknown", "type": "Tool", "semester": "Fall 2024", "course": "Principles & Methods of User Research"},
    {"title": "Screener Template (Doblin)", "author": "Doblin", "type": "Tool", "semester": "Fall 2024", "course": "Principles & Methods of User Research"},
    {"title": "Screener Template (Online Shopping)", "author": "Unknown", "type": "Tool", "semester": "Fall 2024", "course": "Principles & Methods of User Research"},

    # ── Adaptive Leadership ── (Fall 2024)
    {"title": "30-Minute Case Consultation Template", "author": "ID Faculty", "type": "Tool", "semester": "Fall 2024", "course": "Adaptive Leadership"},
    {"title": "Wicked Problems", "author": "Unknown", "type": "Paper", "semester": "Fall 2024", "course": "Adaptive Leadership"},
    {"title": "Week 1: Distinguishing Leadership from Authority", "author": "ID Faculty", "type": "Slide Deck", "semester": "Fall 2024", "course": "Adaptive Leadership"},
    {"title": "Week 2: Technical Problems vs. Adaptive Challenges", "author": "ID Faculty", "type": "Slide Deck", "semester": "Fall 2024", "course": "Adaptive Leadership"},
    {"title": "Week 3: Diagnosis of the System", "author": "ID Faculty", "type": "Slide Deck", "semester": "Fall 2024", "course": "Adaptive Leadership"},
    {"title": "Week 4: Factions and Analyzing Human Aspects of Change", "author": "ID Faculty", "type": "Slide Deck", "semester": "Fall 2024", "course": "Adaptive Leadership"},
    {"title": "Adaptive Leadership Quick Reference Guide", "author": "ID Faculty", "type": "Tool", "semester": "Fall 2024", "course": "Adaptive Leadership"},

    # ── Strategic Communication ── (Fall 2024)
    {"title": "Week 1: Introduction", "author": "ID Faculty", "type": "Slide Deck", "semester": "Fall 2024", "course": "Strategic Communication"},
    {"title": "Week 2: Visual Frameworks", "author": "ID Faculty", "type": "Slide Deck", "semester": "Fall 2024", "course": "Strategic Communication"},
    {"title": "Week 3: Initial POV", "author": "ID Faculty", "type": "Slide Deck", "semester": "Fall 2024", "course": "Strategic Communication"},
    {"title": "Week 4: Abstraction + Voice", "author": "ID Faculty", "type": "Slide Deck", "semester": "Fall 2024", "course": "Strategic Communication"},
    {"title": "Week 5: Testimony", "author": "ID Faculty", "type": "Slide Deck", "semester": "Fall 2024", "course": "Strategic Communication"},
    {"title": "One-Pager Critique Form", "author": "ID Faculty", "type": "Tool", "semester": "Fall 2024", "course": "Strategic Communication"},
    {"title": "Thought Starters Worksheet", "author": "ID Faculty", "type": "Tool", "semester": "Fall 2024", "course": "Strategic Communication"},
    {"title": "Strategic Evidence Worksheet", "author": "ID Faculty", "type": "Tool", "semester": "Fall 2024", "course": "Strategic Communication"},
    {"title": "Narrative Development Worksheet", "author": "ID Faculty", "type": "Tool", "semester": "Fall 2024", "course": "Strategic Communication"},
    {"title": "Backyard Farms Client Brief", "author": "Unknown", "type": "PDF", "semester": "Fall 2024", "course": "Strategic Communication"},
]


def create_resource(resource):
    """Create a single resource entry in Notion."""
    properties = {
        "Title": {"title": [{"text": {"content": resource["title"]}}]},
        "Author(s)": {"rich_text": [{"text": {"content": resource["author"]}}]},
        "Type": {"select": {"name": resource["type"]}},
        "Semester": {"select": {"name": resource["semester"]}},
    }

    # Add course relation if mapped
    course_name = resource.get("course")
    if course_name and course_name in COURSES:
        properties["Courses"] = {
            "relation": [{"id": COURSES[course_name]}]
        }

    body = json.dumps({
        "parent": {"database_id": RESOURCES_DB},
        "properties": properties,
    }).encode()

    req = urllib.request.Request(
        "https://api.notion.com/v1/pages",
        data=body,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, context=SSL_CTX) as resp:
            return json.loads(resp.read())["id"]
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"  ERROR ({e.code}): {error_body[:200]}")
        return None


def main():
    print(f"Seeding {len(RESOURCES)} resources into Notion...", flush=True)
    success = 0
    failed = 0

    for i, resource in enumerate(RESOURCES):
        course_label = resource.get("course", "No course")
        print(f"[{i+1}/{len(RESOURCES)}] {resource['title']} ({course_label})", flush=True)
        page_id = create_resource(resource)
        if page_id:
            success += 1
            print(f"  OK: {page_id}", flush=True)
        else:
            failed += 1
        # Rate limit: ~3 req/sec
        time.sleep(0.35)

    print(f"\nDone! {success} created, {failed} failed.", flush=True)


if __name__ == "__main__":
    main()
