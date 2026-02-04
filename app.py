# app.py
import streamlit as st
import os
from cleaner import (
    extract_text_from_pdf, 
    extract_text_from_docx, 
    extract_independently
)
from postprocess import normalize_extraction
from semantic_matcher import compute_weighted_match
from report_generator import generate_report
from storage import resume_hash, load_resume_json, save_resume_json

st.set_page_config(page_title="AI ATS Analyzer", page_icon="📄", layout="wide")

st.title("📄 AI-Powered ATS Resume Analyzer")
st.markdown("Upload a resume and paste a Job Description to see how well they match.")

col1, col2 = st.columns([1, 1])

with col1:
    st.header("Upload Details")
    uploaded_file = st.file_uploader("Choose a Resume", type=["pdf", "docx"])
    jd_input = st.text_area("Paste Job Description here", height=300)

with col2:
    st.header("Analysis Result")
    if st.button("Analyze Match"):
        if uploaded_file and jd_input:
            with st.spinner("Analyzing... (Semantic model running)"):
                # Save temp file
                with open(uploaded_file.name, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Extract Text
                if uploaded_file.name.endswith(".pdf"):
                    resume_text = extract_text_from_pdf(uploaded_file.name)
                else:
                    resume_text = extract_text_from_docx(uploaded_file.name)

                # Process
                h = resume_hash(resume_text)
                stored_resume = load_resume_json(h)

                if stored_resume:
                    result = extract_independently("", jd_input)
                    result.resume_json = stored_resume
                else:
                    result = extract_independently(resume_text, jd_input)
                    save_resume_json(h, result.resume_json.model_dump())

                normalized = normalize_extraction(result)
                scores = compute_weighted_match(normalized)
                report = generate_report(normalized, scores)

                # Display Scores
                st.success(f"Final Score: {scores['final_weighted_score']}%")
                
                cols = st.columns(4)
                cols[0].metric("Skills", f"{scores['skill_score']}%")
                cols[1].metric("Responsibility", f"{scores['responsibility_score']}%")
                cols[2].metric("Qualification", f"{scores['qualification_score']}%")
                cols[3].metric("Proof", f"{scores['tech_proof_score']}%")

                # Show Report
                st.text_area("Detailed Report", report, height=400)
                
                os.remove(uploaded_file.name)
        else:
            st.error("Please provide both a resume and a JD.")