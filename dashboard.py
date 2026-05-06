# dashboard.py — Student Introduction Analytics Dashboard
#
# Deploy free at: https://streamlit.io/cloud
# Add to the same repo as app.py
#
# Requirements (add to requirements.txt):
#   streamlit, pandas, plotly, wordcloud, matplotlib, anthropic, requests

import os
import io
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import anthropic
import streamlit as st

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="Class Introduction Analytics",
    page_icon="📊",
    layout="wide"
)

# ─────────────────────────────────────────────
# STYLING
# ─────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Lato:wght@300;400;700&display=swap');

html, body, [class*="css"] { font-family: 'Lato', sans-serif; }
h1, h2, h3 { font-family: 'Playfair Display', serif !important; }

.stApp { background: #0d1117; }

.metric-card {
    background: linear-gradient(135deg, #161b22, #1c2128);
    border: 1px solid #30363d;
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    margin-bottom: 1rem;
}
.metric-value {
    font-family: 'Playfair Display', serif;
    font-size: 2.8rem;
    font-weight: 700;
    color: #f0c040;
    line-height: 1;
}
.metric-label {
    color: #8b949e;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-top: 0.4rem;
}
.section-header {
    color: #f0c040;
    font-family: 'Playfair Display', serif !important;
    font-size: 1.4rem;
    border-bottom: 1px solid #30363d;
    padding-bottom: 0.5rem;
    margin: 2rem 0 1rem 0;
}
.ai-summary {
    background: linear-gradient(135deg, #1c2128, #161b22);
    border: 1px solid #f0c04033;
    border-left: 4px solid #f0c040;
    border-radius: 12px;
    padding: 1.5rem 2rem;
    color: #c9d1d9;
    font-size: 1rem;
    line-height: 1.8;
}
.semester-badge {
    display: inline-block;
    background: #f0c040;
    color: #0d1117;
    font-weight: 700;
    font-size: 0.8rem;
    padding: 4px 14px;
    border-radius: 20px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 1rem;
}
section[data-testid="stSidebar"] > div {
    background: #161b22;
    border-right: 1px solid #30363d;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SECRETS
# ─────────────────────────────────────────────

def get_secret(key):
    try:
        return st.secrets[key]
    except Exception:
        return os.environ.get(key, "")

GITHUB_USERNAME   = get_secret("GITHUB_USERNAME")
GITHUB_REPO       = get_secret("GITHUB_REPO")
GITHUB_BRANCH     = get_secret("GITHUB_BRANCH") or "main"
GITHUB_TOKEN      = get_secret("GITHUB_TOKEN")
ANTHROPIC_API_KEY = get_secret("ANTHROPIC_API_KEY")

# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────

SEMESTERS = ["Summer 2026", "Fall 2026", "Spring 2027", "Summer 2027"]
CSV_FILES = {s: f"student_introductions_{s.replace(' ', '_').lower()}.csv" for s in SEMESTERS}
# Also support the default filename from app.py
CSV_FILES["Summer 2026 (default)"] = "student_introductions.csv"

@st.cache_data(ttl=300)
def load_csv_from_github(filename: str) -> pd.DataFrame | None:
    url = f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{GITHUB_REPO}/{GITHUB_BRANCH}/{filename}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        return None
    return pd.read_csv(io.StringIO(r.text))

def generate_ai_summary(df: pd.DataFrame, semester: str) -> str:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    sample = df.head(20).to_string(index=False)
    prompt = f"""You are an educational analyst reviewing student introduction data for {semester}.

Here is a sample of student responses:
{sample}

Write a concise 3-4 sentence summary for the professor covering:
- Common themes in why students enrolled
- What students are most excited or fearful about
- Any notable patterns worth the professor knowing

Be warm, professional, and specific. No bullet points."""

    msg = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}]
    )
    return msg.content[0].text.strip()

def make_wordcloud(text: str, title: str):
    wc = WordCloud(
        width=800, height=350,
        background_color="#161b22",
        colormap="YlOrBr",
        max_words=60,
        collocations=False
    ).generate(text)
    fig, ax = plt.subplots(figsize=(10, 4))
    fig.patch.set_facecolor("#161b22")
    ax.set_facecolor("#161b22")
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    return fig

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("<h2 style='color:#f0c040;'>📊 Analytics</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#8b949e; font-size:0.85rem;'>Student Introduction Dashboard</p>", unsafe_allow_html=True)
    st.divider()

    semester = st.selectbox("Select Semester", list(CSV_FILES.keys()), index=0)
    st.divider()

    show_ai = st.toggle("AI Summary", value=True)
    show_wordclouds = st.toggle("Word Clouds", value=True)
    show_majors = st.toggle("Majors Chart", value=True)
    show_contact = st.toggle("Contact Methods", value=True)
    show_table = st.toggle("Raw Data Table", value=False)

    st.divider()
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

st.markdown(f"<h1 style='color:#f0c040; margin-bottom:0.25rem;'>🎓 Class Introduction Analytics</h1>", unsafe_allow_html=True)
st.markdown(f'<span class="semester-badge">{semester.replace(" (default)", "")}</span>', unsafe_allow_html=True)

# Load data
df = load_csv_from_github(CSV_FILES[semester])

if df is None or df.empty:
    st.warning(f"No data found for **{semester}**. Make sure students have submitted their introductions and the CSV exists in your GitHub repo.")
    st.info(f"Expected file: `{CSV_FILES[semester]}`")
    st.stop()

# Rename columns for easier access
col_map = {
    df.columns[0]: "name",
    df.columns[1]: "major",
    df.columns[2]: "enrolled",
    df.columns[3]: "excited",
    df.columns[4]: "fear",
    df.columns[5]: "three_things",
    df.columns[6]: "contact",
    df.columns[7]: "professor",
}
df = df.rename(columns=col_map)

# ── METRIC CARDS ──────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{len(df)}</div><div class="metric-label">Total Students</div></div>', unsafe_allow_html=True)
with c2:
    n_majors = df["major"].nunique()
    st.markdown(f'<div class="metric-card"><div class="metric-value">{n_majors}</div><div class="metric-label">Unique Majors</div></div>', unsafe_allow_html=True)
with c3:
    top_contact = df["contact"].str.lower().apply(lambda x: "Email" if "email" in str(x) or "@" in str(x) else "Phone").value_counts().idxmax()
    st.markdown(f'<div class="metric-card"><div class="metric-value">{top_contact}</div><div class="metric-label">Top Contact Method</div></div>', unsafe_allow_html=True)
with c4:
    top_major = df["major"].value_counts().idxmax() if not df["major"].empty else "N/A"
    st.markdown(f'<div class="metric-card"><div class="metric-value" style="font-size:1.4rem;">{top_major}</div><div class="metric-label">Most Common Major</div></div>', unsafe_allow_html=True)

# ── AI SUMMARY ────────────────────────────────
if show_ai and ANTHROPIC_API_KEY:
    st.markdown('<div class="section-header">🤖 AI Class Summary</div>', unsafe_allow_html=True)
    with st.spinner("Generating AI summary..."):
        try:
            summary = generate_ai_summary(df, semester)
            st.markdown(f'<div class="ai-summary">{summary}</div>', unsafe_allow_html=True)
        except Exception as e:
            st.warning(f"AI summary unavailable: {e}")

# ── WORD CLOUDS ───────────────────────────────
if show_wordclouds:
    st.markdown('<div class="section-header">☁️ Word Clouds</div>', unsafe_allow_html=True)
    wc1, wc2 = st.columns(2)

    with wc1:
        st.markdown("**What excites students**")
        text_excited = " ".join(df["excited"].dropna().tolist())
        if text_excited.strip():
            st.pyplot(make_wordcloud(text_excited, "Excitement"))

    with wc2:
        st.markdown("**What students fear**")
        text_fear = " ".join(df["fear"].dropna().tolist())
        if text_fear.strip():
            st.pyplot(make_wordcloud(text_fear, "Fears"))

    st.markdown("**Why students enrolled**")
    text_enrolled = " ".join(df["enrolled"].dropna().tolist())
    if text_enrolled.strip():
        st.pyplot(make_wordcloud(text_enrolled, "Enrollment reasons"))

# ── MAJORS CHART ──────────────────────────────
if show_majors:
    st.markdown('<div class="section-header">📚 Majors Breakdown</div>', unsafe_allow_html=True)
    major_counts = df["major"].value_counts().reset_index()
    major_counts.columns = ["Major", "Count"]
    fig = px.bar(
        major_counts, x="Count", y="Major", orientation="h",
        color="Count", color_continuous_scale="YlOrBr",
        template="plotly_dark"
    )
    fig.update_layout(
        paper_bgcolor="#0d1117", plot_bgcolor="#161b22",
        font_color="#c9d1d9", showlegend=False,
        coloraxis_showscale=False,
        yaxis={"categoryorder": "total ascending"},
        margin=dict(l=10, r=10, t=10, b=10)
    )
    st.plotly_chart(fig, use_container_width=True)

# ── CONTACT METHOD PIE ────────────────────────
if show_contact:
    st.markdown('<div class="section-header">📱 Preferred Contact Methods</div>', unsafe_allow_html=True)
    contact_labels = df["contact"].str.lower().apply(
        lambda x: "Email" if "email" in str(x) or "@" in str(x) else
                  "Phone/Text" if any(c.isdigit() for c in str(x)) else "Other"
    )
    contact_counts = contact_labels.value_counts().reset_index()
    contact_counts.columns = ["Method", "Count"]
    fig2 = px.pie(
        contact_counts, names="Method", values="Count",
        color_discrete_sequence=["#f0c040", "#e07b39", "#5c6bc0"],
        template="plotly_dark", hole=0.45
    )
    fig2.update_layout(
        paper_bgcolor="#0d1117",
        font_color="#c9d1d9",
        legend=dict(bgcolor="#161b22"),
        margin=dict(l=10, r=10, t=10, b=10)
    )
    col_pie, col_space = st.columns([1, 1])
    with col_pie:
        st.plotly_chart(fig2, use_container_width=True)

# ── RAW TABLE ─────────────────────────────────
if show_table:
    st.markdown('<div class="section-header">📋 Raw Data</div>', unsafe_allow_html=True)
    st.dataframe(
        df.rename(columns={v: k.replace("_", " ").title() for k, v in {"name": "name"}.items()}),
        use_container_width=True,
        hide_index=True
    )
    csv_export = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download CSV", csv_export, f"introductions_{semester.replace(' ', '_')}.csv", "text/csv")
