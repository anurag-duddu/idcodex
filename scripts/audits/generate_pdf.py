#!/usr/bin/env python3
"""
Generate a styled PDF of the Resource Coverage Gap Analysis from audit_results.json.
Uses fpdf2 (pure Python, no system dependencies).
"""

import json
from fpdf import FPDF

INPUT = "/Users/idstuart/Projects/idcodex/data/audit_results.json"
OUTPUT = "/Users/idstuart/Projects/idcodex/reports/RESOURCE-GAPS.pdf"

# IIT brand colors
RED = (204, 0, 0)
DARK = (40, 40, 40)
GRAY = (100, 100, 100)
LIGHT_BG = (248, 248, 248)
WHITE = (255, 255, 255)
TABLE_BORDER = (200, 200, 200)

# Grade colors
GRADE_COLORS = {
    "F": (204, 0, 0),
    "C": (220, 120, 0),
    "B": (180, 160, 0),
    "A": (0, 140, 60),
}


def safe(text):
    """Replace Unicode chars that Helvetica can't render."""
    return str(text).replace("\u2014", "-").replace("\u2013", "-").replace("\u2018", "'").replace("\u2019", "'").replace("\u201c", '"').replace("\u201d", '"').replace("\u2265", ">=").replace("\u2264", "<=")


class ReportPDF(FPDF):
    def header(self):
        if self.page_no() == 1:
            return  # custom first page header
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(*GRAY)
        self.cell(0, 5, "ID Codex - Resource Coverage Gap Analysis", align="L")
        self.ln(8)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "", 7)
        self.set_text_color(*GRAY)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def section_title(self, text, color=DARK):
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(*color)
        self.cell(0, 8, safe(text))
        self.ln(8)
        # underline
        self.set_draw_color(*TABLE_BORDER)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(3)

    def subtitle(self, text):
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*GRAY)
        self.multi_cell(0, 4.5, safe(text))
        self.ln(2)

    def draw_table(self, headers, col_widths, rows, highlight_col=None):
        # Header row
        self.set_font("Helvetica", "B", 7.5)
        self.set_fill_color(*RED)
        self.set_text_color(*WHITE)
        self.set_draw_color(*RED)
        for i, (h, w) in enumerate(zip(headers, col_widths)):
            self.cell(w, 6, safe(h), border=1, fill=True, align="C")
        self.ln()

        # Data rows
        self.set_font("Helvetica", "", 7)
        self.set_draw_color(*TABLE_BORDER)
        for row_idx, row in enumerate(rows):
            # Check if we need a new page (leave room for at least one row + footer)
            if self.get_y() + 5.5 > self.h - 18:
                self.add_page()
                # Re-draw header
                self.set_font("Helvetica", "B", 7.5)
                self.set_fill_color(*RED)
                self.set_text_color(*WHITE)
                self.set_draw_color(*RED)
                for i, (h, w) in enumerate(zip(headers, col_widths)):
                    self.cell(w, 6, safe(h), border=1, fill=True, align="C")
                self.ln()
                self.set_font("Helvetica", "", 7)
                self.set_draw_color(*TABLE_BORDER)

            # Alternating row background
            if row_idx % 2 == 0:
                self.set_fill_color(*WHITE)
            else:
                self.set_fill_color(*LIGHT_BG)

            for i, (val, w) in enumerate(zip(row, col_widths)):
                self.set_text_color(*DARK)
                # Color the grade column
                if highlight_col is not None and i == highlight_col:
                    grade = str(val).strip()
                    if grade in GRADE_COLORS:
                        self.set_text_color(*GRADE_COLORS[grade])
                        self.set_font("Helvetica", "B", 7)

                align = "C" if i == 0 or w <= 12 else "L"
                # Truncate long text to fit column
                text = safe(val)
                self.cell(w, 5.2, text, border="B", fill=True, align=align)
                self.set_font("Helvetica", "", 7)
            self.ln()


