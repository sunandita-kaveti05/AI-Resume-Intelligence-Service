# report_generator.py
from embeddings import embed
import numpy as np

# ---------- COSINE ----------
def cos(a, b):
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


# ---------- SEMANTIC SKILL ANALYSIS ----------
def semantic_skill_analysis(resume_skills, jd_skills, threshold=0.75):
    if not resume_skills or not jd_skills:
        return [], jd_skills

    r_emb = embed(resume_skills)
    j_emb = embed(jd_skills)

    strengths = []
    gaps = []

    for i, j_vec in enumerate(j_emb):
        scores = [cos(j_vec, r_vec) for r_vec in r_emb]
        best_score = max(scores) if scores else 0

        if best_score >= threshold:
            strengths.append(jd_skills[i])
        else:
            gaps.append(jd_skills[i])

    return strengths, gaps


# ---------- SEMANTIC ANALYSIS ----------
def semantic_analysis(resume_texts, jd_texts, threshold=0.45):
    if not resume_texts or not jd_texts:
        return [], jd_texts

    resume_texts = [t for t in resume_texts if t.strip()]

    r_emb = embed(resume_texts)
    j_emb = embed(jd_texts)

    strengths = []
    weaknesses = []

    for i, j in enumerate(j_emb):
        scores = [cos(j, r) for r in r_emb]
        best = max(scores) if scores else 0

        if best >= threshold:
            strengths.append(jd_texts[i])
        else:
            weaknesses.append(jd_texts[i])

    return strengths, weaknesses


# ---------- PROOF POINT BUILDER ----------
def get_resume_proof_points(resume):
    points = []

    for e in resume.get("experience", []):
        points.extend(e.get("responsibilities", []))

    for p in resume.get("projects", []):
        if isinstance(p, dict) and p.get("description"):
            points.append(p["description"])

    for s in resume.get("raw_skills", []):
        points.append(f"Experienced in {s}")

    for edu in resume.get("education", []):
        points.append(f"Completed {edu.get('degree')} at {edu.get('institution')}")

    return [p for p in points if p.strip()]


# ---------- NEW: STRUCTURED REPORT DICT ----------
def generate_report_dict(normalized, scores):
    resume = normalized["resume"]
    jd = normalized["jd"]

    skill_strengths, skill_gaps = semantic_skill_analysis(
        resume["tech_skills"],
        jd["key_skills"],
        threshold=0.65
    )

    proof_points = get_resume_proof_points(resume)

    resp_strengths, resp_weak = semantic_analysis(
        proof_points,
        jd["responsibilities"],
        threshold=0.45
    )

    qual_strengths, qual_weak = semantic_analysis(
        proof_points,
        jd["qualifications"] or [],
        threshold=0.40
    )

    return {
        "candidate_name": resume["name"],
        "job_title": jd["job_title"],
        "scores": scores,

        "skills": {
            "jd_skills": jd["key_skills"],
            "resume_skills": resume["tech_skills"],
            "matched": skill_strengths,
            "missing": skill_gaps
        },

        "responsibilities": {
            "matched": resp_strengths,
            "missing": resp_weak
        },

        "qualifications": {
            "matched": qual_strengths,
            "missing": qual_weak
        },

        "education": resume["education"],
        "experience": resume["experience"],
        "projects": resume["projects"],
        "certifications": resume["certifications"],
        "achievements": resume["achievements"],
    }


# ---------- OPTIONAL: STRING REPORT (for CLI debugging) ----------
def generate_report_string(report_dict):
    s = report_dict["scores"]
    skills = report_dict["skills"]
    resp = report_dict["responsibilities"]
    qual = report_dict["qualifications"]

    return f"""
==================== ATS ANALYSIS REPORT ====================

Candidate : {report_dict['candidate_name']}
Job Title : {report_dict['job_title']}

AI Match Score : {s['final_weighted_score']}%

Matched Skills:
{', '.join(skills['matched'])}

Missing Skills:
{', '.join(skills['missing'])}

Responsibility Strengths:
{chr(10).join(resp['matched'])}

Responsibility Gaps:
{chr(10).join(resp['missing'])}

Qualification Strengths:
{chr(10).join(qual['matched'])}

Qualification Gaps:
{chr(10).join(qual['missing'])}
"""
