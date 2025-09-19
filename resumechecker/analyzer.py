import pdfplumber
import json
from groq import Groq
from django.conf import settings


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract all text from a PDF file."""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()


def analyze_resume_with_llm(resume_text: str, job_description: str) -> dict:
    """
    Send resume and job description to Groq AI and get analyzed output.
    Returns a dictionary:
    {
        "rank": "85",
        "skills": ["Python", "Django"],
        "total_experience": "3",
        "project_category": ["AI", "Web Development"]
    }
    """
    prompt = f"""
You are an AI assistant that analyzes resumes for software engineering job applications.
Given a resume and a job description, extract the following details:

1. List all skills mentioned in the resume.
2. Calculate the total years of professional experience.
   - If experience is less than 1 year, convert it to months (e.g., 0.5 years → 6 months)
   - Round the final number to **1 decimal place**
3. Categorize projects based on their domain (e.g., AI, Web Development, Cloud, SaaS).
4. Rank the resume relevance to the job description on a scale from 0 to 100.

Resume:
{resume_text}

Job Description:
{job_description}

Provide the output ONLY in valid JSON format exactly like this structure:
{{
    "rank": "<percentage>",
    "skills": ["skill1", "skill2", "..."],
    "total_experience": "<number of years or months, rounded to 1 decimal place>",
    "project_category": ["category1", "category2", "..."]
}}
"""

    try:
        client = Groq(api_key=settings.GROQ_API_KEY)
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            response_format={"type": "json_object"},
        )

        # Get JSON content safely
        result = response.choices[0].message.content
        if isinstance(result, dict):
            return result
        return json.loads(result)

    except Exception as e:
        import sys, os
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"Error: {exc_type}, File: {fname}, Line: {exc_tb.tb_lineno}")
        print(e)
        return {
            "rank": "0",
            "skills": [],
            "total_experience": "0",
            "project_category": []
        }


def process_resume(pdf_path: str, job_description: str) -> dict:
    """
    Full pipeline: extract PDF text and analyze with LLM.
    Returns dictionary with rank, skills, experience, project categories.
    """
    try:
        resume_text = extract_text_from_pdf(pdf_path)
        if not resume_text:
            raise ValueError("PDF is empty or text could not be extracted.")
        return analyze_resume_with_llm(resume_text, job_description)
    except Exception as e:
        print(f"Process error: {e}")
        return {
            "rank": "0",
            "skills": [],
            "total_experience": "0",
            "project_category": []
        }
