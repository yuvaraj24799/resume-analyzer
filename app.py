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
    .history-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 0.5rem 0;
    }
    .rewriter-box {
        background: #f0fff4;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #00b09b;
        margin: 0.5rem 0;
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
    st.markdown("**Features:**")
    st.write("✅ Match score with visual gauge")
    st.write("✅ Matching skills detected")
    st.write("✅ Missing skills identified")
    st.write("✅ Personalized recommendations")
    st.write("✅ ATS keywords to add")
    st.write("✅ Download analysis report")
    st.write("✅ Resume bullet rewriter")
    st.write("✅ Compare two resumes")
    st.write("✅ Analysis history")
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

# Initialize session state for history
if "analysis_history" not in st.session_state:
    st.session_state.analysis_history = []

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

# Tabs for different features
tab1, tab2, tab3, tab4 = st.tabs([
    "🎯 Analyze Match",
    "✍️ Resume Rewriter",
    "⚖️ Compare Resumes",
    "📚 History"
])

# ============================================================
# TAB 1 — ANALYZE MATCH
# ============================================================
with tab1:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📄 Your Resume")
        resume_file = st.file_uploader(
            "Upload Resume (PDF, DOCX, or TXT)",
            type=["pdf", "docx", "txt"],
            key="resume_upload_tab1"
        )
        resume_text_input = st.text_area(
            "Or paste resume text here",
            height=200,
            placeholder="Paste your resume content here...",
            key="resume_text_tab1"
        )

    with col2:
        st.subheader("💼 Job Description")
        jd_text_input = st.text_area(
            "Paste the job description here",
            height=350,
            placeholder="Paste the full job description here...",
            key="jd_text_tab1"
        )

    resume_text = ""
    if resume_file is not None:
        with st.spinner("Reading your resume..."):
            resume_text = extract_text_from_file(resume_file)
        if resume_text:
            st.success("Resume loaded successfully!")
    elif resume_text_input:
        resume_text = resume_text_input

    st.markdown("---")
    analyze_button = st.button(
        "🚀 Analyze Match",
        type="primary",
        use_container_width=True,
        key="analyze_btn"
    )

    if analyze_button:
        if not api_key:
            st.error("API key not configured.")
        elif not resume_text:
            st.error("Please upload or paste your resume.")
        elif not jd_text_input:
            st.error("Please paste the job description.")
        elif len(jd_text_input) < 50:
            st.error("Job description seems too short.")
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
                    "[Single number from 0-100]\n\n"
                    "## Summary\n"
                    "[2-3 sentences explaining the overall fit]\n\n"
                    "## Matching Skills Found\n"
                    "[List 5-10 matching skills as bullet points]\n\n"
                    "## Missing Skills or Experience\n"
                    "[List 3-7 missing skills as bullet points]\n\n"
                    "## Specific Recommendations\n"
                    "[List 4-5 actionable recommendations as bullet points]\n\n"
                    "## ATS Keywords to Add\n"
                    "[List 8-10 exact keywords as bullet points]\n\n"
                    "## Interview Talking Points\n"
                    "[List 3 strong talking points as bullet points]\n\n"
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
                        delta = "Strong Match" if score >= 70 else "Needs Work"
                        st.metric("Match Score", str(score) + "/100", delta)
                    with met2:
                        if score >= 80:
                            st.metric("Interview Chance", "High", "Apply Now!")
                        elif score >= 65:
                            st.metric("Interview Chance", "Medium", "Good Fit")
                        else:
                            st.metric("Interview Chance", "Lower", "Improve First")
                    with met3:
                        st.metric("Analysis By", "Claude AI", "Anthropic")

                    # Save to history
                    st.session_state.analysis_history.append({
                        "date": datetime.now().strftime("%b %d, %Y %I:%M %p"),
                        "score": score,
                        "jd_snippet": jd_text_input[:100] + "...",
                        "result": response_text
                    })

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

# ============================================================
# TAB 2 — RESUME REWRITER
# ============================================================
with tab2:
    st.subheader("✍️ AI Resume Bullet Rewriter")
    st.write("Paste a weak resume bullet point and Claude will rewrite it to be stronger, more impactful, and ATS-optimized.")

    col_rw1, col_rw2 = st.columns(2)

    with col_rw1:
        weak_bullet = st.text_area(
            "Paste your weak bullet point here",
            height=150,
            placeholder="Example: Helped with cloud infrastructure tasks and fixed some issues...",
            key="weak_bullet"
        )
        job_context = st.text_input(
            "Target job role (optional)",
            placeholder="Example: AI Engineer, Software Developer, Data Analyst",
            key="job_context"
        )

    with col_rw2:
        st.markdown("**Tips for better rewrites:**")
        st.write("✅ Include any numbers you remember (%, $, hours saved)")
        st.write("✅ Mention the tools or technologies you used")
        st.write("✅ Describe what problem you solved")
        st.write("✅ Add your target job role for tailored rewrites")

    rewrite_button = st.button(
        "✨ Rewrite This Bullet",
        type="primary",
        use_container_width=True,
        key="rewrite_btn"
    )

    if rewrite_button:
        if not api_key:
            st.error("API key not configured.")
        elif not weak_bullet:
            st.error("Please paste a bullet point to rewrite.")
        else:
            with st.spinner("Claude is rewriting your bullet point..."):
                try:
                    client = anthropic.Anthropic(api_key=api_key)

                    rewrite_prompt = (
                        "You are an expert resume writer. Rewrite the following weak resume bullet point "
                        "to be strong, impactful, ATS-optimized, and follow the Action Verb + Task + Result format.\n\n"
                        "Weak bullet: " + weak_bullet + "\n"
                        + ("Target role: " + job_context + "\n" if job_context else "") +
                        "\nProvide 3 different rewritten versions, each stronger than the last.\n\n"
                        "Format exactly like this:\n\n"
                        "**Version 1 (Conservative):**\n"
                        "[rewritten bullet]\n\n"
                        "**Version 2 (Strong):**\n"
                        "[rewritten bullet]\n\n"
                        "**Version 3 (Most Impactful):**\n"
                        "[rewritten bullet]\n\n"
                        "**Why these are better:**\n"
                        "[2-3 sentences explaining what was improved]\n\n"
                        "**Keywords added:**\n"
                        "[list the ATS keywords added]"
                    )

                    message = client.messages.create(
                        model="claude-sonnet-4-5",
                        max_tokens=1000,
                        messages=[{"role": "user", "content": rewrite_prompt}]
                    )

                    rewrite_result = message.content[0].text

                    st.markdown("---")
                    st.markdown("### 📝 Original Bullet:")
                    st.markdown(
                        '<div class="history-card">' + weak_bullet + '</div>',
                        unsafe_allow_html=True
                    )

                    st.markdown("### ✨ Rewritten Versions:")
                    st.markdown(
                        '<div class="rewriter-box">' + rewrite_result.replace('\n', '<br>') + '</div>',
                        unsafe_allow_html=True
                    )

                    st.download_button(
                        label="📥 Download Rewritten Bullets",
                        data="ORIGINAL:\n" + weak_bullet + "\n\nREWRITTEN VERSIONS:\n" + rewrite_result,
                        file_name="rewritten_bullets.txt",
                        mime="text/plain",
                        use_container_width=True
                    )

                except Exception as e:
                    st.error("Error: " + str(e))

# ============================================================
# TAB 3 — COMPARE RESUMES
# ============================================================
with tab3:
    st.subheader("⚖️ Compare Two Resumes")
    st.write("Paste the same job description and two different resumes to see which one scores higher.")

    jd_compare = st.text_area(
        "Job Description (same for both)",
        height=150,
        placeholder="Paste the job description here...",
        key="jd_compare"
    )

    col_c1, col_c2 = st.columns(2)

    with col_c1:
        st.markdown("### 📄 Resume A")
        resume_a = st.text_area(
            "Paste Resume A",
            height=250,
            placeholder="Paste first resume here...",
            key="resume_a"
        )

    with col_c2:
        st.markdown("### 📄 Resume B")
        resume_b = st.text_area(
            "Paste Resume B",
            height=250,
            placeholder="Paste second resume here...",
            key="resume_b"
        )

    compare_button = st.button(
        "⚖️ Compare Both Resumes",
        type="primary",
        use_container_width=True,
        key="compare_btn"
    )

    if compare_button:
        if not api_key:
            st.error("API key not configured.")
        elif not jd_compare:
            st.error("Please paste the job description.")
        elif not resume_a or not resume_b:
            st.error("Please paste both resumes.")
        else:
            with st.spinner("Claude is analyzing both resumes..."):
                try:
                    client = anthropic.Anthropic(api_key=api_key)

                    compare_prompt = (
                        "You are an expert recruiter. Compare these two resumes against the job description.\n\n"
                        "JOB DESCRIPTION:\n" + jd_compare + "\n\n"
                        "RESUME A:\n" + resume_a + "\n\n"
                        "RESUME B:\n" + resume_b + "\n\n"
                        "Provide analysis in this EXACT format:\n\n"
                        "## Resume A Score\n"
                        "[Single number 0-100]\n\n"
                        "## Resume B Score\n"
                        "[Single number 0-100]\n\n"
                        "## Winner\n"
                        "[State which resume is stronger and why in 2 sentences]\n\n"
                        "## Resume A Strengths\n"
                        "[3-5 bullet points]\n\n"
                        "## Resume B Strengths\n"
                        "[3-5 bullet points]\n\n"
                        "## How to Improve the Losing Resume\n"
                        "[4-5 specific recommendations as bullet points]\n\n"
                        "Be specific and honest."
                    )

                    message = client.messages.create(
                        model="claude-sonnet-4-5",
                        max_tokens=2000,
                        messages=[{"role": "user", "content": compare_prompt}]
                    )

                    compare_result = message.content[0].text

                    st.markdown("---")
                    st.markdown("## ⚖️ Comparison Results")

                    score_a = None
                    score_b = None
                    lines = compare_result.split('\n')
                    for i, line in enumerate(lines):
                        if 'Resume A Score' in line:
                            for j in range(i+1, min(i+4, len(lines))):
                                nums = re.findall(r'\b(\d{1,3})\b', lines[j])
                                for n in nums:
                                    if 0 <= int(n) <= 100:
                                        score_a = int(n)
                                        break
                        if 'Resume B Score' in line:
                            for j in range(i+1, min(i+4, len(lines))):
                                nums = re.findall(r'\b(\d{1,3})\b', lines[j])
                                for n in nums:
                                    if 0 <= int(n) <= 100:
                                        score_b = int(n)
                                        break

                    if score_a and score_b:
                        col_ca, col_cb = st.columns(2)
                        with col_ca:
                            show_score_gauge(score_a)
                            st.markdown("### Resume A")
                        with col_cb:
                            show_score_gauge(score_b)
                            st.markdown("### Resume B")

                    st.markdown(compare_result)

                except Exception as e:
                    st.error("Error: " + str(e))

# ============================================================
# TAB 4 — HISTORY
# ============================================================
with tab4:
    st.subheader("📚 Analysis History")
    st.write("Your recent analyses from this session are saved here.")

    if not st.session_state.analysis_history:
        st.info("No analyses yet. Run your first analysis in the Analyze Match tab!")
    else:
        st.write("**Total analyses this session:** " + str(len(st.session_state.analysis_history)))

        for i, item in enumerate(reversed(st.session_state.analysis_history)):
            with st.expander("Analysis " + str(len(st.session_state.analysis_history) - i) + " | Score: " + str(item['score']) + "/100 | " + item['date']):
                st.write("**Job Description Preview:** " + item['jd_snippet'])
                st.markdown(item['result'])

        if st.button("Clear History", key="clear_history"):
            st.session_state.analysis_history = []
            st.rerun()

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
