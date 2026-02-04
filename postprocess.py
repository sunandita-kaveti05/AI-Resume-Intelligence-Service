# postprocess.py

from typing import Tuple, List, Dict, Any
from skill_ontology import normalize_skill
import re


# ---------- 1. BASIC STRING CLEAN ----------

def clean_text(x: str) -> str:
    if not x:
        return ""
    return (
        x.replace("\n", " ")
         .replace("\t", " ")
         .replace("  ", " ")
         .strip()
    )


# ---------- 2. SKILL VOCAB FILTER (ATS CORE) ----------

TECH_PATTERN = re.compile(
    r"\b("
    r"python|java|c\+\+|c|sql|mysql|mongodb|pandas|numpy|matplotlib|seaborn|"
    r"sklearn|scikit|xgboost|ml|ai|nlp|llm|rag|docker|linux|git|api|rest|"
    r"cloud|aws|gcp|azure|fastapi|flask|tensorflow|pytorch"
    r")\b"
)


def looks_like_skill(token: str) -> bool:
    """
    Resume-agnostic, JD-agnostic skill detector.
    Keeps only technology-looking tokens.
    """
    if len(token) < 2:
        return False

    if len(token.split()) > 4:
        return False

    return bool(TECH_PATTERN.search(token))


# ---------- 3. CLEAN SKILL LIST (LLM-AWARE) ----------

def clean_skill_list(items: List[str]) -> List[str]:
    if not items:
        return []

    cleaned = []

    for x in items:
        x = clean_text(x).lower()

        tokens = re.split(r"[,\n:/;|•\-\(\)&\.]", x)

        for t in tokens:
            t = t.strip()

            if len(t) < 2:
                continue

            # remove dates, numbers, scores
            if re.search(r"\d", t):
                continue

            if not looks_like_skill(t):
                continue

            t = normalize_skill(t)
            cleaned.append(t)

    return list(set(cleaned))


# ---------- 4. CLEAN SENTENCE LIST ----------

def clean_sentence_list(items: List[str]) -> List[str]:
    if not items:
        return []

    cleaned = []
    for x in items:
        x = clean_text(x)
        if len(x) > 1:
            cleaned.append(x)

    return list(set(cleaned))


# ---------- 5. SPLIT TECH vs SOFT SKILLS ----------

SOFT_SKILLS = {
    "problem solving",
    "collaboration",
    "adaptability",
    "quick learning",
    "communication",
    "leadership",
    "teamwork",
    "hardworking",
    "proactive"
}


def split_skills(skills: List[str]) -> Tuple[List[str], List[str]]:
    tech, soft = [], []

    for s in skills:
        if s in SOFT_SKILLS:
            soft.append(s)
        else:
            tech.append(s)

    return tech, soft


# ---------- 6. SAFE ACCESS ----------

def get(obj: Any, key: str, default=None):
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


# ---------- 7. MAIN NORMALIZER ----------

def normalize_extraction(result: Any) -> Dict:

    resume = get(result, "resume_json")
    jd = get(result, "jd_json")

    raw_skills = clean_sentence_list(get(resume, "skills", []))

    resume_skills = clean_skill_list(get(resume, "skills", []))
    jd_skills = clean_skill_list(get(jd, "key_skills", []))

    tech_skills, soft_skills = split_skills(resume_skills)

    # ---- Experience ----
    experience = get(resume, "experience", [])
    cleaned_exp = []

    for exp in experience:
        responsibilities = clean_sentence_list(get(exp, "responsibilities", []))
        cleaned_exp.append({
            **(exp if isinstance(exp, dict) else exp.model_dump()),
            "responsibilities": responsibilities
        })

    # ---- Projects ----
    projects = get(resume, "projects", [])
    cleaned_projects = []

    for proj in projects:
        cleaned_projects.append({
            **(proj if isinstance(proj, dict) else proj.model_dump())
        })

    # ---- JD responsibilities ----
    jd_responsibilities = clean_sentence_list(get(jd, "responsibilities", []))

    # ---- Education ----
    education = [
        e if isinstance(e, dict) else e.model_dump()
        for e in get(resume, "education", [])
    ]

    normalized_data = {
        "resume": {
            "name": get(resume, "name"),
            "email": get(resume, "email"),
            "phone": get(resume, "phone"),

            "raw_skills": raw_skills,
            "tech_skills": tech_skills,
            "soft_skills": soft_skills,

            "education": education,
            "experience": cleaned_exp,
            "projects": cleaned_projects,
            "certifications": get(resume, "certifications", []),
            "achievements": get(resume, "achievements", []),
        },
        "jd": {
            "job_title": get(jd, "job_title"),
            "key_skills": jd_skills,
            "responsibilities": jd_responsibilities,
            "qualifications": clean_sentence_list(get(jd, "qualifications", [])),
            "experience_required": get(jd, "experience_required"),
        }
    }

    return normalized_data
