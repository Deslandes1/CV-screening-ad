The core reason your Streamlit deployment isn't loading correctly is hidden right at the very end of your provided code snippet:

```python
/[     UTC     ] Logs for cv-screening-ad-s2yaqezapp6nm5k6mvenv5r.streamlit.app/
...

```

You accidentally pasted Streamlit Community Cloud log data and file paths directly into the bottom of your Python script! Because `/[  UTC  ]...` is invalid syntax in Python, it causes a `SyntaxError` immediately when Streamlit tries to execute the file.

### How to Fix It

1. Open your `app.py` file.
2. Scroll all the way down to the very bottom.
3. Remove everything *after* the final line of your script:
```python

```



else:
main_app()

```
4. Save the file and push the changes back to your GitHub repository.

---

### Cleaned & Optimized `app.py` Code

Here is the fully cleaned up code with the trailing logs removed. I also squashed a subtle hidden bug in your file handling: Streamlit's `file_uploader` yields a file-like object that requires you to handle `read()` operations safely without double-consuming the buffer. 

Copy and paste this exact block into your `app.py`:

```python
import streamlit as st
import pandas as pd
import io
import os
import re
import random
from datetime import datetime

try:
    import pdfplumber
except ImportError:
    pdfplumber = None
try:
    import docx2txt
except ImportError:
    docx2txt = None

st.set_page_config(
    page_title="🌟 CV Screening Pro – GlobalInternet.py",
    page_icon="🎯",
    layout="wide"
)

