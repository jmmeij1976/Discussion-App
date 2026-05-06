# app.py — Student Introduction Generator (Streamlit Web App)
#
# Deploy free at: https://streamlit.io/cloud
# Required secrets (set in Streamlit Cloud dashboard):
#   ANTHROPIC_API_KEY, GITHUB_TOKEN, GITHUB_USERNAME, GITHUB_REPO,
#   CANVAS_URL, CANVAS_TOKEN, COURSE_ID, DISCUSSION_ID

import csv
import os
import base64
import requests
import anthropic
import streamlit as st

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="Student Introduction Generator",
    page_icon="🎓",
    layout="centered"
)

# ─────────────────────────────────────────────
# CUSTOM STYLING
# ─────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

h1, h2, h3 {
    font-family: 'DM Serif Display', serif !important;
}

.stApp {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    min-height: 100vh;
}

.main-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 20px;
    padding: 2.5rem;
    backdrop-filter: blur(12px);
    margin-bottom: 1.5rem;
}

.intro-box {
    background: rgba(99, 230, 190, 0.08);
    border-left: 4px solid #63e6be;
    border-radius: 12px;
    padding: 1.5rem 2rem;
    color: #e0fff7;
    font-size: 1.05rem;
    line-height: 1.8;
    margin: 1rem 0;
}

