# skill_ontology.py
import json

with open("skills_db.json") as f:
    SKILL_DB = json.load(f)

def normalize_skill(skill: str) -> str:
    s = skill.lower().strip()

    for canonical, variants in SKILL_DB.items():
        if s == canonical or s in variants:
            return canonical

    return s