st.markdown(
    """
    <style>
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    @keyframes floatStar {
        0% { transform: translateY(0px) rotate(0deg); opacity: 1; }
        100% { transform: translateY(-80px) rotate(30deg); opacity: 0; }
    }
    @keyframes bouncePointer {
        0%, 100% { transform: translateX(0); }
        50% { transform: translateX(15px); }
    }
    @keyframes glow {
        0% { box-shadow: 0 0 5px gold; }
        50% { box-shadow: 0 0 25px #ffaa33; }
        100% { box-shadow: 0 0 5px gold; }
    }
    .spinning-star {
        position: absolute;
        font-size: 28px;
        animation: spin 3s linear infinite;
        z-index: 10;
    }
    .floating-star {
        position: absolute;
        font-size: 22px;
        animation: floatStar 5s ease-in infinite;
        pointer-events: none;
        z-index: 5;
    }
    .pointing-hand {
        position: absolute;
        font-size: 45px;
        animation: bouncePointer 1.5s infinite;
        z-index: 20;
        filter: drop-shadow(2px 2px 2px rgba(0,0,0,0.5));
    }
    .stApp {
        background: radial-gradient(circle at 10% 20%, #ff9a3c, #ff4d4d, #2b2b2b);
        position: relative;
        overflow-x: hidden;
    }
    .job-card, .info-card {
        background: rgba(0,0,0,0.6) !important;
        backdrop-filter: blur(8px);
        border: 2px solid gold;
        border-radius: 25px;
        padding: 1rem;
        transition: transform 0.3s, box-shadow 0.3s;
        animation: glow 2s infinite;
    }
    .job-card:hover, .info-card:hover {
        transform: scale(1.02);
    }
    .stButton button {
        background: linear-gradient(90deg, #ffcc00, #ff9900) !important;
        color: #1e1e1e !important;
        font-weight: bold;
        border-radius: 50px !important;
        border: none;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        transition: 0.2s;
    }
    .stButton button:hover {
        transform: scale(1.05);
        background: linear-gradient(90deg, #ffdd55, #ffaa22) !important;
        color: black !important;
    }
    h1, h2, h3, p, div, span, label, .stMarkdown {
        color: white !important;
        text-shadow: 1px 1px 2px black;
    }
    .badge-cartoon {
        background: #ffcc00;
        color: #1e1e1e;
        border-radius: 30px;
        padding: 5px 15px;
        display: inline-block;
        font-weight: bold;
        font-size: 1.2rem;
        margin: 5px;
        box-shadow: 0 0 10px gold;
    }
    .sidebar .stSidebar {
        background: rgba(0,0,0,0.7);
    }
    footer {
        text-align: center;
        margin-top: 2rem;
        font-size: 0.8rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

def add_stars_and_pointers():
    spin_positions = [(5, 15), (90, 10), (15, 80), (85, 70), (45, 5)]
    for i, (x, y) in enumerate(spin_positions):
        st.markdown(f'<div class="spinning-star" style="left: {x}%; top: {y}%; animation-delay: {i}s;">⭐</div>', unsafe_allow_html=True)
    for _ in range(12):
        left = random.randint(2, 95)
        top = random.randint(2, 90)
        dur = random.uniform(3, 7)
        st.markdown(f'<div class="floating-star" style="left: {left}%; top: {top}%; animation-duration: {dur}s;">🌟</div>', unsafe_allow_html=True)
    pointer_positions = [(20, 50), (75, 30), (50, 80)]
    for (x, y) in pointer_positions:
        st.markdown(f'<div class="pointing-hand" style="left: {x}%; top: {y}%;">👉</div>', unsafe_allow_html=True)

add_stars_and_pointers()

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "job_positions" not in st.session_state:
    st.session_state.job_positions = pd.DataFrame({
        "id": [1, 2],
        "title": ["Senior Python Developer", "Data Scientist"],
        "description": ["Build web apps with Streamlit", "Analyse data and build ML models"],
        "required_skills": ["Python,Streamlit,API", "Python,SQL,Machine Learning"],
        "min_experience": [3, 2]
    })
if "applications" not in st.session_state:
    st.session_state.applications = pd.DataFrame(columns=["applicant_name", "email", "job_title", "score", "cv_text_preview", "date"])

def extract_text_from_pdf(file_bytes):
    if pdfplumber is None:
        return "PDF extraction not available."
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text
    except:
        return ""

def extract_text_from_docx(file_bytes):
    if docx2txt is None:
        return "DOCX extraction not available."
    try:
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name
        text = docx2txt.process(tmp_path)
        os.unlink(tmp_path)
        return text
    except:
        return ""

def extract_text_from_txt(file_bytes):
    try:
        return file_bytes.decode("utf-8")
    except:
        return ""

def extract_cv_text(uploaded_file):
    # Read bytes once so buffer remains healthy
    file_bytes = uploaded_file.getvalue()
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(file_bytes)
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return extract_text_from_docx(file_bytes)
    elif uploaded_file.type == "text/plain":
        return extract_text_from_txt(file_bytes)
    else:
        return "Unsupported file type."

def compute_match_score(cv_text, job_skills, job_description):
    cv_lower = cv_text.lower()
    skills_list = [s.strip().lower() for s in job_skills.split(",")]
    matches = sum(1 for skill in skills_list if skill in cv_lower)
    skill_score = (matches / len(skills_list)) * 100 if skills_list else 50
    desc_keywords = re.findall(r'\b\w{4,}\b', job_description.lower())
    desc_matches = sum(1 for kw in desc_keywords if kw in cv_lower)
    desc_score = (desc_matches / max(len(desc_keywords), 1)) * 100
    return round(skill_score * 0.7 + desc_score * 0.3, 2)

def login():
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown('<div style="text-align: center; font-size: 80px;">🎯👔🎯</div>', unsafe_allow_html=True)
        st.markdown("<h1 style='text-align:center;'>🌟 Applicant CV Screening Pro 🌟</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; font-size:1.2rem;'>The smartest recruitment assistant – powered by AI matching</p>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("<div style='text-align:center;'><span class='badge-cartoon'>🎉 HR Superpower 🎉</span> <span class='badge-cartoon'>⚡ Instant Scoring ⚡</span> <span class='badge-cartoon'>📄 PDF/DOCX Support</span></div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        password = st.text_input("🔐 Enter Admin Password", type="password")
        if st.button("🚀 Unlock the Magic"):
            if password == "20082010":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Wrong password. (Hint: try 20082010)")

def main_app():
    with st.sidebar:
        st.markdown('<div style="text-align:center; font-size:70px; animation: spin 3s linear infinite;">🤖</div>', unsafe_allow_html=True)
        st.markdown("### 🚀 GlobalInternet.py")
        st.markdown("**Gesner Deslandes** – *Engineer in Chief, Founder*")
        st.markdown("---")
        st.markdown("📧 deslandes78@gmail.com")
        st.markdown("📞 (509) 4738-5663")
        st.markdown("[🌐 Visit Website](https://globalinternetsitepy-abh7v6tnmskxxnuplrdcgk.streamlit.app/)")
        st.markdown("---")
        st.markdown("**Recruitment Tool v2.0** ✨")
        if st.button("🔓 Logout"):
            st.session_state.authenticated = False
            st.rerun()

    st.markdown('<div style="text-align:center;"><span style="font-size:50px;">⭐</span> <span style="font-size:60px;">👔</span> <span style="font-size:50px;">⭐</span></div>', unsafe_allow_html=True)
    st.title("🎯 Applicant CV Screening Software")
    st.markdown("<p style='font-size:1.3rem; text-align:center;'>✨ <strong>Automated screening – match candidates to jobs in seconds</strong> ✨</p>", unsafe_allow_html=True)
    st.markdown("---")

    tabs = st.tabs(["📌 Job Positions", "📝 Screen CV", "📊 Applications", "📧 Email Integration"])
    
    with tabs[0]:
        st.subheader("📋 Manage Job Positions")
        col1, col2 = st.columns([2,1])
        with col1:
            with st.expander("➕ Add New Position (click here)"):
                new_title = st.text_input("Job Title")
                new_desc = st.text_area("Job Description")
                new_skills = st.text_input("Required Skills (comma separated)")
                new_exp = st.number_input("Minimum Experience (years)", min_value=0, step=1)
                if st.button("➕ Add Position"):
                    if new_title and new_desc:
                        new_id = len(st.session_state.job_positions) + 1
                        new_row = pd.DataFrame({
                            "id": [new_id],
                            "title": [new_title],
                            "description": [new_desc],
                            "required_skills": [new_skills],
                            "min_experience": [new_exp]
                        })
                        st.session_state.job_positions = pd.concat([st.session_state.job_positions, new_row], ignore_index=True)
                        st.success(f"🎉 Position '{new_title}' added!")
                        st.rerun()
        with col2:
            st.markdown("#### 📌 Current Openings")
            if len(st.session_state.job_positions) > 0:
                for idx, row in st.session_state.job_positions.iterrows():
                    with st.container():
                        st.markdown(f'<div class="job-card"><strong>🎯 {row["title"]}</strong><br>{row["description"]}<br>✨ Skills: {row["required_skills"]}<br>⏱️ Min exp: {row["min_experience"]} yrs</div>', unsafe_allow_html=True)
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button(f"✏️ Edit", key=f"edit_{row['id']}"):
                                st.session_state.edit_id = row['id']
                                st.session_state.edit_title = row['title']
                                st.session_state.edit_desc = row['description']
                                st.session_state.edit_skills = row['required_skills']
                                st.session_state.edit_exp = row['min_experience']
                        with col_b:
                            if st.button(f"🗑️ Delete", key=f"del_{row['id']}"):
                                st.session_state.job_positions = st.session_state.job_positions[st.session_state.job_positions['id'] != row['id']]
                                st.rerun()
                if 'edit_id' in st.session_state:
                    st.markdown("---")
                    st.subheader(f"✏️ Editing: {st.session_state.edit_title}")
                    new_title = st.text_input("Title", value=st.session_state.edit_title)
                    new_desc = st.text_area("Description", value=st.session_state.edit_desc)
                    new_skills = st.text_input("Skills", value=st.session_state.edit_skills)
                    new_exp = st.number_input("Experience", value=int(st.session_state.edit_exp))
                    if st.button("💾 Save Changes"):
                        idx = st.session_state.job_positions[st.session_state.job_positions['id'] == st.session_state.edit_id].index[0]
                        st.session_state.job_positions.at[idx, 'title'] = new_title
                        st.session_state.job_positions.at[idx, 'description'] = new_desc
                        st.session_state.job_positions.at[idx, 'required_skills'] = new_skills
                        st.session_state.job_positions.at[idx, 'min_experience'] = new_exp
                        del st.session_state.edit_id
                        st.rerun()
            else:
                st.info("No job positions yet. Click the '+' above to add one.")
    
    with tabs[1]:
        st.subheader("📄 CV Screening Portal")
        st.markdown("<div style='background:rgba(0,0,0,0.5); border-radius:20px; padding:15px;'><span class='badge-cartoon'>⚡ Upload CV</span> <span class='badge-cartoon'>🎯 Get Match Score</span> <span class='badge-cartoon'>📧 Automatic Recording</span></div>", unsafe_allow_html=True)
        applicant_name = st.text_input("👤 Applicant Full Name")
        applicant_email = st.text_input("📧 Applicant Email")
        uploaded_cv = st.file_uploader("📎 Upload CV (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])
        job_options = st.session_state.job_positions['title'].tolist()
        selected_job = st.selectbox("🎯 Select Target Job", job_options) if job_options else None
        
        if st.button("🔍 Analyse CV & Score") and uploaded_cv and applicant_name and selected_job:
            with st.spinner("✨ Scanning CV with smart algorithm..."):
                cv_text = extract_cv_text(uploaded_cv)
                if cv_text and len(cv_text) > 50:
                    job_row = st.session_state.job_positions[st.session_state.job_positions['title'] == selected_job].iloc[0]
                    score = compute_match_score(cv_text, job_row['required_skills'], job_row['description'])
                    new_app = pd.DataFrame({
                        "applicant_name": [applicant_name],
                        "email": [applicant_email],
                        "job_title": [selected_job],
                        "score": [score],
                        "cv_text_preview": [cv_text[:500] + "..."],
                        "date": [datetime.now().strftime("%Y-%m-%d %H:%M")]
                    })
                    st.session_state.applications = pd.concat([st.session_state.applications, new_app], ignore_index=True)
                    st.balloons()
                    st.success(f"✅ Match Score: {score}%")
                    if score >= 70:
                        st.markdown(f'<p class="score-high">🌟 TOP CANDIDATE – {score}% match</p>', unsafe_allow_html=True)
                    elif score >= 50:
                        st.markdown(f'<p class="score-medium">📌 Potential – {score}% match</p>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<p class="score-low">❌ Low compatibility – {score}%</p>', unsafe_allow_html=True)
                    st.info("📨 Application stored. An email notification would be sent to both applicant and admin.")
                else:
                    st.error("Could not read CV text. Try a clearer file.")
        elif not selected_job:
            st.warning("👉 First, create job positions in the previous tab.")
    
    with tabs[2]:
        st.subheader("📋 All Applications")
        if len(st.session_state.applications) > 0:
            st.dataframe(st.session_state.applications[["applicant_name", "email", "job_title", "score", "date"]], use_container_width=True)
            csv = st.session_state.applications.to_csv(index=False)
            st.download_button("📥 Download CSV Report", data=csv, file_name="applications.csv")
            selected_app = st.selectbox("🔍 View CV preview", st.session_state.applications['applicant_name'].tolist())
            app_row = st.session_state.applications[st.session_state.applications['applicant_name'] == selected_app].iloc[0]
            st.text_area("CV Text Preview", app_row['cv_text_preview'], height=200)
        else:
            st.info("No applications yet. Upload some CVs to see magic happen.")
    
    with tabs[3]:
        st.subheader("📧 Seamless Integration")
        st.markdown("""
        <div style="background: rgba(255,215,0,0.2); border-radius: 20px; padding: 1rem;">
        <p>✅ <strong>Direct CV upload via this portal</strong> – instant scoring and storage.<br>
        ✅ <strong>Admin email:</strong> deslandes78@gmail.com – you will be notified of each new application.<br>
        ✅ <strong>Advanced option:</strong> Connect your Gmail/Outlook to auto‑fetch CV attachments. Contact us for custom setup.<br>
        🎯 <strong>Pricing:</strong> Full software license – $299 USD. One‑time payment, lifetime updates.
        </p>
        </div>
        """, unsafe_allow_html=True)
        st.info("📩 For custom email integration or purchase inquiry, email deslandes78@gmail.com or WhatsApp (509) 4738-5663.")
    
    st.markdown("---")
    st.markdown("<div style='text-align:center;'><span>🎈</span> <span>© 2025 GlobalInternet.py – Built by Gesner Deslandes</span> <span>🎈</span></div>", unsafe_allow_html=True)
    st.markdown("<div style='text-align:center;'><span class='badge-cartoon'>🚀 Hire smarter, not harder</span></div>", unsafe_allow_html=True)

if not st.session_state.authenticated:
    login()
else:
    main_app()

```
