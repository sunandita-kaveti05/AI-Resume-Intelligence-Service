# AI Resume Intelligence Service

An AI-powered resume analysis microservice that evaluates a candidate’s resume against a job description using LLM parsing, skill ontology, semantic matching (embeddings), and weighted ATS scoring.
It returns a structured JSON report and a downloadable PDF analysis report.

This service is designed to plug into any recruitment portal as an **AI analysis engine**.

---

## 🚀 What this system does

Given:

* A **Job Description**
* A **Candidate Resume** (PDF/DOCX)

The system:

1. Extracts text from resume
2. Uses an LLM to parse resume and JD into structured JSON
3. Cleans and normalizes skills using a skill ontology
4. Performs semantic matching using sentence embeddings
5. Computes weighted ATS match scores
6. Generates a structured analysis report (JSON)
7. Generates a human-readable PDF report

---

## 🧩 Architecture

```
Resume + JD
     ↓
LLM Parsing (Gemini)
     ↓
Post-processing + Skill Ontology
     ↓
Semantic Matching (Sentence Transformers)
     ↓
Weighted Scoring
     ↓
JSON Report + PDF
```

This service is **stateless** and intended to be called by a main backend.

---

## 🔌 API Endpoints

### `POST /analyze`

Analyze a resume against a JD.

**Input (Form Data)**

* `jd_text` — full job description
* `file` — resume (.pdf/.docx)

**Output**

* Full analysis JSON
* AI match scores
* Matched/missing skills
* Education, experience, projects
* `analysis_report_pdf` link

---

### `GET /ranking`

Returns analyzed candidates sorted by score.

---

## 🛠️ Requirements

* Python 3.10+
* Gemini API key (LLM)
* Internet (for first-time embedding model download)

---

## 📦 Installation

Create a virtual environment and install dependencies:

```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Variables

Create a `.env` file:

```
GEMINI_API_KEY=your_api_key_here
```

Make sure `.env` is in `.gitignore`.

---

## ▶️ Running the server

```bash
uvicorn main:app --reload
```

Open Swagger docs:

```
http://127.0.0.1:8000/docs
```

---

## 📁 Project Structure

```
main.py                → FastAPI endpoints
cleaner.py             → Resume/JD extraction + LLM parsing
postprocess.py         → Cleaning and normalization
skill_ontology.py      → Skill normalization logic
skills_db.json         → Skill vocabulary
semantic_matcher.py    → Weighted scoring logic
embeddings.py          → SentenceTransformer embeddings
report_generator.py    → Structured report builder
pdf_report.py          → PDF generation
storage.py             → Resume caching
```

---

## 🔗 How this integrates into a recruitment system

This service does **not** manage users, jobs, or databases.

A main backend should:

1. Send resume + JD to `/analyze`
2. Store returned JSON against candidate & job
3. Use stored data for dashboards, reports, ranking
4. Provide UI for viewing results

---

## ✅ Summary

This is an AI microservice that provides:

* LLM-based resume parsing
* Ontology-driven skill recognition
* Semantic job matching
* ATS-style scoring
* PDF report generation

Designed to be plugged into any hiring platform.
