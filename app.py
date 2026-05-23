import streamlit as st
import pandas as pd
import io
import os
import re
import random
from datetime import datetime

# Safe imports for extraction tools
try:
    import pdfplumber
except ImportError:
    pdfplumber = None
try:
    import docx2txt
except ImportError:
    docx2txt = None

# 1. Page Configuration
st.set_page_config(
    page_title="🎯 CV Screening Pro – GlobalInternet.py",
    page_icon="🎯",
    layout="wide"
)

# 2. Heavy-Duty Cartoon Aesthetic Custom CSS Styles
st.markdown(
    """
    <style>
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    @keyframes pulseGlow {
        0% { box-shadow: 0 0 10px #ffcc00; transform: scale(1); }
        50% { box-shadow: 0 0 30px #ff3300; transform: scale(1.02); }
        100% { box-shadow: 0 0 10px #ffcc00; transform: scale(1); }
    }
    .stApp {
        background: radial-gradient(circle at 50% 50%, #222222, #111111);
        color: #ffffff !important;
    }
    .main-ad-card {
        background: linear-gradient(145deg, rgba(255, 153, 0, 0.15), rgba(255, 51, 0, 0.15)) !important;
        backdrop-filter: blur(12px);
        border: 3px dashed #ffcc00;
        border-radius: 30px;
        padding: 2.5rem;
        margin: 20px auto;
        animation: pulseGlow 4s infinite ease-in-out;
        text-align: center;
    }
    .badge-cartoon {
        background: #ffcc00 !important;
        color: #111111 !important;
        border-radius: 40px;
        padding: 8px 20px;
        display: inline-block;
        font-weight: 900;
        font-size: 1.1rem;
        margin: 8px;
        box-shadow: 0 5px 0px #cc9900;
        text-transform: uppercase;
    }
    .premium-price-tag {
        font-size: 3.5rem !important;
        font-weight: 900 !important;
        color: #ffcc00 !important;
        text-shadow: 3px 3px 0px #ff3300, 5px 5px 0px #000;
        margin: 15px 0;
    }
    .stButton button {
        background: linear-gradient(90deg, #ffcc00, #ff6600) !important;
        color: #000000 !important;
        font-weight: 900 !important;
        font-size: 1.3rem !important;
        border-radius: 50px !important;
        border: 3px solid #ffffff !important;
        box-shadow: 0 8px 0px #cc4400 !important;
        padding: 12px 35px !important;
        transition: all 0.1s ease-in-out;
    }
    .stButton button:hover {
        transform: translateY(3px) !important;
        box-shadow: 0 4px 0px #cc4400 !important;
        background: linear-gradient(90deg, #ffea00, #ff3300) !important;
    }
    h1, h2, h3, h4, p, span, label {
        color: #ffffff !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
        font-family: 'Arial Black', Gadget, sans-serif;
    }
    .sidebar-brand {
        text-align: center;
        background: rgba(0,0,0,0.4);
        padding: 15px;
        border-radius: 20px;
        border: 2px solid #ff9900;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 3. Handle Session State Initialization
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "job_positions" not in st.session_state:
    st.session_state.job_positions = pd.DataFrame({
        "id": [1, 2],
        "title": ["Senior Python Developer", "Data Scientist"],
        "description": ["Build web apps with Streamlit and robust APIs", "Analyze big data structures and train ML models"],
        "required_skills": ["Python,Streamlit,API", "Python,SQL,Machine Learning"],
        "min_experience": [3, 2]
    })
if "applications" not in st.session_state:
    st.session_state.applications = pd.DataFrame(columns=["applicant_name", "email", "job_title", "score", "cv_text_preview", "date"])

# --- CORE UTILITY FUNCTIONS ---
def extract_cv_text(uploaded_file):
    file_bytes = uploaded_file.getvalue()
    if uploaded_file.type == "application/pdf" and pdfplumber is not None:
        try:
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                return "".join([page.extract_text() or "" for page in pdf.pages])
        except: return ""
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document" and docx2txt is not None:
        try:
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
                tmp.write(file_bytes)
                tmp_path = tmp.name
            text = docx2txt.process(tmp_path)
            os.unlink(tmp_path)
            return text
        except: return ""
    try:
        return file_bytes.decode("utf-8")
    except:
        return "Unsupported or unreadable format."

def compute_match_score(cv_text, job_skills, job_description):
    cv_lower = cv_text.lower()
    skills = [s.strip().lower() for s in job_skills.split(",") if s.strip()]
    matches = sum(1 for skill in skills if skill in cv_lower)
    skill_score = (matches / len(skills)) * 100 if skills else 50
    keywords = re.findall(r'\b\w{4,}\b', job_description.lower())
    kw_matches = sum(1 for kw in keywords if kw in cv_lower)
    desc_score = (kw_matches / max(len(keywords), 1)) * 100
    return round(skill_score * 0.7 + desc_score * 0.3, 2)


# --- INTERFACE ONE: POWERFUL SALES AD & GATEWAY ---
def show_powerful_sales_ad():
    col1, col2, col3 = st.columns([1, 6, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(
            """
            <div class="main-ad-card">
                <div style="font-size: 90px; margin-bottom: 10px;">⚡🎯🤖</div>
                <h1 style="font-size: 3rem; margin: 0; color: #ffcc00 !important;">GLOBALINTERNET.PY PRESENTS</h1>
                <h2 style="font-size: 2.2rem; color: #ffffff; margin-top: 5px;">Applicant CV Screening Pro v2.0</h2>
                <p style="font-size: 1.3rem; max-width: 750px; margin: 15px auto; color: #ddd !important;">
                    Stop drowning in stacks of resumes. Instantly scan, score, parse, and match applicants to your active job vacancies with our military-grade Python extraction system.
                </p>
                <div style="margin: 25px 0;">
                    <span class="badge-cartoon">⚡ ZERO SUBSCRIPTIONS</span>
                    <span class="badge-cartoon">🔥 100% SOURCE CODE INCLUDED</span>
                    <span class="badge-cartoon">🚀 UNLIMITED CV SCANS</span>
                    <span class="badge-cartoon">📥 EXPORT TO EXCEL/CSV</span>
                </div>
                <hr style="border: 1px dashed #ff9900; margin: 30px 0;">
                <h3 style="margin-bottom: 0px; letter-spacing: 1px;">OWN THE LIFETIME LICENSE TODAY</h3>
                <div class="premium-price-tag">$299 USD</div>
                <p style="font-size: 1.1rem; color: #ffcc00 !important; font-weight: bold;">One-Time Payment • Full Updates • Instant Local Setup</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Centered Administrative Gateway Barrier
        st.markdown("<br>", unsafe_allow_html=True)
        with st.container():
            st.markdown("<h3 style='text-align: center; color: #ffcc00 !important;'>🔐 Enter Admin Key to Launch Core System</h3>", unsafe_allow_html=True)
            pass_col1, pass_col2, pass_col3 = st.columns([1, 2, 1])
            with pass_col2:
                password = st.text_input("", type="password", placeholder="Enter authorization key...", label_visibility="collapsed")
                st.markdown("<div style='text-align: center; margin-top: 15px;'>", unsafe_allow_html=True)
                if st.button("🚀 UNLOCK THE ENGINE"):
                    if password == "20082010":
                        st.session_state.authenticated = True
                        st.rerun()
                    else:
                        st.error("❌ Invalid License Activation Key. (Hint: 20082010)")
                st.markdown("</div>", unsafe_allow_html=True)


# --- INTERFACE TWO: THE WORKHORSE DASHBOARD ---
def show_main_dashboard():
    # Structural Sidebar Configuration
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-brand">
                <span style="font-size: 60px;">🤖</span>
                <h3 style="margin: 10px 0 5px 0; color: #ffcc00 !important;">GlobalInternet.py</h3>
                <p style="font-size: 0.9rem; margin: 0; font-weight: bold;">Gesner Deslandes</p>
                <p style="font-size: 0.8rem; color: #bbb !important; margin: 0;">Engineer in Chief & Founder</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        st.markdown("---")
        st.markdown("### 📞 Instant Contact")
        st.markdown("📧 **deslandes78@gmail.com**")
        st.markdown("📱 **(509) 4738-5663**")
        st.markdown("[🌐 Main Commercial Suite](https://globalinternetsitepy-abh7v6tnmskxxnuplrdcgk.streamlit.app/)")
        st.markdown("---")
        if st.button("🔒 Lock Console"):
            st.session_state.authenticated = False
            st.rerun()

    # Content Headers
    st.title("🎯 Recruitment Command Center")
    st.markdown("### Automated parsing & matching pipeline active.")
    st.markdown("---")

    tabs = st.tabs(["📌 Job Vacancies", "📝 Screen Candidates", "📊 Analytics & Reports", "📧 System Integrations"])
    
    # TAB 1: JOB VACANCY ENGINE
    with tabs[0]:
        st.subheader("📋 Core Structural Openings")
        col_left, col_right = st.columns([2,1])
        with col_left:
            with st.expander("➕ Provision New Position Profile"):
                new_title = st.text_input("Official Title")
                new_desc = st.text_area("Scope of Operations / Description")
                new_skills = st.text_input("Target Skills Matrix (Comma Separated Keyphrases)")
                new_exp = st.number_input("Minimum Experience Threshold (Years)", min_value=0, step=1)
                if st.button("💾 Deploy Position"):
                    if new_title and new_desc:
                        new_id = len(st.session_state.job_positions) + 1
                        new_row = pd.DataFrame({
                            "id": [new_id], "title": [new_title], "description": [new_desc],
                            "required_skills": [new_skills], "min_experience": [new_exp]
                        })
                        st.session_state.job_positions = pd.concat([st.session_state.job_positions, new_row], ignore_index=True)
                        st.success(f"Deployed new vacancy track: {new_title}")
                        st.rerun()
        with col_right:
            st.markdown("#### Active Target Vectors")
            for idx, row in st.session_state.job_positions.iterrows():
                st.markdown(
                    f"""
                    <div style='background: rgba(0,0,0,0.4); border: 1px solid #ffcc00; padding: 12px; border-radius:15px; margin-bottom:10px;'>
                        <strong>🎯 {row['title']}</strong><br>
                        <small style='color:#bbb;'>Skills: {row['required_skills']}</small>
                    </div>
                    """, unsafe_allow_html=True
                )
                if st.button("🗑️ Terminate Track", key=f"del_{row['id']}"):
                    st.session_state.job_positions = st.session_state.job_positions[st.session_state.job_positions['id'] != row['id']]
                    st.rerun()

    # TAB 2: ACTIVE PARSING GATEWAY
    with tabs[1]:
        st.subheader("📄 Automated Screening Portal")
        app_name = st.text_input("Candidate Full Legal Identity Name")
        app_email = st.text_input("Communication Channel Email")
        uploaded_cv = st.file_uploader("Drop CV Asset File Here (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"])
        job_list = st.session_state.job_positions['title'].tolist()
        target_job = st.selectbox("Assign Evaluation Objective Vector", job_list) if job_list else None
        
        if st.button("🔍 INITIATE ALGORITHMIC ANALYSIS") and uploaded_cv and app_name and target_job:
            with st.spinner("Executing sequence parsing algorithms..."):
                cv_text = extract_cv_text(uploaded_cv)
                if len(cv_text) > 10:
                    job_data = st.session_state.job_positions[st.session_state.job_positions['title'] == target_job].iloc[0]
                    match_score = compute_match_score(cv_text, job_data['required_skills'], job_data['description'])
                    
                    new_entry = pd.DataFrame({
                        "applicant_name": [app_name], "email": [app_email], "job_title": [target_job],
                        "score": [match_score], "cv_text_preview": [cv_text[:500] + "..."],
                        "date": [datetime.now().strftime("%Y-%m-%d %H:%M")]
                    })
                    st.session_state.applications = pd.concat([st.session_state.applications, new_entry], ignore_index=True)
                    st.balloons()
                    st.metric(label="Match Quality Output Matrix", value=f"{match_score}%")
                else:
                    st.error("Error: Processing framework could not capture standard document body data strings.")

    # TAB 3: SYSTEM HISTOGRAMS & ANALYTICS
    with tabs[2]:
        st.subheader("📊 Performance Matrix & Database Analytics")
        if len(st.session_state.applications) > 0:
            st.dataframe(st.session_state.applications[["applicant_name", "email", "job_title", "score", "date"]], use_container_width=True)
            csv_data = st.session_state.applications.to_csv(index=False)
            st.download_button("📥 Extraction Database Log Dump (CSV)", data=csv_data, file_name="screening_report.csv")
        else:
            st.info("System logging nodes are current listening. Run analysis tasks to build database tracks.")

    # TAB 4: EXTENDED CUSTOM SERVICES
    with tabs[3]:
        st.subheader("📧 Webhook & Corporate Mail Integration")
        st.markdown(
            """
            <div style="background: rgba(255,255,255,0.05); border-radius: 20px; padding: 20px; border-left: 5px solid #ffcc00;">
                <h4>✨ Enterprise Extensions Available</h4>
                <p>Need direct IMAP routing to pull attachments instantly out of your incoming corporate email loops? We build fully isolated custom microservices to feed your parsing pool dynamically.</p>
                <strong>Inquire via support arrays:</strong> deslandes78@gmail.com
            </div>
            """, unsafe_allow_html=True
        )

# --- EXECUTION ROOT ---
if not st.session_state.authenticated:
    show_powerful_sales_ad()
else:
    show_main_dashboard()
