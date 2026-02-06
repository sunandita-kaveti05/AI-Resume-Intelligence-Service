# main.py
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import shutil
import os
import json
from pathlib import Path
from datetime import datetime

from cleaner import extract_text_from_pdf, extract_text_from_docx, extract_independently
from storage import resume_hash, save_resume_json, load_resume_json
from postprocess import normalize_extraction
from semantic_matcher import compute_weighted_match
from report_generator import generate_report_dict
from pdf_report import generate_pdf

app = FastAPI()

from fastapi.responses import HTMLResponse

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
        <head>
            <title>Resume Analysis Service</title>
        </head>
        <body style="font-family: Arial; text-align: center; margin-top: 60px;">
            <h1>Resume Analysis Microservice</h1>
            <p>This service analyzes candidate Resume and semantically matches with JD</p>
            <p>Use the interactive API docs to test the service.</p>
            <a href="/docs" style="font-size:20px;">👉 Open API Documentation</a>
        </body>
    </html>
    """

# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- DIRECTORIES ----------
UPLOAD_DIR = Path("temp_uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

REPORT_DIR = Path("reports")
REPORT_DIR.mkdir(exist_ok=True)

ANALYSIS_DIR = Path("data/analysis")
ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)

# Serve PDFs
app.mount("/reports", StaticFiles(directory="reports"), name="reports")


# ---------- ANALYZE ENDPOINT ----------
@app.post("/analyze")
async def analyze_resume(
    jd_text: str = Form(...),
    file: UploadFile = File(...)
):
    temp_path = UPLOAD_DIR / file.filename

    # 1. Save uploaded file
    with temp_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    print(f"[INFO] Uploaded file: {file.filename}")

    # 2. Extract resume text
    if file.filename.endswith(".pdf"):
        resume_text = extract_text_from_pdf(str(temp_path))
    elif file.filename.endswith(".docx"):
        resume_text = extract_text_from_docx(str(temp_path))
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format")

    print("[INFO] Resume text extracted")

    # 3. Resume cache check
    h = resume_hash(resume_text)
    stored_resume = load_resume_json(h)

    if stored_resume:
        print("[INFO] Resume found in cache")
        result = extract_independently("", jd_text)
        result.resume_json = stored_resume
    else:
        print("[INFO] Parsing resume with Gemini")
        result = extract_independently(resume_text, jd_text)
        save_resume_json(h, result.resume_json.model_dump())

    # 4. Core pipeline
    normalized = normalize_extraction(result)
    scores = compute_weighted_match(normalized)

    # 5. Structured report
    report_dict = generate_report_dict(normalized, scores)

    # 6. Generate Analysis Report PDF
    pdf_path = generate_pdf(report_dict)
    pdf_url = f"/reports/{Path(pdf_path).name}"
    report_dict["analysis_report_pdf"] = pdf_url

    print(f"[INFO] Candidate: {report_dict['candidate_name']}")
    print(f"[INFO] Final Score: {scores['final_weighted_score']}")
    print(f"[INFO] PDF Generated: {pdf_url}")

    # 7. Persist analysis result
    file_name = f"{report_dict['candidate_name']}_{datetime.now().timestamp()}.json"
    with open(ANALYSIS_DIR / file_name, "w") as f:
        json.dump(report_dict, f, indent=2)

    print(f"[INFO] Analysis saved: {file_name}")

    # 8. Cleanup
    os.remove(temp_path)

    return report_dict


# ---------- RANKING ENDPOINT ----------
@app.get("/ranking")
def get_ranking():
    results = []

    for file in ANALYSIS_DIR.glob("*.json"):
        data = json.load(open(file))
        results.append({
            "candidate_name": data["candidate_name"],
            "score": data["scores"]["final_weighted_score"],
            "pdf": data["analysis_report_pdf"]
        })

    results.sort(key=lambda x: x["score"], reverse=True)

    return results


# ---------- RUN ----------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
