#!/usr/bin/env python3
"""Seed Notion Resources DB — Batch 2: Anurag-unique elective materials."""

import os
import json
import ssl
import time
import urllib.request
import urllib.error

# SSL setup
SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

API_KEY = os.environ.get("NOTION_API_KEY")
RESOURCES_DB = "dd4ea6d9-92b4-4f28-b75c-ecb7f6b851be"
NOTION_VERSION = "2022-06-28"

# Course page IDs
COURSES = {
    "Adaptive Leadership": "31a89b8f-3cf1-8154-80bb-ea52378636f7",
    "PMUR": "31a89b8f-3cf1-8105-a67e-fb8a332d5283",
    "Strategic Communication": "31a89b8f-3cf1-8151-83af-f5de01880c11",
    "Behavioral Design": "31a89b8f-3cf1-81ab-b129-c03f6f0c9c61",
    "Communication Systems": "31a89b8f-3cf1-811a-acd6-c14108fd7d83",
    "Metrics that Matter": "31a89b8f-3cf1-81c2-8926-eb4deecb371d",
    "Facilitation Methods": "31a89b8f-3cf1-81c6-bd30-e61189482dac",
    "Org Models of Innovation": "31a89b8f-3cf1-819f-adea-f759a8e28df3",
    "Multidisciplinary Innovation": "31a89b8f-3cf1-81a6-97b8-cc8d83d2b4fe",
    "Smart Connected Service Management": "31a89b8f-3cf1-8153-b12a-d359ba4bcaee",
    "Computational Research": "34b89b8f-3cf1-816d-8dd1-c74f9262e185",
}

# ──────────────────────────────────────────────────────────────────────
# ALL RESOURCES — faculty-created instruction materials only
# ──────────────────────────────────────────────────────────────────────

