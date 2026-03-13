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

    prompt = f"""You are an ATS-grade resume parser.

Extract structured JSON from the Resume and Job Description.

The output MUST match the schema exactly.

-------------------------
RESUME EXTRACTION RULES
-------------------------

1. SKILLS

Extract ALL technologies used in the resume from:

- Skills section
- Project tech stacks
- Experience bullet points
- Tools mentioned inside descriptions

Skills may appear in messy formats like:

Python | SQL | Pandas
Python, SQL, Pandas
Python • SQL • Pandas
Python / SQL / Pandas
Python;SQL;Pandas

Convert them into a clean list.

Example output:

["python","sql","pandas","scikit-learn","docker"]

Return only technology names.

Do NOT return sentences.

Combine skills from all resume sections into a single flat list.


2. PROJECTS

For every project extract:

title  
tech_stack  
description

Rules:

• description should be 2–3 important lines summarizing the project
• tech_stack must contain the technologies used

Example:

{{
"title": "AI Resume Matcher",
"tech_stack": ["python","fastapi","bert"],
"description": "Built a semantic resume matching system using embeddings and FastAPI."
}}


3. EXPERIENCE

For each job or internship extract:

role  
organization  
duration  
responsibilities

Rules:

• responsibilities should contain the important bullet points
• keep them concise
• keep technologies mentioned in the bullet points


Example:

{{
"role":"Machine Learning Intern",
"organization":"ABC Tech",
"duration":"Jan 2024 – May 2024",
"responsibilities":[
"Built ML models using Python and Scikit-learn",
"Processed datasets using Pandas",
"Developed APIs using FastAPI"
]
}}


4. EDUCATION

Extract:

degree  
institution  
duration  
score (if available)


5. CERTIFICATIONS

Extract all certifications listed.


6. ACHIEVEMENTS

Extract awards, competitions, or recognitions.


-------------------------
JOB DESCRIPTION RULES
-------------------------

Extract structured fields from the JD.

1. job_title

2. key_skills

Extract concrete technologies and tools.

Example:

["python","pytorch","docker","fastapi","aws"]

Ignore vague phrases like:
"machine learning models"
"backend technologies"


3. responsibilities

Extract the main responsibility bullet points.


4. qualifications

Extract required education, experience, or knowledge.


5. experience_required

If the JD explicitly mentions required years of experience.


-------------------------
IMPORTANT
-------------------------

Return ONLY valid JSON matching the schema.

Do NOT mix resume data and JD data.

Do NOT hallucinate information.
-------------------------
RESUME TEXT
-------------------------
{resume_text}

-------------------------
JOB DESCRIPTION
-------------------------
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