def main():
    with open(INPUT) as f:
        data = json.load(f)

    results = data["results"]
    total_courses = data["total_courses"]
    total_resources = data["total_resources"]
    orphan_count = data["orphan_count"]
    grade_counts = data["grade_counts"]

    pdf = ReportPDF(orientation="L", unit="mm", format="letter")
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # ── Title page / header ───────────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 24)
    pdf.set_text_color(*RED)
    pdf.cell(0, 12, "ID Codex", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 16)
    pdf.set_text_color(*DARK)
    pdf.cell(0, 8, "Resource Coverage Gap Analysis", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    # Metadata line
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(*GRAY)
    pdf.cell(0, 5, safe(f"Generated: {data['generated'][:16]}   |   {total_courses} courses   |   {total_resources} resources   |   {orphan_count} orphans"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # ── Summary box ───────────────────────────────────────────────────────────
    pdf.section_title("Summary")
    summary_headers = ["Grade", "Meaning", "Count"]
    summary_widths = [20, 80, 20]
    summary_rows = [
        ("F", "No resources at all", str(grade_counts.get("F", 0))),
        ("C", "Minimal (1-49% of target)", str(grade_counts.get("C", 0))),
        ("B", "Partial (50-99% of target)", str(grade_counts.get("B", 0))),
        ("A", "Full coverage (100%+ of target)", str(grade_counts.get("A", 0))),
    ]
    pdf.draw_table(summary_headers, summary_widths, summary_rows, highlight_col=0)
    pdf.ln(3)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(*GRAY)
    pdf.cell(0, 4, "Targets: Workshop/Studio = 14 resources (14 weeks), Seminar = 7 resources (7 weeks)", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    # ── Separate results by grade ─────────────────────────────────────────────
    active = [r for r in results if r["status"] != "Merged"]
    f_courses = [r for r in active if r["grade"] == "F"]
    c_courses = [r for r in active if r["grade"] == "C"]
    b_courses = [r for r in active if r["grade"] == "B"]
    a_courses = [r for r in active if r["grade"] == "A"]

    # ── Grade F ───────────────────────────────────────────────────────────────
    if f_courses:
        pdf.section_title(f"Grade F — No Resources ({len(f_courses)} courses)", RED)
        pdf.subtitle("These courses have zero resources. Any contribution helps. Priority: CRITICAL")

        headers = ["#", "Course", "Number", "Type", "Status", "Category", "Target"]
        widths = [8, 90, 22, 22, 18, 28, 16]
        rows = []
        for i, r in enumerate(f_courses, 1):
            rows.append((
                str(i),
                r["name"][:52],
                r["number"] or "—",
                r["type"],
                r["status"],
                r["category"],
                str(r["target"]),
            ))
        pdf.draw_table(headers, widths, rows)
        pdf.ln(6)

    # ── Grade C ───────────────────────────────────────────────────────────────
    if c_courses:
        pdf.add_page()
        pdf.section_title(f"Grade C — Minimal Coverage ({len(c_courses)} courses)", (220, 120, 0))
        pdf.subtitle("These courses have some resources but are well below target. Priority: HIGH")

        headers = ["#", "Course", "Number", "Type", "Status", "Have", "Target", "Gap", "%", "Breakdown"]
        widths = [8, 70, 20, 20, 16, 14, 14, 12, 12, 68]
        rows = []
        for i, r in enumerate(c_courses, 1):
            bd = r.get("type_breakdown", {})
            breakdown = ", ".join(f"{v} {k}" for k, v in sorted(bd.items(), key=lambda x: -x[1]))
            rows.append((
                str(i), r["name"][:40], r["number"] or "—", r["type"],
                r["status"], str(r["count"]), str(r["target"]),
                str(r["gap"]), f"{r['pct']}%", breakdown[:38],
            ))
        pdf.draw_table(headers, widths, rows)
        pdf.ln(6)

    # ── Grade B ───────────────────────────────────────────────────────────────
    if b_courses:
        pdf.section_title(f"Grade B — Partial Coverage ({len(b_courses)} courses)", (180, 160, 0))
        pdf.subtitle("These courses are making progress but still have gaps. Priority: MEDIUM")

        headers = ["#", "Course", "Number", "Type", "Status", "Have", "Target", "Gap", "%", "Breakdown"]
        widths = [8, 70, 20, 20, 16, 14, 14, 12, 12, 68]
        rows = []
        for i, r in enumerate(b_courses, 1):
            bd = r.get("type_breakdown", {})
            breakdown = ", ".join(f"{v} {k}" for k, v in sorted(bd.items(), key=lambda x: -x[1]))
            rows.append((
                str(i), r["name"][:40], r["number"] or "—", r["type"],
                r["status"], str(r["count"]), str(r["target"]),
                str(r["gap"]), f"{r['pct']}%", breakdown[:38],
            ))
        pdf.draw_table(headers, widths, rows)
        pdf.ln(6)

    # ── Grade A ───────────────────────────────────────────────────────────────
    if a_courses:
        pdf.add_page()
        pdf.section_title(f"Grade A — Full Coverage ({len(a_courses)} courses)", (0, 140, 60))
        pdf.subtitle("These courses meet or exceed the target.")

        headers = ["#", "Course", "Number", "Type", "Status", "Have", "Target", "%", "Breakdown"]
        widths = [8, 78, 22, 20, 16, 14, 14, 14, 68]
        rows = []
        for i, r in enumerate(a_courses, 1):
            bd = r.get("type_breakdown", {})
            breakdown = ", ".join(f"{v} {k}" for k, v in sorted(bd.items(), key=lambda x: -x[1]))
            rows.append((
                str(i), r["name"][:46], r["number"] or "—", r["type"],
                r["status"], str(r["count"]), str(r["target"]),
                f"{r['pct']}%", breakdown[:38],
            ))
        pdf.draw_table(headers, widths, rows)
        pdf.ln(6)

    # ── How to Contribute ─────────────────────────────────────────────────────
    pdf.add_page()
    pdf.section_title("How to Contribute")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*DARK)
    pdf.ln(2)
    pdf.multi_cell(0, 5.5,
        "If you have materials (syllabi, lecture slides, readings, project briefs, videos) "
        "for any course listed in this report, here's how you can help:")
    pdf.ln(4)

    steps = [
        ("1.", "Check the Grade column", "F and C courses are the highest priority - any material helps."),
        ("2.", "Share your files", "Google Drive, Dropbox, or email to the ID Codex admin."),
        ("3.", "Include context", "Course name + semester you took it (e.g., 'PMUR, Fall 2024')."),
        ("4.", "Any format works", "PDF, PPTX, DOCX, links, videos - we'll organize it."),
    ]
    for num, title, desc in steps:
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(*RED)
        pdf.cell(8, 6, safe(num))
        pdf.set_text_color(*DARK)
        pdf.cell(50, 6, safe(title))
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(*GRAY)
        pdf.cell(0, 6, safe(desc), new_x="LMARGIN", new_y="NEXT")

    pdf.ln(8)
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(*GRAY)
    pdf.cell(0, 6, "Every contribution helps preserve ID's collective knowledge for future students.", new_x="LMARGIN", new_y="NEXT")

    # ── Save ──────────────────────────────────────────────────────────────────
    pdf.output(OUTPUT)
    print(f"PDF written to {OUTPUT}")


if __name__ == "__main__":
    main()