.step-badge {
    display: inline-block;
    background: #63e6be;
    color: #0f2027;
    font-weight: 600;
    font-size: 0.75rem;
    padding: 2px 10px;
    border-radius: 20px;
    margin-bottom: 0.5rem;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

.success-banner {
    background: linear-gradient(90deg, #63e6be22, #63e6be11);
    border: 1px solid #63e6be55;
    border-radius: 12px;
    padding: 1rem 1.5rem;
    color: #63e6be;
    font-weight: 500;
    margin: 0.5rem 0;
}

section[data-testid="stSidebar"] { display: none; }

.stTextInput > label, .stTextArea > label {
    color: #b0c4d8 !important;
    font-size: 0.9rem !important;
    font-weight: 500 !important;
}

div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 10px !important;
    color: #ffffff !important;
}

div[data-testid="stTextInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus {
    border-color: #63e6be !important;
    box-shadow: 0 0 0 2px rgba(99,230,190,0.2) !important;
}

.stButton > button {
    background: linear-gradient(135deg, #63e6be, #38d9a9) !important;
    color: #0f2027 !important;
    font-weight: 700 !important;
    font-family: 'DM Sans', sans-serif !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.75rem 2.5rem !important;
    font-size: 1rem !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 25px rgba(99,230,190,0.35) !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SECRETS
# ─────────────────────────────────────────────

def get_secret(key):
    """Get from Streamlit secrets or environment variable."""
    try:
        return st.secrets[key]
    except Exception:
        return os.environ.get(key, "")

ANTHROPIC_API_KEY = get_secret("ANTHROPIC_API_KEY")
GITHUB_TOKEN      = get_secret("GITHUB_TOKEN")
GITHUB_USERNAME   = get_secret("GITHUB_USERNAME")
GITHUB_REPO       = get_secret("GITHUB_REPO")
GITHUB_BRANCH     = get_secret("GITHUB_BRANCH") or "main"
CANVAS_URL        = get_secret("CANVAS_URL")
CANVAS_TOKEN      = get_secret("CANVAS_TOKEN")
COURSE_ID         = get_secret("COURSE_ID")
DISCUSSION_ID     = get_secret("DISCUSSION_ID")
CSV_FILENAME      = "student_introductions.csv"

# ─────────────────────────────────────────────
# QUESTIONS
# ─────────────────────────────────────────────

questions = [
    ("name",        "What is your name?"),
    ("major",       "What is your major?"),
    ("enrolled",    "What made you enroll in this course?"),
    ("excited",     "What are you most excited to learn in this course?"),
    ("fear",        "What is your biggest fear about this course?"),
    ("three_things","What are three things about yourself people cannot tell by looking at you?"),
    ("contact",     "What is the best way to contact you? (email or phone)"),
    ("professor",   "What would you like to know about the professor?"),
]

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def generate_ai_introduction(answers: dict) -> str:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    qa_text = "\n".join(f"Q: {q}\nA: {answers[k]}" for k, q in questions)
    prompt = f"""You are helping a student write a warm, engaging, and professional introduction post for an online course discussion thread.

Based on the student's answers below, write a polished 3-4 sentence introduction paragraph.
Make it friendly, personal, and natural — not robotic. Write in first person as the student.

{qa_text}

Write only the introduction paragraph, nothing else."""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text.strip()


def save_and_upload_csv(answers: dict) -> str:
    rows_exist = os.path.isfile(CSV_FILENAME)
    with open(CSV_FILENAME, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not rows_exist:
            writer.writerow([q for _, q in questions])
        writer.writerow([answers[k] for k, _ in questions])

    with open(CSV_FILENAME, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf-8")

    api_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/{CSV_FILENAME}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github+json"}
    existing = requests.get(api_url, headers=headers)
    sha = existing.json().get("sha") if existing.status_code == 200 else None

    payload = {"message": f"Add student intro: {answers['name']}", "content": content, "branch": GITHUB_BRANCH}
    if sha:
        payload["sha"] = sha

    requests.put(api_url, headers=headers, json=payload).raise_for_status()

    return f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{GITHUB_REPO}/{GITHUB_BRANCH}/{CSV_FILENAME}"


def post_to_canvas(introduction: str, csv_url: str):
    api_url = f"{CANVAS_URL}/api/v1/courses/{COURSE_ID}/discussion_topics/{DISCUSSION_ID}/entries"
    headers = {"Authorization": f"Bearer {CANVAS_TOKEN}"}
    message = (
        f"<p>{introduction}</p>"
        f"<hr/><p><small>📊 <a href='{csv_url}' target='_blank'>View all introductions (CSV)</a></small></p>"
    )
    requests.post(api_url, headers=headers, json={"message": message}).raise_for_status()

# ─────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────

st.markdown("<h1 style='color:#63e6be; margin-bottom:0.25rem;'>🎓 Student Introduction</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#b0c4d8; margin-bottom:2rem;'>Fill out the form below — AI will craft your introduction and post it to Canvas automatically.</p>", unsafe_allow_html=True)

with st.form("intro_form"):
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.markdown('<span class="step-badge">Step 1 — About You</span>', unsafe_allow_html=True)

    answers = {}
    for key, question in questions:
        if key == "three_things":
            answers[key] = st.text_area(question, height=80, placeholder="e.g. I play chess, I've lived in 3 countries, I'm a twin")
        else:
            answers[key] = st.text_input(question)

    st.markdown('</div>', unsafe_allow_html=True)
    submitted = st.form_submit_button("✨ Generate & Post My Introduction")

if submitted:
    missing = [q for k, q in questions if not answers.get(k, "").strip()]
    if missing:
        st.warning(f"Please answer all questions before submitting.")
    else:
        with st.spinner("🤖 Generating your AI-polished introduction..."):
            try:
                introduction = generate_ai_introduction(answers)
                st.markdown('<span class="step-badge">Step 2 — Your Introduction</span>', unsafe_allow_html=True)
                st.markdown(f'<div class="intro-box">{introduction}</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"AI generation failed: {e}")
                st.stop()

        with st.spinner("💾 Saving and uploading to GitHub..."):
            try:
                csv_url = save_and_upload_csv(answers)
                st.markdown('<div class="success-banner">✅ Responses saved and uploaded to GitHub</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"GitHub upload failed: {e}")
                st.stop()

        with st.spinner("📬 Posting to Canvas discussion..."):
            try:
                post_to_canvas(introduction, csv_url)
                st.markdown('<div class="success-banner">✅ Introduction posted to Canvas discussion</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Canvas posting failed: {e}")
                st.stop()

        st.balloons()
        st.success("🎉 All done! Your introduction has been posted to Canvas.")
