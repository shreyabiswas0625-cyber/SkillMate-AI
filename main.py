import streamlit as st
import PyPDF2
import io
import os
from google import genai
from dotenv import load_dotenv

#Loading env variables
load_dotenv()

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon = "📄",
    layout = "centered"
)

st.title("💼 SkillMate AI")
st.markdown("Upload your resume and get AI-powered feedback tailored to your needs!")

#Loading API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    st.error("Gemini API key not found. Please add it to your .env file.")
    st.stop()

client = genai.Client(api_key=GEMINI_API_KEY)

#File Upload
uploaded_file = st.file_uploader("Upload your resume (PDF/TXT)", type=["pdf"])
job_role = st.text_input("Enter Job Role (optional): ")

analyze = st.button("Analyze Resume")

def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    return text


def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(uploaded_file.read()))
    return uploaded_file.read().decode("utf-8")

if analyze and uploaded_file:
    try:
        file_content = extract_text_from_file(uploaded_file)

        if not file_content.strip():
            st.error("File does not contain any text")
            st.stop()

        prompt = f"""
    You are an expert resume reviewer with years of HR and recruitment experience.

    Analyze the following resume.

    Focus on:

    1. Overall Resume Score (out of 100)
    2. ATS Compatibility
    3. Content Clarity
    4. Skills Presentation
    5. Experience Descriptions
    6. Grammar & Formatting
    7. Missing Skills
    8. Strengths
    9. Weaknesses
    10. Suggestions for Improvement

    The user is applying for:
    {job_role if job_role else "General Job Applications"}
    
    Resume:

    {file_content}

    Please return your response in Markdown using clear headings and bullet points.
    """

        with st.spinner("Analyzing your resume..."):

            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=prompt
            )

        st.success("Analysis Complete!")

        st.markdown("## 📊 Resume Analysis")
        st.markdown(response.text)

    except Exception as e:
        st.error(f"An error occurred: {e}")


