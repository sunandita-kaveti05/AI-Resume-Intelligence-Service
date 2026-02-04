# storage.py
import json
import hashlib
from pathlib import Path

BASE = Path("data/resumes")
BASE.mkdir(parents=True, exist_ok=True)

def resume_hash(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()

def save_resume_json(hash_id: str, data: dict):
    with open(BASE / f"{hash_id}.json", "w") as f:
        json.dump(data, f, indent=2)

def load_resume_json(hash_id: str):
    path = BASE / f"{hash_id}.json"
    if path.exists():
        return json.load(open(path))
    return None
