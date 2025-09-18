import pdfplumber
import spacy
from groq import Groq
import json
from django.conf import settings




def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text.strip()




def analyze_resume_with_llm(resume_text:str, job_descrption:str)->dict:
    prompt = f"""
        You are an AI assitant that analyzes resumes for a software engineering job application.
        Given a resume and a job descpription, extract the following details:

        1. Identify all skills mentioned in the resume.
        2. Calculate the total years of expierence.
        3. Categories the projects based on the domain (e.g, AI,Webdevelopment, Cloud etc)
        4. Rank the resume relevance to the job descpriton on a scale of 0 to 100.


        Resume:
        {resume_text}

        Job Description:
        {job_descrption}

        Provide the output in valid JSON format with this structure:
        {{
            "rank" : "<percentage>",
            "skills" : ["skill", "skill2",......],
            "total_experience" : "<number of years>",
            "project_category" : ["category1","category2",....]

        }}

        """
    #print(prompt)
    try:
        client = Groq(api_key = settings.GROQ_API_KEY)
        print(client)
        response = client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    response_format={"type": "json_object"},
                )
        # print("#####")
        print(response)

        result = response.choices[0].message.content
        return json.loads(result)

    except Exception as e:
        print(e)
        import sys, os
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

