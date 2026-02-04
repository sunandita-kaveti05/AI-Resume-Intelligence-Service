# pdf_report.py
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from pathlib import Path
import uuid

REPORT_DIR = Path("reports")
REPORT_DIR.mkdir(exist_ok=True)

def generate_pdf(report_dict: dict) -> str:
    file_id = str(uuid.uuid4())
    path = REPORT_DIR / f"{file_id}.pdf"

    doc = SimpleDocTemplate(str(path))
    styles = getSampleStyleSheet()
    elements = []

    def add(title, content):
        elements.append(Paragraph(f"<b>{title}</b>", styles['Heading2']))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(content.replace("\n", "<br/>"), styles['Normal']))
        elements.append(Spacer(1, 20))

    add("Candidate", report_dict["candidate_name"])
    add("Job Title", report_dict["job_title"])

    scores = report_dict["scores"]
    add("AI Match Score", f"{scores['final_weighted_score']}%")

    skills = report_dict["skills"]
    add("Matched Skills", ", ".join(skills["matched"]))
    add("Missing Skills", ", ".join(skills["missing"]))

    resp = report_dict["responsibilities"]
    add("Responsibility Strengths", "\n".join(resp["matched"]))
    add("Responsibility Gaps", "\n".join(resp["missing"]))

    qual = report_dict["qualifications"]
    add("Qualification Strengths", "\n".join(qual["matched"]))
    add("Qualification Gaps", "\n".join(qual["missing"]))

    doc.build(elements)
    return str(path)
