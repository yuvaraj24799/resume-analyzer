import streamlit as st
import anthropic
from docx import Document
import PyPDF2
import re
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="AI Resume Analyzer | Yuvaraj Thatiparthi",
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
    .score-container {
        text-align: center;
        padding: 2rem;
        border-radius: 12px;
        margin: 1rem 0;
    }
    .score-excellent { background: linear-gradient(135deg, #00b09b, #96c93d); color: white; }
    .score-good { background: linear-gradient(135deg, #f093fb, #f5576c); color: white; }
    .score-average { background: linear-gradient(135deg, #4facfe, #00f2fe); color: white; }
    .score-low { background: linear-gradient(135deg, #f7971e, #ffd200); color: white; }
    .score-number { font-size: 4rem; font-weight: bold; }
    .score-label { font-size: 1.2rem; margin-top: 0.5rem; }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🎯 AI Resume Analyzer</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Built with Claude API by Yuvaraj Thatiparthi | Analyze resume-job match instantly</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("### 📊 About This App")
    st.write("This tool uses Claude AI to analyze how well your resume matches a job description.")
    st.markdown("**Features:**")
    st.write("✅ Match score with visual gauge")
    st.write("✅ Matching skills detected")
    st.write("✅ Missing skills identified")
    st.write("✅ Personalized recommendations")
    st.write("✅ ATS keywords to add")
    st.write("✅ Download analysis report")
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
    st.error("API key not configured.")

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

# Score visualization function
def show_score_gauge(score):
    if score >= 80:
        css_class = "score-excellent"
        label = "Excellent Match! 🌟"
    elif score >= 65:
        css_class = "score-good"
        label = "Good Match! 👍"
    elif score >= 50:
        css_class = "score-average"
        label = "Average Match 📊"
    else:
        css_class = "score-low"
        label = "Needs Improvement ⚠️"

    st.markdown(
        '<div class="score-container ' + css_class + '">'
        '<div class="score-number">' + str(score) + '/100</div>'
        '<div class="score-label">' + label + '</div>'
        '</div>',
        unsafe_allow_html=True
    )
    st.progress(score / 100)

# Extract score from response
def extract_score(response_text):
    lines = response_text.split('\n')
    for i, line in enumerate(lines):
        if 'Match Score' in line:
            for j in range(i+1, min(i+4, len(lines))):
                next_line = lines[j].strip()
                if next_line:
                    numbers = re.findall(r'\b(\d{1,3})\b', next_line)
                    for num in numbers:
                        if 0 <= int(num) <= 100:
                            return int(num)
    return None

# Main columns
col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 Your Resume")
    resume_file = st.file_uploader(
        "Upload Resume (PDF, DOCX, or TXT)",
        type=["pdf", "docx", "txt"]
    )
    resume_text_input = st.text_area(
        "Or paste resume text here",
        height=200,
        placeholder="Paste your resume content here..."
    )

with col2:
    st.subheader("💼 Job Description")
    jd_text_input = st.text_area(
        "Paste the job description here",
        height=350,
        placeholder="Paste the full job description here..."
    )

# Get final resume text
resume_text = ""
if resume_file is not None:
    with st.spinner("Reading your resume..."):
        resume_text = extract_text_from_file(resume_file)
    if resume_text:
        st.success("Resume loaded successfully!")
elif resume_text_input:
    resume_text = resume_text_input

# Analyze button
st.markdown("---")
analyze_button = st.button(
    "🚀 Analyze Match",
    type="primary",
    use_container_width=True
)

if analyze_button:
    if not api_key:
        st.error("API key not configured.")
    elif not resume_text:
        st.error("Please upload or paste your resume.")
    elif not jd_text_input:
        st.error("Please paste the job description.")
    elif len(jd_text_input) < 50:
        st.error("Job description seems too short. Please paste the full job description.")
    else:
        progress_bar = st.progress(0)
        status_text = st.empty()

        status_text.text("🔍 Reading your resume...")
        progress_bar.progress(20)

        status_text.text("🧠 Claude is analyzing the job requirements...")
        progress_bar.progress(40)

        try:
            client = anthropic.Anthropic(api_key=api_key)

            status_text.text("🤖 Matching skills and experience...")
            progress_bar.progress(60)

            prompt = (
                "You are an expert career coach and ATS recruiter with 15 years of experience. "
                "Analyze this resume against the job description and provide a detailed, honest assessment.\n\n"
                "JOB DESCRIPTION:\n" + jd_text_input + "\n\n"
                "RESUME:\n" + resume_text + "\n\n"
                "Provide your analysis in this EXACT format:\n\n"
                "## Match Score\n"
                "[Single number from 0-100 representing overall match percentage]\n\n"
                "## Summary\n"
                "[2-3 sentences explaining the overall fit]\n\n"
                "## Matching Skills Found\n"
                "[List 5-10 specific matching skills as bullet points]\n\n"
                "## Missing Skills or Experience\n"
                "[List 3-7 missing skills as bullet points]\n\n"
                "## Specific Recommendations\n"
                "[List 4-5 actionable recommendations as bullet points]\n\n"
                "## ATS Keywords to Add\n"
                "[List 8-10 exact keywords to add as bullet points]\n\n"
                "## Interview Talking Points\n"
                "[List 3 strong talking points to emphasize in interviews as bullet points]\n\n"
                "Be specific, honest, and constructive."
            )

            status_text.text("✍️ Generating detailed recommendations...")
            progress_bar.progress(80)

            message = client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=2500,
                messages=[{"role": "user", "content": prompt}]
            )

            progress_bar.progress(100)
            status_text.text("✅ Analysis complete!")

            response_text = message.content[0].text

            progress_bar.empty()
            status_text.empty()

            st.markdown("---")
            st.markdown("## 📊 Analysis Results")

            score = extract_score(response_text)
            if score is not None:
                col_score1, col_score2, col_score3 = st.columns([1, 2, 1])
                with col_score2:
                    show_score_gauge(score)

                met1, met2, met3 = st.columns(3)
                with met1:
                    if score >= 70:
                        st.metric("Match Score", str(score) + "/100", "Strong Match")
                    else:
                        st.metric("Match Score", str(score) + "/100", "Needs Work")
                with met2:
                    if score >= 80:
                        st.metric("Interview Chance", "High", "Apply Now!")
                    elif score >= 65:
                        st.metric("Interview Chance", "Medium", "Good Fit")
                    else:
                        st.metric("Interview Chance", "Lower", "Improve First")
                with met3:
                    st.metric("Analysis By", "Claude AI", "Anthropic")

            st.markdown("---")
            st.markdown(response_text)

            st.markdown("---")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            date_str = datetime.now().strftime("%B %d, %Y at %I:%M %p")
            separator = "=" * 60
            download_content = (
                "AI RESUME ANALYSIS REPORT\n"
                "Generated by: Yuvaraj Thatiparthi AI Resume Analyzer\n"
                "Powered by: Anthropic Claude API\n"
                "Date: " + date_str + "\n"
                "Live App: https://yuvaraj-resume-analyzer.streamlit.app\n\n"
                + separator + "\n\n"
                + response_text + "\n\n"
                + separator + "\n"
                "Built by Yuvaraj Thatiparthi\n"
                "LinkedIn: linkedin.com/in/yuvaraj-thatiparthi\n"
                "GitHub: github.com/yuvaraj24799\n"
            )

            st.download_button(
                label="📥 Download Analysis Report",
                data=download_content,
                file_name="resume_analysis_" + timestamp + ".txt",
                mime="text/plain",
                use_container_width=True
            )

            st.success("Analysis complete! Use these insights to improve your resume!")

        except Exception as e:
            progress_bar.empty()
            status_text.empty()
            st.error("Error: " + str(e))
            st.info("Please check your internet connection or try again.")

# Footer
st.markdown("---")
col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    st.markdown("**🎯 AI Resume Analyzer**")
    st.markdown("Powered by Anthropic Claude API")
with col_f2:
    st.markdown("**👨‍💻 Built by**")
    st.markdown("[Yuvaraj Thatiparthi](https://linkedin.com/in/yuvaraj-thatiparthi)")
with col_f3:
    st.markdown("**💻 Source Code**")
    st.markdown("[github.com/yuvaraj24799](https://github.com/yuvaraj24799/resume-analyzer)")
