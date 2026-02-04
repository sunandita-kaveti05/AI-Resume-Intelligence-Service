# semantic_matcher.py

import numpy as np
from embeddings import embed

# ---------- COSINE ----------

def cos(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


# ---------- EMBEDDING MATCH ----------

def avg_best_match(source_list, target_list):
    """
    For every requirement in the target_list, find the single best 
    matching proof point in the source_list and average those scores.
    """
    if not source_list or not target_list:
        return 0.0

    s_emb = embed(source_list)
    t_emb = embed(target_list)

    scores = []
    for t in t_emb:
        # Quality fix: This now looks for the specific bullet point that 
        # matches the JD requirement, rather than comparing to a whole-resume summary.
        best = max(cos(t, s) for s in s_emb)
        scores.append(best)

    return float(np.mean(scores)) * 100


# ---------- 🔥 UPDATED: RETURN LIST INSTEAD OF JOINED STRING ----------

def get_semantic_resume_segments(resume):
    """
    Returns a list of individual semantic units (bullets/descriptions)
    to prevent signal dilution during matching.
    """
    lines = []

    # Experience responsibilities
    for e in resume.get("experience", []):
        lines.extend(e.get("responsibilities", []))

    # Project descriptions
    for p in resume.get("projects", []):
        if isinstance(p, dict) and p.get("description"):
            lines.append(p["description"])
        elif hasattr(p, "description") and p.description:
            lines.append(p.description)

    # Skills converted to natural language sentences
    for s in resume.get("raw_skills", []):
        lines.append(f"Experienced with {s}")

    return lines


# ---------- SKILL MATCH (ontology based) ----------

def skill_score(resume, jd):
    return avg_best_match(
        resume["tech_skills"],     # ontology skills
        jd["key_skills"]
    )


# ---------- RESPONSIBILITY MATCH ----------

def responsibility_score(resume, jd):
    # Quality fix: Passing the list of segments directly
    segments = get_semantic_resume_segments(resume)
    return avg_best_match(segments, jd["responsibilities"])


# ---------- QUALIFICATION MATCH ----------

def qualification_score(resume, jd):
    # Quality fix: Passing the list of segments directly
    segments = get_semantic_resume_segments(resume)

    qual_text = jd["qualifications"] or []
    if not qual_text:
        return 100.0

    return avg_best_match(segments, qual_text)


# ---------- TECH PROOF ----------

def tech_proof_score(resume, jd):
    combined = (
        resume["certifications"]
        + [p["title"] for p in resume["projects"]]
        + resume.get("raw_skills", [])
    )

    return avg_best_match(combined, jd["key_skills"])


# ---------- FINAL ----------

def compute_weighted_match(normalized):
    resume = normalized["resume"]
    jd = normalized["jd"]

    s1 = skill_score(resume, jd)
    s2 = responsibility_score(resume, jd)
    s3 = qualification_score(resume, jd)
    s4 = tech_proof_score(resume, jd)

    final = (
        0.35 * s1 +
        0.30 * s2 +
        0.20 * s3 +
        0.15 * s4
    )

    return {
        "skill_score": round(s1, 2),
        "responsibility_score": round(s2, 2),
        "qualification_score": round(s3, 2),
        "tech_proof_score": round(s4, 2),
        "final_weighted_score": round(final, 2),
    }