# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
# from reportlab.lib.styles import getSampleStyleSheet
# from pathlib import Path
# import uuid
# import json

# REPORT_DIR = Path("reports")
# REPORT_DIR.mkdir(exist_ok=True)


# def generate_pdf(report_dict: dict) -> str:

#     file_id = str(uuid.uuid4())
#     path = REPORT_DIR / f"{file_id}.pdf"

#     doc = SimpleDocTemplate(str(path))
#     styles = getSampleStyleSheet()
#     elements = []

#     def section(title):
#         elements.append(Paragraph(f"<b>{title}</b>", styles["Heading2"]))
#         elements.append(Spacer(1, 10))

#     def text(content):
#         elements.append(Paragraph(content.replace("\n", "<br/>"), styles["Normal"]))
#         elements.append(Spacer(1, 10))

#     # Candidate info
#     section("Candidate Information")
#     text(f"Name: {report_dict['candidate_name']}")
#     text(f"Job Title: {report_dict['job_title']}")

#     # Scores
#     section("AI Match Scores")

#     scores = report_dict["scores"]

#     text(f"Final Match Score: {scores['final_weighted_score']}%")
#     text(f"Skill Score: {scores['skill_score']}%")
#     text(f"Responsibility Score: {scores['responsibility_score']}%")
#     text(f"Qualification Score: {scores['qualification_score']}%")
#     text(f"Tech Proof Score: {scores['tech_proof_score']}%")

#     # Skills
#     section("Skills Analysis")

#     skills = report_dict["skills"]

#     text("JD Skills:\n" + "\n".join(skills["jd_skills"]))
#     text("Resume Skills:\n" + "\n".join(skills["resume_skills"]))
#     text("Matched Skills:\n" + "\n".join(skills["matched"]))
#     text("Missing Skills:\n" + "\n".join(skills["missing"]))

#     # Responsibilities
#     section("Responsibility Analysis")

#     resp = report_dict["responsibilities"]

#     text("Matched Responsibilities:\n" + "\n".join(resp["matched"]))
#     text("Missing Responsibilities:\n" + "\n".join(resp["missing"]))

#     # Qualifications
#     section("Qualification Analysis")

#     qual = report_dict["qualifications"]

#     text("Matched Qualifications:\n" + "\n".join(qual["matched"]))
#     text("Missing Qualifications:\n" + "\n".join(qual["missing"]))

#     # Education
#     section("Education")

#     for edu in report_dict["education"]:
#         text(f"{edu['degree']} — {edu['institution']} ({edu['duration']})")

#     # Experience
#     section("Experience")

#     for exp in report_dict["experience"]:
#         text(f"{exp['role']} at {exp['organization']} ({exp['duration']})")
#         text("\n".join(exp["responsibilities"]))

#     # Projects
#     section("Projects")

#     for proj in report_dict["projects"]:
#         text(f"{proj['title']}")
#         text("Tech Stack: " + ", ".join(proj["tech_stack"]))
#         text(proj["description"])

#     doc.build(elements)

#     return str(path)

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from pathlib import Path
import uuid

REPORT_DIR = Path("reports")
REPORT_DIR.mkdir(exist_ok=True)