RESOURCES = [

    # ══════════════════════════════════════════════════════════════════
    # ADAPTIVE LEADERSHIP — Fall 2024 (NEW items only)
    # ══════════════════════════════════════════════════════════════════
    {"title": "Reflection Rubric", "author": "", "type": "Tool", "semester": "Fall 2024", "course": "Adaptive Leadership"},
    {"title": "The Practice of Adaptive Leadership — Ch 2: The Theory Behind the Practice", "author": "Ronald Heifetz", "type": "Book", "semester": "Fall 2024", "course": "Adaptive Leadership"},
    {"title": "The Practice of Adaptive Leadership — Ch 4: Diagnose the System", "author": "Ronald Heifetz", "type": "Book", "semester": "Fall 2024", "course": "Adaptive Leadership"},
    {"title": "The Practice of Adaptive Leadership — Ch 5: Diagnose the Adaptive Challenge", "author": "Ronald Heifetz", "type": "Book", "semester": "Fall 2024", "course": "Adaptive Leadership"},
    {"title": "The Practice of Adaptive Leadership — Ch 6: Diagnose the Political Landscape", "author": "Ronald Heifetz", "type": "Book", "semester": "Fall 2024", "course": "Adaptive Leadership"},
    {"title": "The Practice of Adaptive Leadership — Ch 7: Qualities of An Adaptive Organization", "author": "Ronald Heifetz", "type": "Book", "semester": "Fall 2024", "course": "Adaptive Leadership"},
    {"title": "The Practice of Adaptive Leadership — Ch 8: Make Interpretations", "author": "Ronald Heifetz", "type": "Book", "semester": "Fall 2024", "course": "Adaptive Leadership"},
    {"title": "The Practice of Adaptive Leadership — Ch 10: Act Politically", "author": "Ronald Heifetz", "type": "Book", "semester": "Fall 2024", "course": "Adaptive Leadership"},
    {"title": "The Practice of Adaptive Leadership — Ch 13: See Yourself As a System", "author": "Ronald Heifetz", "type": "Book", "semester": "Fall 2024", "course": "Adaptive Leadership"},
    {"title": "The Practice of Adaptive Leadership — Ch 14: Identify Your Loyalties", "author": "Ronald Heifetz", "type": "Book", "semester": "Fall 2024", "course": "Adaptive Leadership"},
    {"title": "The Practice of Adaptive Leadership — Ch 15: Know Your Tuning", "author": "Ronald Heifetz", "type": "Book", "semester": "Fall 2024", "course": "Adaptive Leadership"},
    {"title": "The Practice of Adaptive Leadership — Ch 17: Understand Your Roles", "author": "Ronald Heifetz", "type": "Book", "semester": "Fall 2024", "course": "Adaptive Leadership"},
    {"title": "Weekly README Instructions — Week 3", "author": "", "type": "PDF", "semester": "Fall 2024", "course": "Adaptive Leadership"},

    # ══════════════════════════════════════════════════════════════════
    # PMUR — Fall 2024 (NEW items only)
    # ══════════════════════════════════════════════════════════════════
    {"title": "Observing the User Experience — Ch 9", "author": "Elizabeth Goodman", "type": "Book", "semester": "Fall 2024", "course": "PMUR"},
    {"title": "Observing the User Experience — Ch 10", "author": "Elizabeth Goodman", "type": "Book", "semester": "Fall 2024", "course": "PMUR"},
    {"title": "Observing the User Experience — Ch 11: Usability", "author": "Elizabeth Goodman", "type": "Book", "semester": "Fall 2024", "course": "PMUR"},
    {"title": "Observing the User Experience — Ch 4: Research Planning", "author": "Elizabeth Goodman", "type": "Book", "semester": "Fall 2024", "course": "PMUR"},
    {"title": "MARS Survey Instrument", "author": "", "type": "Tool", "semester": "Fall 2024", "course": "PMUR"},
    {"title": "Practical Ethnography: Private Sector Guide", "author": "", "type": "Book", "semester": "Fall 2024", "course": "PMUR"},
    {"title": "Qualitative Data Analysis — Ch 4 (Miles et al. 2013)", "author": "Miles, Huberman, Saldana", "type": "Book", "semester": "Fall 2024", "course": "PMUR"},

    # ══════════════════════════════════════════════════════════════════
    # STRATEGIC COMMUNICATION — Fall 2024 (NEW items only)
    # ══════════════════════════════════════════════════════════════════
    {"title": "Weekly README Instructions — W1", "author": "", "type": "PDF", "semester": "Fall 2024", "course": "Strategic Communication"},
    {"title": "Weekly README Instructions — W2", "author": "", "type": "PDF", "semester": "Fall 2024", "course": "Strategic Communication"},
    {"title": "Weekly README Instructions — W3", "author": "", "type": "PDF", "semester": "Fall 2024", "course": "Strategic Communication"},
    {"title": "Weekly README Instructions — W4", "author": "", "type": "PDF", "semester": "Fall 2024", "course": "Strategic Communication"},
    {"title": "Weekly README Instructions — W5", "author": "", "type": "PDF", "semester": "Fall 2024", "course": "Strategic Communication"},
    {"title": "Case Text: InterconnectedWorld", "author": "", "type": "Article", "semester": "Fall 2024", "course": "Strategic Communication"},
    {"title": "Case Text: KeepingHealthy", "author": "", "type": "Article", "semester": "Fall 2024", "course": "Strategic Communication"},
    {"title": "Case Text: Recovery", "author": "", "type": "Article", "semester": "Fall 2024", "course": "Strategic Communication"},
    {"title": "Techniques to Identify Themes (Ryan-Bernard 2003)", "author": "Gery Ryan, H. Russell Bernard", "type": "Paper", "semester": "Fall 2024", "course": "Strategic Communication"},
    {"title": "Client Brief: Chipotle", "author": "", "type": "PDF", "semester": "Fall 2024", "course": "Strategic Communication"},
    {"title": "Client Brief: Subway", "author": "", "type": "PDF", "semester": "Fall 2024", "course": "Strategic Communication"},
    {"title": "Client Brief: Whole Foods", "author": "", "type": "PDF", "semester": "Fall 2024", "course": "Strategic Communication"},
    {"title": "Subway Brand Guidelines", "author": "", "type": "PDF", "semester": "Fall 2024", "course": "Strategic Communication"},

    # ══════════════════════════════════════════════════════════════════
    # BEHAVIORAL DESIGN — Fall 2025 (NEW/updated items)
    # ══════════════════════════════════════════════════════════════════
    {"title": "Syllabus IDN542 — Fall 2025", "author": "", "type": "PDF", "semester": "Fall 2025", "course": "Behavioral Design"},
    {"title": "BD-01 Intro to Behavioral Design (Fall 2025)", "author": "", "type": "Slide Deck", "semester": "Fall 2025", "course": "Behavioral Design"},
    {"title": "BD-02 Cognitive Effort (Fall 2025)", "author": "", "type": "Slide Deck", "semester": "Fall 2025", "course": "Behavioral Design"},
    {"title": "BD-03 Uncertainty (Fall 2025)", "author": "", "type": "Slide Deck", "semester": "Fall 2025", "course": "Behavioral Design"},
    {"title": "BD-04 Action (Fall 2025)", "author": "", "type": "Slide Deck", "semester": "Fall 2025", "course": "Behavioral Design"},
    {"title": "BD-04 Literature Review (Fall 2025)", "author": "", "type": "Slide Deck", "semester": "Fall 2025", "course": "Behavioral Design"},
    {"title": "BD-05 COM-B MINDSPACE EAST (Fall 2025)", "author": "", "type": "Slide Deck", "semester": "Fall 2025", "course": "Behavioral Design"},
    {"title": "BD-05 Time + Social Norms (Fall 2025)", "author": "", "type": "Slide Deck", "semester": "Fall 2025", "course": "Behavioral Design"},
    {"title": "Choice Posture Architecture Infrastructure (Schmidt et al. 2022)", "author": "Schmidt et al.", "type": "Paper", "semester": "Fall 2025", "course": "Behavioral Design"},

    # ══════════════════════════════════════════════════════════════════
    # COMMUNICATION SYSTEMS / DATA VISUALIZATION — Fall 2024 (ALL NEW)
    # ══════════════════════════════════════════════════════════════════
    # Books (9)
    {"title": "All Data Are Local", "author": "Yanni Loukissas", "type": "Book", "semester": "Fall 2024", "course": "Communication Systems"},
    {"title": "Data Action", "author": "Sarah Williams", "type": "Book", "semester": "Fall 2024", "course": "Communication Systems"},
    {"title": "Data Feminism", "author": "Catherine D'Ignazio, Lauren Klein", "type": "Book", "semester": "Fall 2024", "course": "Communication Systems"},
    {"title": "Dear Data", "author": "Giorgia Lupi, Stefanie Posavec", "type": "Book", "semester": "Fall 2024", "course": "Communication Systems"},
    {"title": "How to Do Things with Videogames", "author": "Ian Bogost", "type": "Book", "semester": "Fall 2024", "course": "Communication Systems"},
    {"title": "Self-Tracking", "author": "Gina Neff, Dawn Nafus", "type": "Book", "semester": "Fall 2024", "course": "Communication Systems"},
    {"title": "The Nature of Data", "author": "", "type": "Book", "semester": "Fall 2024", "course": "Communication Systems"},
    {"title": "The Quantified Self", "author": "Deborah Lupton", "type": "Book", "semester": "Fall 2024", "course": "Communication Systems"},
    {"title": "Visual Information Communication", "author": "", "type": "Book", "semester": "Fall 2024", "course": "Communication Systems"},
    # Papers (11)
    {"title": "arXiv 1901.01920", "author": "", "type": "Paper", "semester": "Fall 2024", "course": "Communication Systems"},
    {"title": "Intentionality and Design in Data Sonification (2020)", "author": "", "type": "Paper", "semester": "Fall 2024", "course": "Communication Systems"},
    {"title": "Data Murals (Bhargava 2016)", "author": "Rahul Bhargava", "type": "Paper", "semester": "Fall 2024", "course": "Communication Systems"},
    {"title": "Why Model? (Epstein)", "author": "Joshua Epstein", "type": "Paper", "semester": "Fall 2024", "course": "Communication Systems"},
    {"title": "Everyone Wants to Do the Model Work, Not the Data Work", "author": "", "type": "Paper", "semester": "Fall 2024", "course": "Communication Systems"},
    {"title": "Gilman & Green", "author": "Nils Gilman, Michele Green", "type": "Paper", "semester": "Fall 2024", "course": "Communication Systems"},
    {"title": "Quantitative, Qualitative, and a Ruthless Criticism (Patel)", "author": "Patel", "type": "Paper", "semester": "Fall 2024", "course": "Communication Systems"},
    {"title": "The Psychology of Personal Data Donation", "author": "", "type": "Paper", "semester": "Fall 2024", "course": "Communication Systems"},
    {"title": "UNU-MACAU Data Marginalization Brochure", "author": "UNU-MACAU", "type": "Paper", "semester": "Fall 2024", "course": "Communication Systems"},
    {"title": "UNU-MACAU Data Marginalization Flyer", "author": "UNU-MACAU", "type": "Paper", "semester": "Fall 2024", "course": "Communication Systems"},
    {"title": "Creating Understanding of Data Literacy (Wolff)", "author": "Wolff", "type": "Paper", "semester": "Fall 2024", "course": "Communication Systems"},

    # ══════════════════════════════════════════════════════════════════
    # METRICS THAT MATTER — Fall 2024 (ALL NEW)
    # ══════════════════════════════════════════════════════════════════
    {"title": "Lecture Week 1: Introduction", "author": "", "type": "Slide Deck", "semester": "Fall 2024", "course": "Metrics that Matter"},
    {"title": "Lecture Week 2: Implementation", "author": "", "type": "Slide Deck", "semester": "Fall 2024", "course": "Metrics that Matter"},
    {"title": "Lecture Week 3: Organizational Measurement", "author": "", "type": "Slide Deck", "semester": "Fall 2024", "course": "Metrics that Matter"},
    {"title": "Lecture Week 4: Services and Social Sector", "author": "", "type": "Slide Deck", "semester": "Fall 2024", "course": "Metrics that Matter"},
    {"title": "Implementation Outcomes (Proctor)", "author": "Proctor", "type": "Paper", "semester": "Fall 2024", "course": "Metrics that Matter"},
    {"title": "Taxonomy of Implementation Outcomes", "author": "", "type": "Paper", "semester": "Fall 2024", "course": "Metrics that Matter"},

    # ══════════════════════════════════════════════════════════════════
    # FACILITATION METHODS — Spring 2025 (ALL NEW)
    # ══════════════════════════════════════════════════════════════════
    # Readings (5)
    {"title": "Dressler — Preface", "author": "Larry Dressler", "type": "Book", "semester": "Spring 2025", "course": "Facilitation Methods"},
    {"title": "Dressler — 6 Ways of Standing", "author": "Larry Dressler", "type": "Book", "semester": "Spring 2025", "course": "Facilitation Methods"},
    {"title": "Breaking Through (NYT)", "author": "", "type": "Article", "semester": "Spring 2025", "course": "Facilitation Methods"},
    {"title": "Moments of Impact — pp. 1-33", "author": "", "type": "Book", "semester": "Spring 2025", "course": "Facilitation Methods"},
    {"title": "Dressler — Know What You Stand For", "author": "Larry Dressler", "type": "Book", "semester": "Spring 2025", "course": "Facilitation Methods"},
    # Method handouts (5)
    {"title": "Method Handout: Assisters/Resisters", "author": "", "type": "Tool", "semester": "Spring 2025", "course": "Facilitation Methods"},
    {"title": "Method Handout: Word Dance", "author": "", "type": "Tool", "semester": "Spring 2025", "course": "Facilitation Methods"},
    {"title": "Method Handout: Storyboarding", "author": "", "type": "Tool", "semester": "Spring 2025", "course": "Facilitation Methods"},
    {"title": "Method Handout: Why / What's Stopping You", "author": "", "type": "Tool", "semester": "Spring 2025", "course": "Facilitation Methods"},
    {"title": "Method Handout: Data Questions", "author": "", "type": "Tool", "semester": "Spring 2025", "course": "Facilitation Methods"},

    # ══════════════════════════════════════════════════════════════════
    # ORG MODELS OF INNOVATION (IDN 535) — Spring 2025 (ALL NEW)
    # ══════════════════════════════════════════════════════════════════
    # W1
    {"title": "Design as Knowledge Agent (2003)", "author": "", "type": "Paper", "semester": "Spring 2025", "course": "Org Models of Innovation"},
    {"title": "Harvard/MIT Atlas of Economic Complexity", "author": "", "type": "Article", "semester": "Spring 2025", "course": "Org Models of Innovation"},
    # W2
    {"title": "Dynamic Capabilities and Strategic Management (Teece 1998)", "author": "David Teece", "type": "Paper", "semester": "Spring 2025", "course": "Org Models of Innovation"},
    {"title": "The Innovator's Hypothesis", "author": "", "type": "Book", "semester": "Spring 2025", "course": "Org Models of Innovation"},
    # W3
    {"title": "Using Data-Driven Crisis Analytics", "author": "", "type": "Article", "semester": "Spring 2025", "course": "Org Models of Innovation"},
    {"title": "Digital Transformation Changes How Companies Create Value", "author": "", "type": "Article", "semester": "Spring 2025", "course": "Org Models of Innovation"},
    # W4
    {"title": "To Innovate Like a Startup, Make Decisions Like VCs Do", "author": "", "type": "Article", "semester": "Spring 2025", "course": "Org Models of Innovation"},
    {"title": "Next Step in Impact Investing", "author": "", "type": "Article", "semester": "Spring 2025", "course": "Org Models of Innovation"},
    # W5
    {"title": "Put Purpose at the Core of Your Strategy", "author": "", "type": "Article", "semester": "Spring 2025", "course": "Org Models of Innovation"},
    {"title": "Harvard Growth Lab — Peace Corps", "author": "", "type": "Article", "semester": "Spring 2025", "course": "Org Models of Innovation"},
    # W6
    {"title": "Geography of Startups and Innovation Is Changing", "author": "", "type": "Article", "semester": "Spring 2025", "course": "Org Models of Innovation"},
    {"title": "Out of the Lab and Into the Frontline", "author": "", "type": "Article", "semester": "Spring 2025", "course": "Org Models of Innovation"},
    # Root
    {"title": "Design Research: Synergies from Interdisciplinary Perspectives (Zimmerman & Forlizzi)", "author": "John Zimmerman, Jodi Forlizzi", "type": "Paper", "semester": "Spring 2025", "course": "Org Models of Innovation"},
    {"title": "Strengthening the Philanthropic Supply Chain", "author": "", "type": "Paper", "semester": "Spring 2025", "course": "Org Models of Innovation"},

    # ══════════════════════════════════════════════════════════════════
    # MULTIDISCIPLINARY INNOVATION — Spring 2025 (ALL NEW)
    # ══════════════════════════════════════════════════════════════════
    {"title": "Lecture 1: MDI Introduction", "author": "", "type": "Slide Deck", "semester": "Spring 2025", "course": "Multidisciplinary Innovation"},
    {"title": "Lecture 2: Design-Led Innovation", "author": "", "type": "Slide Deck", "semester": "Spring 2025", "course": "Multidisciplinary Innovation"},
    {"title": "Lecture 3: Working in Teams + Problem Framing", "author": "", "type": "Slide Deck", "semester": "Spring 2025", "course": "Multidisciplinary Innovation"},
    {"title": "Guest Lecture: Pino — AI Intro MDP", "author": "Pino", "type": "Slide Deck", "semester": "Spring 2025", "course": "Multidisciplinary Innovation"},
    {"title": "Steelcase 3D AI Thought Starter", "author": "Steelcase", "type": "Article", "semester": "Spring 2025", "course": "Multidisciplinary Innovation"},
    {"title": "Team Canvas Template", "author": "", "type": "Tool", "semester": "Spring 2025", "course": "Multidisciplinary Innovation"},
    {"title": "Framework Era Map", "author": "", "type": "Tool", "semester": "Spring 2025", "course": "Multidisciplinary Innovation"},

    # ══════════════════════════════════════════════════════════════════
    # SMART CONNECTED SERVICE MANAGEMENT — Spring 2023 (ALL NEW)
    # ══════════════════════════════════════════════════════════════════
    # Week 1 — Required Readings
    {"title": "Platforms and Ecosystems (Cain)", "author": "Cain", "type": "Paper", "semester": "Spring 2023", "course": "Smart Connected Service Management"},
    {"title": "Three Models of Strategy (Chaffee)", "author": "Chaffee", "type": "Paper", "semester": "Spring 2023", "course": "Smart Connected Service Management"},
    {"title": "Pipelines, Platforms, and the New Rules of Strategy", "author": "", "type": "Paper", "semester": "Spring 2023", "course": "Smart Connected Service Management"},
    {"title": "How Smart, Connected Products Are Transforming Competition (Porter)", "author": "Michael Porter", "type": "Paper", "semester": "Spring 2023", "course": "Smart Connected Service Management"},
    # Week 1 — Supplemental Readings
    {"title": "Internet Business Models — Chapter 6 (Afuah-Tucci)", "author": "Allan Afuah, Christopher Tucci", "type": "Book", "semester": "Spring 2023", "course": "Smart Connected Service Management"},
    {"title": "Forrester's Digital Maturity Model 4.0", "author": "Forrester", "type": "Paper", "semester": "Spring 2023", "course": "Smart Connected Service Management"},
    # Week 1 — Exercise
    {"title": "Creating Concept Maps (Dubberly)", "author": "Hugh Dubberly", "type": "Tool", "semester": "Spring 2023", "course": "Smart Connected Service Management"},
    {"title": "Exercise: Mapping Strategic Context", "author": "", "type": "Tool", "semester": "Spring 2023", "course": "Smart Connected Service Management"},
    {"title": "Learning How to Learn (Novak & Gowin)", "author": "Joseph Novak, D. Bob Gowin", "type": "Book", "semester": "Spring 2023", "course": "Smart Connected Service Management"},
    # Week 1 — Presentation
    {"title": "Spring 2023 Kickoff Deck", "author": "", "type": "Slide Deck", "semester": "Spring 2023", "course": "Smart Connected Service Management"},

    # Week 2 — Required Readings
    {"title": "Amazon Alexa Will Take Over Your Home (The Atlantic)", "author": "", "type": "Article", "semester": "Spring 2023", "course": "Smart Connected Service Management"},
    {"title": "When Your Boss Is an Algorithm (Financial Times)", "author": "", "type": "Article", "semester": "Spring 2023", "course": "Smart Connected Service Management"},
    {"title": "The Platform Delusion (Knee)", "author": "Knee", "type": "Book", "semester": "Spring 2023", "course": "Smart Connected Service Management"},
    # Week 2 — Supplemental Readings
    {"title": "How Generative AI Systems Will Reconfigure the Made World (Kuniavsky)", "author": "Mike Kuniavsky", "type": "Paper", "semester": "Spring 2023", "course": "Smart Connected Service Management"},
    {"title": "Pressed for Time — Ch 7 (Wajcman)", "author": "Judy Wajcman", "type": "Book", "semester": "Spring 2023", "course": "Smart Connected Service Management"},
    {"title": "Pressed for Time — Introduction (Wajcman)", "author": "Judy Wajcman", "type": "Book", "semester": "Spring 2023", "course": "Smart Connected Service Management"},
    # Week 2 — Presentation
    {"title": "Week 2 Presentation", "author": "", "type": "Slide Deck", "semester": "Spring 2023", "course": "Smart Connected Service Management"},

    # Week 3 — Required Readings
    {"title": "The Nature of Technology — Ch 1, 2, 6 (Arthur)", "author": "W. Brian Arthur", "type": "Book", "semester": "Spring 2023", "course": "Smart Connected Service Management"},
    {"title": "Technics and Civilization — Intro and Ch 1 (Mumford)", "author": "Lewis Mumford", "type": "Book", "semester": "Spring 2023", "course": "Smart Connected Service Management"},
    {"title": "What Is Technology? Six Definitions (Nightingale)", "author": "Nightingale", "type": "Paper", "semester": "Spring 2023", "course": "Smart Connected Service Management"},
    # Week 3 — Supplemental Readings
    {"title": "AI Knowledge Map: How to Classify AI Technologies (Corea)", "author": "Francesco Corea", "type": "Article", "semester": "Spring 2023", "course": "Smart Connected Service Management"},
    {"title": "Data Factories (Stratechery)", "author": "", "type": "Article", "semester": "Spring 2023", "course": "Smart Connected Service Management"},
    {"title": "Affordances (Gibson)", "author": "James J. Gibson", "type": "Paper", "semester": "Spring 2023", "course": "Smart Connected Service Management"},
    {"title": "The Evolution of Large Technological Systems (Hughes)", "author": "Thomas Hughes", "type": "Paper", "semester": "Spring 2023", "course": "Smart Connected Service Management"},
    {"title": "Models Will Run the World (WSJ)", "author": "", "type": "Article", "semester": "Spring 2023", "course": "Smart Connected Service Management"},
    # Week 3 — Exercise
    {"title": "Exercise: Product Teardown", "author": "", "type": "Tool", "semester": "Spring 2023", "course": "Smart Connected Service Management"},
    # Week 3 — Presentation
    {"title": "Week 3 Presentation", "author": "", "type": "Slide Deck", "semester": "Spring 2023", "course": "Smart Connected Service Management"},

    # Week 4 — Required Readings
    {"title": "Women and the Assessment of Technology (Bush)", "author": "Corlann Gee Bush", "type": "Paper", "semester": "Spring 2023", "course": "Smart Connected Service Management"},
    {"title": "Hertzian Tales — Ch 2 (Dunne)", "author": "Anthony Dunne", "type": "Book", "semester": "Spring 2023", "course": "Smart Connected Service Management"},
    {"title": "Hertzian Tales — Ch 1 (Dunne)", "author": "Anthony Dunne", "type": "Book", "semester": "Spring 2023", "course": "Smart Connected Service Management"},
    {"title": "Do Artifacts Have Politics? (Winner)", "author": "Langdon Winner", "type": "Paper", "semester": "Spring 2023", "course": "Smart Connected Service Management"},
    # Week 4 — Supplemental Readings
    {"title": "Feminist HCI (Bardzell)", "author": "Shaowen Bardzell", "type": "Paper", "semester": "Spring 2023", "course": "Smart Connected Service Management"},

    # Week 5 — Required Readings
    {"title": "Second-Generation Design Methods (Rittel 1984)", "author": "Horst Rittel", "type": "Paper", "semester": "Spring 2023", "course": "Smart Connected Service Management"},
    {"title": "Summary of Lynch's Mapping Method", "author": "", "type": "Paper", "semester": "Spring 2023", "course": "Smart Connected Service Management"},
    {"title": "Review of Ashby (Umpleby)", "author": "Stuart Umpleby", "type": "Paper", "semester": "Spring 2023", "course": "Smart Connected Service Management"},
    # Week 5 — Supplemental Readings
    {"title": "Machine Learning for Designers (Hebron)", "author": "Patrick Hebron", "type": "Book", "semester": "Spring 2023", "course": "Smart Connected Service Management"},
    {"title": "How to Build an IoT Product Roadmap (IoT For All)", "author": "", "type": "Article", "semester": "Spring 2023", "course": "Smart Connected Service Management"},
    {"title": "IoT Product Managers Guide to the IoT Technology Stack (IoT For All)", "author": "", "type": "Article", "semester": "Spring 2023", "course": "Smart Connected Service Management"},
    {"title": "Good City Form (Lynch)", "author": "Kevin Lynch", "type": "Book", "semester": "Spring 2023", "course": "Smart Connected Service Management"},
    {"title": "The Death of Nature — Selections (Merchant)", "author": "Carolyn Merchant", "type": "Book", "semester": "Spring 2023", "course": "Smart Connected Service Management"},
    # Week 5 — Exercise
    {"title": "Exercise: The Ledger", "author": "", "type": "Tool", "semester": "Spring 2023", "course": "Smart Connected Service Management"},

    # Week 6 — Required Readings
    {"title": "Social Constructionism (Burr)", "author": "Vivien Burr", "type": "Book", "semester": "Spring 2023", "course": "Smart Connected Service Management"},
    {"title": "Dilemmas in a General Theory of Planning (Rittel)", "author": "Horst Rittel, Melvin Webber", "type": "Paper", "semester": "Spring 2023", "course": "Smart Connected Service Management"},
    {"title": "Plans and Situated Actions (Suchman)", "author": "Lucy Suchman", "type": "Book", "semester": "Spring 2023", "course": "Smart Connected Service Management"},
    # Week 6 — Supplemental Readings
    {"title": "Design as Participation", "author": "", "type": "Paper", "semester": "Spring 2023", "course": "Smart Connected Service Management"},
    {"title": "Exploring Design Tradeoffs for HCD (Fischer)", "author": "Gerhard Fischer", "type": "Paper", "semester": "Spring 2023", "course": "Smart Connected Service Management"},
    {"title": "Alternative Design (Nieusma)", "author": "Dean Nieusma", "type": "Paper", "semester": "Spring 2023", "course": "Smart Connected Service Management"},
    {"title": "Agencies in Technology Design (Suchman)", "author": "Lucy Suchman", "type": "Paper", "semester": "Spring 2023", "course": "Smart Connected Service Management"},
    {"title": "Anthropological Relocations and the Limits of Design (Suchman)", "author": "Lucy Suchman", "type": "Paper", "semester": "Spring 2023", "course": "Smart Connected Service Management"},
    {"title": "Reflective Design (Sengers et al.)", "author": "Phoebe Sengers, Kirsten Boehner, Shay David, Joseph Kaye", "type": "Paper", "semester": "Spring 2023", "course": "Smart Connected Service Management"},
    # Week 6 — Exercise
    {"title": "Exercise: Social Life of Things", "author": "", "type": "Tool", "semester": "Spring 2023", "course": "Smart Connected Service Management"},

    # Week 7 — Method cards
    {"title": "Method Cards", "author": "", "type": "Tool", "semester": "Spring 2023", "course": "Smart Connected Service Management"},
    {"title": "eLab Methods", "author": "", "type": "Tool", "semester": "Spring 2023", "course": "Smart Connected Service Management"},

    # ══════════════════════════════════════════════════════════════════
    # COMPUTATIONAL RESEARCH — Spring 2025 (ALL NEW)
    # ══════════════════════════════════════════════════════════════════
    # Books (15)
    {"title": "The Disability Studies Reader", "author": "Lennard Davis", "type": "Book", "semester": "Spring 2025", "course": "Computational Research"},
    {"title": "Big Data, Little Data, No Data", "author": "Christine Borgman", "type": "Book", "semester": "Spring 2025", "course": "Computational Research"},
    {"title": "Doing Digital Methods", "author": "Richard Rogers", "type": "Book", "semester": "Spring 2025", "course": "Computational Research"},
    {"title": "The End of Average", "author": "Todd Rose", "type": "Book", "semester": "Spring 2025", "course": "Computational Research"},
    {"title": "Simulation and Its Discontents", "author": "Sherry Turkle", "type": "Book", "semester": "Spring 2025", "course": "Computational Research"},
    {"title": "The Signal and the Noise", "author": "Nate Silver", "type": "Book", "semester": "Spring 2025", "course": "Computational Research"},
    {"title": "Grokking Algorithms", "author": "Aditya Bhargava", "type": "Book", "semester": "Spring 2025", "course": "Computational Research"},
    {"title": "The Seductions of Quantification", "author": "Sally Engle Merry", "type": "Book", "semester": "Spring 2025", "course": "Computational Research"},
    {"title": "Algorithms (MIT Press Essential Knowledge)", "author": "Panos Louridas", "type": "Book", "semester": "Spring 2025", "course": "Computational Research"},
    {"title": "Ghost Stories for Darwin", "author": "Banu Subramaniam", "type": "Book", "semester": "Spring 2025", "course": "Computational Research"},
    {"title": "Statistics in a Nutshell (O'Reilly)", "author": "", "type": "Book", "semester": "Spring 2025", "course": "Computational Research"},
    {"title": "Data Science (MIT Press Essential Knowledge)", "author": "John Kelleher, Brendan Tierney", "type": "Book", "semester": "Spring 2025", "course": "Computational Research"},
    {"title": "The Nature of Data", "author": "", "type": "Book", "semester": "Spring 2025", "course": "Computational Research"},
    {"title": "Building SimCity", "author": "Chaim Gingold", "type": "Book", "semester": "Spring 2025", "course": "Computational Research"},
    {"title": "Human-Centered Data Science", "author": "Cecilia Aragon, Shion Guha, Marina Kogan, Michael Muller, Gina Neff", "type": "Book", "semester": "Spring 2025", "course": "Computational Research"},
    # Papers (7)
    {"title": "MAST: User Behavior Pattern Analysis", "author": "", "type": "Paper", "semester": "Spring 2025", "course": "Computational Research"},
    {"title": "Sensors Journal Paper", "author": "", "type": "Paper", "semester": "Spring 2025", "course": "Computational Research"},
    {"title": "spider.pdf", "author": "", "type": "Paper", "semester": "Spring 2025", "course": "Computational Research"},
    {"title": "Computational Literature Reviews (Antons et al. 2021)", "author": "Antons et al.", "type": "Paper", "semester": "Spring 2025", "course": "Computational Research"},
    {"title": "Corporate Foresight to Future-Making (Wenzel 2022)", "author": "Wenzel", "type": "Paper", "semester": "Spring 2025", "course": "Computational Research"},
    {"title": "Predictive or Imaginative Futures (Durante et al. 2024)", "author": "Durante et al.", "type": "Paper", "semester": "Spring 2025", "course": "Computational Research"},
    {"title": "journal.pmed.1003583", "author": "", "type": "Paper", "semester": "Spring 2025", "course": "Computational Research"},
]


