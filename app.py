import streamlit as st
import pdfplumber
from docx import Document
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3

# Database Connection
conn = sqlite3.connect("resume_data.db")
cursor = conn.cursor()

# Create Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_name TEXT,
    match_score REAL
)
""")

conn.commit()

# Streamlit UI
st.set_page_config(
    page_title="AI Resume Screening System",
    layout="wide"
)

st.title("🚀 AI Resume Screening System")

candidate_name = st.text_input(
    "Enter Candidate Name"
)

uploaded_file = st.file_uploader(
    "Upload Your Resume",
    type=["pdf", "docx"]
)

skills_list = [
    "python",
    "sql",
    "machine learning",
    "azure",
    "power bi",
    "statistics",
    "data analysis",
    "excel"
]

if uploaded_file is not None:

    st.success("Resume Uploaded Successfully!")

    text = ""

    # PDF Extraction
    if uploaded_file.name.endswith(".pdf"):

        with pdfplumber.open(uploaded_file) as pdf:

            for page in pdf.pages:
                text += page.extract_text()

    # DOCX Extraction
    elif uploaded_file.name.endswith(".docx"):

        doc = Document(uploaded_file)

        for para in doc.paragraphs:
            text += para.text + "\n"

    st.subheader("📄 Extracted Resume Text")
    st.write(text)

    # Skill Detection
    detected_skills = []

    lower_text = text.lower()

    for skill in skills_list:

        if skill in lower_text:
            detected_skills.append(skill)

    st.subheader("🧠 Detected Skills")

    if detected_skills:

        for skill in detected_skills:
            st.write("✅", skill)

    else:
        st.write("No skills detected")

    # Job Skills Input
    st.subheader("💼 Job Skills Required")

    job_skills_input = st.text_input(
        "Enter required job skills separated by commas"
    )

    if job_skills_input:

        job_skills = [
            skill.strip().lower()
            for skill in job_skills_input.split(",")
        ]

        matched_skills = []

        for skill in job_skills:

            if skill in detected_skills:
                matched_skills.append(skill)

        # Match Score
        match_score = (
            len(matched_skills) / len(job_skills)
        ) * 100

        st.subheader("📊 Match Results")

        st.write("Matched Skills:", matched_skills)

        st.write(
            "Match Score:",
            round(match_score, 2),
            "%"
        )

        # Save to Database
        cursor.execute("""
        INSERT INTO candidates (
            candidate_name,
            match_score
        )
        VALUES (?, ?)
        """, (
            candidate_name,
            round(match_score, 2)
        ))

        conn.commit()

        st.success("Candidate Data Saved Successfully!")

        # Fetch Data
        data = pd.read_sql_query(
            "SELECT * FROM candidates",
            conn
        )

        st.subheader("🏆 Candidate Ranking")
        st.dataframe(data)

        # Chart
        st.subheader("📈 Candidate Score Chart")

        fig, ax = plt.subplots()

        ax.bar(
            data["candidate_name"],
            data["match_score"]
        )

        ax.set_ylabel("Score")

        ax.set_title("Candidate Match Scores")

        st.pyplot(fig)