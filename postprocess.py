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


# ---------- 2. CLEAN SKILL LIST ----------

def clean_skill_list(items: List[str]) -> List[str]:

    if not items:
        return []

    cleaned = []

    for x in items:

        x = clean_text(x).lower()

        # handle messy separators
        tokens = re.split(r"[,\n;|•/]", x)

        for t in tokens:

            t = t.strip()

            if len(t) < 2:
                continue

            if len(t.split()) > 4:
                continue

            t = normalize_skill(t)

            cleaned.append(t)

    # remove duplicates but preserve order
    return list(dict.fromkeys(cleaned))


# ---------- 3. CLEAN SENTENCE LIST ----------

def clean_sentence_list(items: List[str]) -> List[str]:

    if not items:
        return []

    cleaned = []

    for x in items:

        x = clean_text(x)

        if len(x) > 1:
            cleaned.append(x)

    return list(dict.fromkeys(cleaned))


# ---------- 4. SPLIT TECH vs SOFT SKILLS ----------

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

    tech = []
    soft = []

    for s in skills:

        if s in SOFT_SKILLS:
            soft.append(s)
        else:
            tech.append(s)

    return tech, soft


# ---------- 5. SAFE ACCESS ----------

def get(obj: Any, key: str, default=None):

    if isinstance(obj, dict):
        return obj.get(key, default)

    return getattr(obj, key, default)


# ---------- 6. MAIN NORMALIZER ----------

def normalize_extraction(result: Any) -> Dict:

    resume = get(result, "resume_json")
    jd = get(result, "jd_json")

    # raw skills (for semantic matcher evidence)
    raw_skills = clean_sentence_list(get(resume, "skills", []))

    # ---------- RESUME SKILLS ----------

    resume_skills = clean_skill_list(get(resume, "skills", []))

    projects = get(resume, "projects", [])

    project_skills = []

    for p in projects:
        project_skills.extend(get(p, "tech_stack", []))

    resume_skills.extend(project_skills)

    resume_skills = clean_skill_list(resume_skills)

    tech_skills, soft_skills = split_skills(resume_skills)

    # ---------- JD SKILLS ----------

    jd_skills = clean_skill_list(get(jd, "key_skills", []))

    # ---------- EXPERIENCE CLEAN ----------

    experience = get(resume, "experience", [])

    cleaned_exp = []

    for exp in experience:

        responsibilities = clean_sentence_list(
            get(exp, "responsibilities", [])
        )

        cleaned_exp.append({
            **(exp if isinstance(exp, dict) else exp.model_dump()),
            "responsibilities": responsibilities
        })

    # ---------- PROJECT CLEAN ----------

    cleaned_projects = []

    for proj in projects:

        cleaned_projects.append({
            **(proj if isinstance(proj, dict) else proj.model_dump())
        })

    # ---------- JD RESPONSIBILITIES ----------

    jd_responsibilities = clean_sentence_list(
        get(jd, "responsibilities", [])
    )

    # ---------- EDUCATION ----------

    education = [
        e if isinstance(e, dict) else e.model_dump()
        for e in get(resume, "education", [])
    ]

    # ---------- FINAL STRUCTURE ----------

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

            "qualifications": clean_sentence_list(
                get(jd, "qualifications", [])
            ),

            "experience_required": get(jd, "experience_required"),
        }
    }

    return normalized_data
