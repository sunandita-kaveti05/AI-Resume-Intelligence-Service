# cleaner.py
import fitz  # PyMuPDF
import docx
from typing import List, Optional
from pydantic import BaseModel
from google import genai



# ---------- 1. TEXT EXTRACTION ----------

def extract_text_from_pdf(path: str) -> str:
    doc = fitz.open(path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text


def extract_text_from_docx(path: str) -> str:
    doc = docx.Document(path)
    return "\n".join([para.text for para in doc.paragraphs])


# ---------- 2. ATS-GRADE GEMINI SAFE SCHEMA ----------

class Education(BaseModel):
    degree: str
    institution: str
    duration: Optional[str]
    score: Optional[str]


class Experience(BaseModel):
    role: str
    organization: str
    duration: str
    responsibilities: List[str]


class Project(BaseModel):
    title: str
    tech_stack: List[str]
    description: str


class ResumeData(BaseModel):
    name: str
    email: str
    phone: str
    links: List[str]
    education: List[Education]
    skills: List[str]
    experience: List[Experience]
    projects: List[Project]
    certifications: List[str]
    achievements: List[str]


class JDData(BaseModel):
    job_title: str
    key_skills: List[str]
    responsibilities: List[str]
    qualifications: List[str]
    experience_required: Optional[str]


class BatchExtraction(BaseModel):
    resume_json: ResumeData
    jd_json: JDData


# ---------- 3. GEMINI CLIENT ----------

import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))



# ---------- 4. CORE FUNCTION USED BY API ----------

def extract_independently(resume_text: str, jd_text: str) -> BatchExtraction:
    """
    This function ONLY does structured extraction.
    No scoring, no reporting, no printing.
    """

    prompt = f"""
You are an ATS data extraction engine.

Extract ALL structured entities from Resume and Job Description.

RULES:
- Do NOT mix Resume info into JD.
- Do NOT mix JD info into Resume.
- If a field is missing, return empty list or null.
- Extract maximum possible detail.

--- RESUME TEXT ---
{resume_text}

--- JOB DESCRIPTION TEXT ---
{jd_text}
"""

    response = client.models.generate_content(
        model="models/gemini-2.5-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": BatchExtraction,
        },
    )

    return response.parsed
