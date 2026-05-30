import streamlit as st
import anthropic
from docx import Document
import PyPDF2

# Page configuration
st.set_page_config(
    page_title="Resume Analyzer | AI-Powered",
    page_icon="🎯",
    layout="wide"
)

# Custom styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1a1a1a;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🎯 AI Resume Analyzer</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Built with Claude API by Yuvaraj Thatiparthi | Analyze resume-job match instantly</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 📊 About This App")
    st.write("This tool uses Claude AI to analyze how well your resume matches a job description.")
    st.write("**Features:**")
    st.write("- Match score (0-100)")
    st.write("- Matching skills detected")
    st.write("- Missing skills")
    st.write("- Personalized recommendations")
    st.write("- ATS keywords to add")
    st.markdown("---")
    st.markdown("**Built by:** [Yuvaraj Thatiparthi](https://linkedin.com/in/yuvaraj-thatiparthi)")
    st.markdown("**GitHub:** [github.com/yuvaraj24799](https://github.com/yuvaraj24799)")
    st.markdown("---")
    st.markdown("**Powered by:** Anthropic Claude API")

# Get API key from Streamlit secrets
try:
    api_key = st.secrets["ANTHROPIC_API_KEY"]
except:
    api_key = None
    st.error("API key not configured. Please contact the app owner.")

# Helper function to extract text
def extract_text_from_file(uploaded_file):
    if uploaded_file is None:
        return ""
    file_extension = uploaded_file.name.split(".")[-1].lower()
    if file_extension == "pdf":
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    elif file_extension == "docx":
        doc = Document(uploaded_file)
        text = "\n".join([para.text for para in doc.paragraphs])
        return text
    elif file_extension == "txt":
        return uploaded_file.read().decode("utf-8")
    return ""

# Main columns
col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 Your Resume")
    resume_file = st.file_uploader("Upload Resume (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])
    resume_text_input = st.text_area("Or paste resume text here", height=200, placeholder="Paste your resume content...")

with col2:
    st.subheader("💼 Job Description")
    jd_text_input = st.text_area("Paste the job description here", height=350, placeholder="Paste the full job description...")

# Get final resume text
resume_text = ""
if resume_file is not None:
    resume_text = extract_text_from_file(resume_file)
elif resume_text_input:
    resume_text = resume_text_input

# Analyze button
st.markdown("---")
analyze_button = st.button("🚀 Analyze Match", type="primary", use_container_width=True)

if analyze_button:
    if not api_key:
        st.error("API key not configured.")
    elif not resume_text:
        st.error("Please upload or paste your resume.")
    elif not jd_text_input:
        st.error("Please paste the job description.")
    else:
        with st.spinner("🧠 Claude is analyzing your match..."):
            try:
                client = anthropic.Anthropic(api_key=api_key)
                prompt = f"""You are an expert career coach and ATS recruiter. Analyze this resume against the job description.

JOB DESCRIPTION:
{jd_text_input}

RESUME:
{resume_text}

Provide your analysis in this EXACT format:

## Match Score
[Single number from 0-100 followed by /100]

## Summary
[2-3 sentences explaining the overall fit]

## Matching Skills Found
[List 5-10 matching skills as bullet points]

## Missing Skills or Experience
[List 3-7 missing skills as bullet points]

## Specific Recommendations
[List 3-5 actionable recommendations as bullet points]

## ATS Keywords to Add
[List 5-10 exact keywords to add as bullet points]

Be specific, honest, and constructive."""

                message = client.messages.create(
                    model="claude-sonnet-4-5",
                    max_tokens=2000,
                    messages=[{"role": "user", "content": prompt}]
                )
                response_text = message.content[0].text
                st.markdown("---")
                st.markdown("## 📊 Analysis Results")
                st.markdown(response_text)
                st.success("Analysis complete! Use these insights to improve your resume.")

            except Exception as e:
                st.error(f"Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: #888;'>Powered by Claude API | Built by Yuvaraj Thatiparthi</div>", unsafe_allow_html=True)