def generate_pdf(report_dict: dict):

    file_id = str(uuid.uuid4())
    path = REPORT_DIR / f"{file_id}.pdf"

    styles = getSampleStyleSheet()

    elements = []

    # -------- TITLE --------

    elements.append(Paragraph("<b>AI Resume Analysis Report</b>", styles["Title"]))
    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph(
            f"<b>Candidate:</b> {report_dict['candidate_name']}<br/>"
            f"<b>Job Role:</b> {report_dict['job_title']}",
            styles["Normal"],
        )
    )

    elements.append(Spacer(1, 20))

    # -------- SCORE TABLE --------

    scores = report_dict["scores"]

    score_data = [
        ["Metric", "Score"],
        ["Final Match Score", f"{scores['final_weighted_score']}%"],
        ["Skill Score", f"{scores['skill_score']}%"],
        ["Responsibility Score", f"{scores['responsibility_score']}%"],
        ["Qualification Score", f"{scores['qualification_score']}%"],
        ["Tech Proof Score", f"{scores['tech_proof_score']}%"],
    ]

    table = Table(score_data, colWidths=[250, 120])

    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ]
        )
    )

    elements.append(Paragraph("<b>Score Breakdown</b>", styles["Heading2"]))
    elements.append(Spacer(1, 10))
    elements.append(table)

    elements.append(Spacer(1, 20))

    # -------- SKILL ANALYSIS --------

    skills = report_dict["skills"]

    skill_data = [["Matched Skills", "Missing Skills"]]

    max_len = max(len(skills["matched"]), len(skills["missing"]))

    for i in range(max_len):

        matched = skills["matched"][i] if i < len(skills["matched"]) else ""
        missing = skills["missing"][i] if i < len(skills["missing"]) else ""

        skill_data.append([matched, missing])

    skill_table = Table(skill_data, colWidths=[250, 250])

    skill_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ]
        )
    )

    elements.append(Paragraph("<b>Skill Analysis</b>", styles["Heading2"]))
    elements.append(Spacer(1, 10))
    elements.append(skill_table)

    elements.append(Spacer(1, 20))

    # -------- RESPONSIBILITIES --------

    resp = report_dict["responsibilities"]

    resp_data = [["Matched Responsibilities", "Missing Responsibilities"]]

    max_len = max(len(resp["matched"]), len(resp["missing"]))

    for i in range(max_len):

        matched = resp["matched"][i] if i < len(resp["matched"]) else ""
        missing = resp["missing"][i] if i < len(resp["missing"]) else ""

        resp_data.append([matched, missing])

    resp_table = Table(resp_data, colWidths=[250, 250])

    resp_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ]
        )
    )

    elements.append(Paragraph("<b>Responsibility Analysis</b>", styles["Heading2"]))
    elements.append(Spacer(1, 10))
    elements.append(resp_table)

    elements.append(Spacer(1, 20))

    # -------- QUALIFICATIONS --------

    qual = report_dict["qualifications"]

    qual_data = [["Matched Qualifications", "Missing Qualifications"]]

    max_len = max(len(qual["matched"]), len(qual["missing"]))

    for i in range(max_len):

        matched = qual["matched"][i] if i < len(qual["matched"]) else ""
        missing = qual["missing"][i] if i < len(qual["missing"]) else ""

        qual_data.append([matched, missing])

    qual_table = Table(qual_data, colWidths=[250, 250])

    qual_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ]
        )
    )

    elements.append(Paragraph("<b>Qualification Analysis</b>", styles["Heading2"]))
    elements.append(Spacer(1, 10))
    elements.append(qual_table)

    elements.append(Spacer(1, 20))

    # -------- EXPERIENCE --------

    elements.append(Paragraph("<b>Experience</b>", styles["Heading2"]))
    elements.append(Spacer(1, 10))

    for exp in report_dict["experience"]:

        elements.append(
            Paragraph(
                f"<b>{exp['role']}</b> — {exp['organization']} ({exp['duration']})",
                styles["Normal"],
            )
        )

        for r in exp["responsibilities"]:
            elements.append(Paragraph(f"- {r}", styles["Normal"]))

        elements.append(Spacer(1, 10))

    # -------- PROJECTS --------

    elements.append(Paragraph("<b>Projects</b>", styles["Heading2"]))
    elements.append(Spacer(1, 10))

    for proj in report_dict["projects"]:

        elements.append(Paragraph(f"<b>{proj['title']}</b>", styles["Normal"]))
        elements.append(Paragraph(f"Tech Stack: {', '.join(proj['tech_stack'])}", styles["Normal"]))
        elements.append(Paragraph(proj["description"], styles["Normal"]))
        elements.append(Spacer(1, 10))

    doc = SimpleDocTemplate(str(path))
    doc.build(elements)

    return str(path)