def create_resource(r):
    """Create a single resource page in the Notion Resources DB."""
    course_id = COURSES.get(r["course"])
    properties = {
        "Title": {
            "title": [{"text": {"content": r["title"]}}]
        },
        "Type": {
            "select": {"name": r["type"]}
        },
        "Semester": {
            "select": {"name": r["semester"]}
        },
    }
    if r.get("author"):
        properties["Author(s)"] = {
            "rich_text": [{"text": {"content": r["author"]}}]
        }
    if course_id:
        properties["Courses"] = {
            "relation": [{"id": course_id}]
        }

    payload = {
        "parent": {"database_id": RESOURCES_DB},
        "properties": properties,
    }
    data = json.dumps(payload).encode("utf-8")
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
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  ERROR {e.code}: {body}", flush=True)
        return None


def main():
    total = len(RESOURCES)
    print(f"Seeding {total} resources into Notion...\n", flush=True)

    success = 0
    fail = 0
    by_course = {}

    for i, r in enumerate(RESOURCES, 1):
        label = f"[{i}/{total}]"
        print(f"{label} {r['course']} — {r['title']}", flush=True)

        result = create_resource(r)
        if result and "id" in result:
            success += 1
            by_course[r["course"]] = by_course.get(r["course"], 0) + 1
            print(f"  OK  {result['id']}", flush=True)
        else:
            fail += 1
            print(f"  FAILED", flush=True)

        time.sleep(0.35)

    print(f"\n{'='*60}", flush=True)
    print(f"DONE: {success} created, {fail} failed, {total} total", flush=True)
    print(f"\nBy course:", flush=True)
    for course, count in sorted(by_course.items()):
        print(f"  {course}: {count}", flush=True)


if __name__ == "__main__":
    main()
