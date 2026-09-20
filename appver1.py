# ============================================================
# ARTHROSONIC v2.0
# AI-Assisted Osteoarthritis Risk Screening
# SIH 2026 Prototype
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
import io
import textwrap


# ============================================================
# HTML / MARKDOWN RENDERING HELPER
# ============================================================

def render_markdown(content, *args, **kwargs):
    # Streamlit 1.64 can render raw HTML directly with st.html().
    # Use it for HTML blocks; keep normal Markdown on st.markdown().
    if isinstance(content, str):
        content = textwrap.dedent(content).strip()

        if "<" in content and ">" in content:
            return st.html(content)

    return st.markdown(content, *args, **kwargs)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="ArthroSonic | AI OA Screening",
    page_icon="🦴",
    layout="wide",
    initial_sidebar_state="expanded"
)
LOGO_PATH = Path("Assets/logo.png")
if not LOGO_PATH.exists():
    LOGO_PATH = Path("assets/logo.png")
if LOGO_PATH.exists():
    st.logo(str(LOGO_PATH))

# ============================================================
# RESPONSIVE LIGHT / DARK THEME
# ============================================================

# ============================================================
# STREAMLIT CHROME / SIDEBAR TOGGLE
# ============================================================

render_markdown("""
<style>
/* Keep Streamlit's header so the sidebar can always be reopened. */
header[data-testid="stHeader"] {
    background: transparent !important;
}

/* Keep the sidebar collapse/expand control visible. */
button[data-testid="stSidebarCollapseButton"],
button[data-testid="stSidebarCollapseButton"] svg {
    visibility: visible !important;
    opacity: 1 !important;
}

/* Make the owner toolbar unobtrusive rather than removing the header. */
div[data-testid="stToolbar"] {
    opacity: 0.55;
}

/* Navigation typography */
section[data-testid="stSidebar"] div[role="radiogroup"] label {
    min-height: 42px !important;
    padding: 8px 10px !important;
    border-radius: 10px !important;
}

section[data-testid="stSidebar"] div[role="radiogroup"] label p {
    font-size: 15px !important;
    font-weight: 650 !important;
    line-height: 1.25 !important;
}

section[data-testid="stSidebar"] .stRadio > label {
    font-size: 13px !important;
    font-weight: 800 !important;
    letter-spacing: 0.7px !important;
}

.status-row {
    display: flex;
    align-items: center;
    gap: 9px;
    font-size: 15px;
    font-weight: 650;
    padding: 7px 10px;
    border-radius: 10px;
}

.next-row {
    margin-top: 30px;
}
</style>
""")

render_markdown("""
<style>

/* =========================================================
   BASE
   ========================================================= */

:root {
    --bg: #f5f7fb;
    --surface: #ffffff;
    --surface-2: #f8fafc;
    --text: #101828;
    --text2: #475467;
    --muted: #667085;
    --border: #e4e7ec;
    --accent: #2563eb;
    --accent2: #06b6d4;
    --success: #12b76a;
    --warning: #f79009;
    --danger: #f04438;
}

/* Light mode */

.stApp {
    background: var(--bg) !important;
}

.main {
    background: var(--bg) !important;
}

.block-container {
    padding-top: 1.3rem;
    padding-bottom: 3rem;
    max-width: 1500px;
}

.stApp,
.stApp p,
.stApp span,
.stApp label,
.stApp li {
    color: var(--text2);
}

h1, h2, h3, h4, h5, h6 {
    color: var(--text) !important;
}


/* =========================================================
   DARK MODE
   Follows browser/system preference
   ========================================================= */

@media (prefers-color-scheme: dark) {

    :root {
        --bg: #090d16;
        --surface: #111827;
        --surface-2: #172033;
        --text: #f9fafb;
        --text2: #d0d5dd;
        --muted: #98a2b3;
        --border: #263246;
        --accent: #60a5fa;
        --accent2: #22d3ee;
    }

    .stApp,
    .main {
        background: #090d16 !important;
    }

    .stApp p,
    .stApp span,
    .stApp label,
    .stApp li {
        color: #d0d5dd !important;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #f9fafb !important;
    }

    .hero-title {
        color: #f9fafb !important;
    }

    .hero-subtitle {
        color: #98a2b3 !important;
    }

    .card,
    .metric-card,
    .glass-card {
        background: #111827 !important;
        border-color: #263246 !important;
    }

    .card p,
    .card li {
        color: #d0d5dd !important;
    }

    .metric-label,
    .metric-small {
        color: #98a2b3 !important;
    }

    .metric-value {
        color: #f9fafb !important;
    }

    div[data-baseweb="input"] input,
    div[data-baseweb="textarea"] textarea,
    div[data-baseweb="select"] > div {
        background: #111827 !important;
        color: #f9fafb !important;
        border-color: #344054 !important;
    }
}


/* =========================================================
   SIDEBAR
   ========================================================= */

section[data-testid="stSidebar"] {
    background: #0b1220 !important;
}

section[data-testid="stSidebar"] * {
    color: #f8fafc !important;
}


/* =========================================================
   HERO
   ========================================================= */

.hero-title {
    font-size: clamp(30px, 4vw, 48px);
    font-weight: 850;
    letter-spacing: -1.8px;
    color: var(--text) !important;
    line-height: 1.05;
    margin-bottom: 8px;
}

.hero-subtitle {
    font-size: 16px;
    color: var(--muted) !important;
    line-height: 1.6;
}


/* =========================================================
   SECTION TITLES
   ========================================================= */

.section-title {
    font-size: 24px;
    font-weight: 800;
    color: var(--text) !important;
    margin-top: 28px;
    margin-bottom: 15px;
}


/* =========================================================
   CARDS
   ========================================================= */

.card {
    background: var(--surface) !important;
    border-radius: 20px;
    padding: 25px;
    border: 1px solid var(--border);
    box-shadow: 0 8px 30px rgba(16,24,40,0.06);
    color: var(--text2);
}

.card h1,
.card h2,
.card h3,
.card h4 {
    color: var(--text) !important;
}

.card p,
.card li {
    color: var(--text2) !important;
}


/* =========================================================
   GLASS CARDS
   ========================================================= */

.glass-card {
    background: rgba(255,255,255,0.82);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 22px;
    box-shadow: 0 10px 35px rgba(16,24,40,0.07);
    backdrop-filter: blur(10px);
}


/* =========================================================
   METRIC CARDS
   ========================================================= */

.metric-card {
    background: var(--surface) !important;
    border-radius: 18px;
    padding: 20px;
    border: 1px solid var(--border);
    min-height: 125px;
    box-shadow: 0 6px 20px rgba(16,24,40,0.05);
}

.metric-label {
    color: var(--muted) !important;
    font-size: 12px;
    font-weight: 750;
    letter-spacing: 0.7px;
    text-transform: uppercase;
}

.metric-value {
    font-size: 29px;
    font-weight: 850;
    color: var(--text) !important;
    margin-top: 8px;
}

.metric-small {
    color: var(--muted) !important;
    font-size: 13px;
    margin-top: 4px;
}


/* =========================================================
   STATUS CHIPS
   ========================================================= */

.status-chip {
    display: inline-block;
    padding: 7px 12px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 750;
}

.status-green {
    background: #ecfdf3;
    color: #027a48 !important;
}

.status-blue {
    background: #eff8ff;
    color: #175cd3 !important;
}

.status-yellow {
    background: #fffaeb;
    color: #b54708 !important;
}


/* =========================================================
   HERO GRADIENT
   ========================================================= */

.hero-box {
    border-radius: 24px;
    padding: 30px;
    background:
        radial-gradient(circle at 85% 15%, rgba(34,211,238,0.18), transparent 30%),
        radial-gradient(circle at 15% 85%, rgba(37,99,235,0.15), transparent 35%),
        var(--surface);
    border: 1px solid var(--border);
    box-shadow: 0 12px 40px rgba(16,24,40,0.08);
}


/* =========================================================
   RISK DISPLAY
   ========================================================= */

.risk-moderate {
    background: linear-gradient(
        135deg,
        rgba(245,158,11,0.13),
        rgba(255,255,255,0.8)
    );
    border: 1px solid #fedf89;
    border-radius: 20px;
    padding: 25px;
}

.risk-score {
    font-size: 52px;
    font-weight: 900;
    color: #b54708 !important;
    line-height: 1;
}


/* =========================================================
   DIGITAL TWIN
   ========================================================= */

.twin-box {
    border-radius: 24px;
    padding: 25px;
    background:
        radial-gradient(circle at center,
        rgba(37,99,235,0.14),
        transparent 55%),
        var(--surface);
    border: 1px solid var(--border);
    min-height: 400px;
}


/* =========================================================
   TIMELINE
   ========================================================= */

.timeline-item {
    border-left: 3px solid var(--accent);
    padding-left: 18px;
    margin-bottom: 20px;
}

.timeline-date {
    font-size: 12px;
    color: var(--muted);
    font-weight: 700;
}

.timeline-title {
    font-size: 17px;
    font-weight: 800;
    color: var(--text);
}


/* =========================================================
   FOOTER
   ========================================================= */

.footer {
    text-align: center;
    color: var(--muted) !important;
    font-size: 12px;
    margin-top: 55px;
    padding-top: 20px;
    border-top: 1px solid var(--border);
}


/* =========================================================
   BUTTONS
   ========================================================= */

.stButton > button {
    border-radius: 12px;
    font-weight: 700;
}


/* =========================================================
   DIVIDERS
   ========================================================= */

hr {
    border-color: var(--border) !important;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSION STATE
# ============================================================

if "patient_id" not in st.session_state:
    st.session_state.patient_id = "AS-2026-0147"

if "recording_complete" not in st.session_state:
    st.session_state.recording_complete = False

if "analysis_generated" not in st.session_state:
    st.session_state.analysis_generated = False

if "current_page" not in st.session_state:
    st.session_state.current_page = "🏠 Overview"

if "profile_confirmed" not in st.session_state:
    st.session_state.profile_confirmed = False

if "previous_data_connected" not in st.session_state:
    st.session_state.previous_data_connected = False

if "uploaded_reports" not in st.session_state:
    st.session_state.uploaded_reports = []

if "risk_score" not in st.session_state:
    st.session_state.risk_score = 67

if "joint_screened" not in st.session_state:
    st.session_state.joint_screened = "Knee"


# ============================================================
# SIMULATED DATA
# ============================================================

np.random.seed(42)

time = np.linspace(0, 10, 3000)

signal = (
    0.12 * np.sin(2 * np.pi * 4 * time)
    + 0.07 * np.sin(2 * np.pi * 12 * time)
    + 0.025 * np.random.randn(len(time))
)

for center in [2.1, 4.4, 6.2, 8.1]:
    signal += 0.45 * np.exp(-((time - center) / 0.025) ** 2)


# ============================================================
# RISK / REPORT HELPERS
# ============================================================

def risk_grade(score):
    if score < 40:
        return 1, "LOW", "Few OA-related risk markers found by the system."
    if score < 70:
        return 2, "MEDIUM", "Some OA-related risk markers found. A doctor may suggest a check-up."
    return 3, "HIGH", "More OA-related risk markers found. A doctor's assessment is advised."


def go_next(target):
    st.session_state.current_page = target
    st.rerun()


def next_button(target, label="NEXT →"):
    st.markdown("<div class='next-row'></div>", unsafe_allow_html=True)
    if st.button(label, type="primary", use_container_width=True):
        go_next(target)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def page_header(title, subtitle):

    col1, col2 = st.columns([5, 1])

    with col1:

        render_markdown(
            f"""
            <div class="hero-title">{title}</div>
            <div class="hero-subtitle">{subtitle}</div>
            """,
            unsafe_allow_html=True
        )

    with col2:

        logo_path = LOGO_PATH

        if logo_path.exists():
            st.image(str(logo_path), width=120)

    render_markdown("---")


def metric_card(label, value, small=""):

    render_markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-small">{small}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def acoustic_waveform(height=320):

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=time,
            y=signal,
            mode="lines",
            name="Knee Joint Signal",
            line=dict(width=1.4)
        )
    )

    fig.update_layout(
        height=height,
        margin=dict(l=20, r=20, t=30, b=20),
        template="plotly_white",
        xaxis_title="Time (seconds)",
        yaxis_title="Amplitude",
        hovermode="x unified"
    )

    return fig


def create_spectrogram():

    frequencies = np.linspace(100, 8000, 90)
    times = np.linspace(0, 10, 130)

    Z = np.random.rand(
        len(frequencies),
        len(times)
    ) * 0.12

    for event in [2.1, 4.4, 6.2, 8.1]:

        idx = np.argmin(abs(times - event))

        Z[
            :,
            max(0, idx - 2):min(len(times), idx + 3)
        ] += np.random.rand(
            len(frequencies),
            min(5, len(times))
        ) * 0.55

    fig = go.Figure(
        data=go.Heatmap(
            x=times,
            y=frequencies,
            z=Z,
            colorscale="Viridis"
        )
    )

    fig.update_layout(
        height=350,
        template="plotly_white",
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis_title="Time (s)",
        yaxis_title="Frequency (Hz)"
    )

    return fig


def generate_pdf():
    """Generate the two-page report using the same structure and visual hierarchy
    as the supplied ArthroSonic report template, with current patient/analysis data.
    """
    from reportlab.platypus import PageBreak, KeepTogether, Image
    from reportlab.lib.utils import ImageReader

    score = int(st.session_state.risk_score)
    grade, level, simple_words = risk_grade(score)
    patient_id = st.session_state.patient_id
    report_date = datetime.now().strftime("%d %B %Y")
    joint = st.session_state.get("joint_screened", "Knee")
    data_quality = 94
    sound_events = 17
    uploaded_count = len(st.session_state.get("uploaded_reports", []))

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=58,
        leftMargin=58,
        topMargin=52,
        bottomMargin=48,
        title="ArthroSonic Osteoarthritis Risk Report"
    )

    navy = colors.HexColor("#173D55")
    muted = colors.HexColor("#667A89")
    teal = colors.HexColor("#2AAEB0")
    pale_blue = colors.HexColor("#EAF6F6")
    pale_yellow = colors.HexColor("#FFF2D2")
    pale_green = colors.HexColor("#EAF6EC")
    pale_red = colors.HexColor("#FBE8E8")
    grid = colors.HexColor("#D7DEE3")

    styles = getSampleStyleSheet()
    title = styles["Title"]
    title.fontName = "Times-Bold"
    title.fontSize = 23
    title.leading = 26
    title.textColor = navy
    title.alignment = TA_CENTER

    subtitle = styles["Normal"]
    subtitle.fontName = "Times-Roman"
    subtitle.fontSize = 14
    subtitle.leading = 17
    subtitle.textColor = muted
    subtitle.alignment = TA_CENTER

    section = styles["Heading2"]
    section.fontName = "Times-Bold"
    section.fontSize = 15
    section.leading = 18
    section.textColor = navy
    section.spaceBefore = 12
    section.spaceAfter = 10

    body = styles["BodyText"]
    body.fontName = "Times-Roman"
    body.fontSize = 11.5
    body.leading = 15
    body.textColor = navy

    small = styles["BodyText"]
    small.fontName = "Times-Roman"
    small.fontSize = 9.5
    small.leading = 12
    small.textColor = muted

    bold = styles["BodyText"]
    bold.fontName = "Times-Bold"
    bold.fontSize = 11.5
    bold.leading = 15
    bold.textColor = navy

    def P(txt, style=body):
        return Paragraph(txt, style)

    def header_footer(canvas, doc_obj):
        canvas.saveState()
        w, h = A4
        canvas.setStrokeColor(grid)
        canvas.setLineWidth(0.6)
        canvas.line(58, 38, w - 58, 38)
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(muted)
        canvas.drawString(58, 24, "ARTHROSONIC • SAMPLE REPORT • NOT A MEDICAL DIAGNOSIS")
        canvas.drawRightString(w - 58, 24, f"Page {doc_obj.page}")
        canvas.restoreState()

    story = []

    # Header: logo + centered report title
    logo_path = LOGO_PATH if LOGO_PATH.exists() else None
    if logo_path:
        logo = Image(str(logo_path), width=82, height=82)
        header_table = Table([
            [logo, [P("ARTHROSONIC", title), P("AI-Assisted Osteoarthritis (OA) Risk Screening", subtitle), P("NORTH EASTERN REGION (NER), INDIA", subtitle), Spacer(1, 7), P("OSTEOARTHRITIS RISK REPORT", title), P("SAMPLE REPORT — DEMONSTRATION ONLY", subtitle)]]
        ], colWidths=[95, 420])
        header_table.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "MIDDLE"), ("ALIGN", (1,0), (1,0), "CENTER"), ("LEFTPADDING", (0,0), (-1,-1), 0), ("RIGHTPADDING", (0,0), (-1,-1), 0)]))
        story.append(header_table)
    else:
        story += [P("ARTHROSONIC", title), P("AI-Assisted Osteoarthritis (OA) Risk Screening", subtitle), P("NORTH EASTERN REGION (NER), INDIA", subtitle), Spacer(1, 7), P("OSTEOARTHRITIS RISK REPORT", title), P("SAMPLE REPORT — DEMONSTRATION ONLY", subtitle)]

    story.append(Spacer(1, 25))
    story.append(P("1. Patient &amp; Report Details", section))

    patient_rows = [
        [P("<b>Patient ID</b>"), P(patient_id), P("<b>Report Date</b>"), P(report_date)],
        [P("<b>Screening<br/>Type</b>"), P("AI-assisted joint screening"), P("<b>Joint<br/>Screened</b>"), P(f"{joint}")],
        [P("<b>Report<br/>Status</b>"), P("Preliminary screening"), P("<b>System<br/>Version</b>"), P("OA-NER v1.0")],
    ]
    t = Table(patient_rows, colWidths=[88, 170, 88, 169], rowHeights=[29, 39, 39])
    t.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.55, grid),
        ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#F2F5F6")),
        ("BACKGROUND", (2,0), (2,-1), colors.HexColor("#F2F5F6")),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0), (-1,-1), 8), ("RIGHTPADDING", (0,0), (-1,-1), 8),
    ]))
    story.append(t)

    story.append(P("2. Your Screening Result", section))
    result_text = {
        1: "The system found few OA-related risk markers. A doctor can help you understand what this means for your joint health.",
        2: "The system found some signs that may be linked to joint problems. A doctor can help you understand what this means for your joint health.",
        3: "The system found more OA-related risk markers. A doctor's assessment can help determine what this means for your joint health."
    }[grade]
    result_box = Table([[P(f"<b>GRADE {grade} — {level} RISK</b>", bold)], [P(f"<font size='25'><b>{score} / 100</b></font>", title)], [P("<b>OA-associated risk score</b>", small)], [P(result_text)]], colWidths=[515])
    result_box.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), pale_yellow if grade == 2 else (pale_green if grade == 1 else pale_red)),
        ("BOX", (0,0), (-1,-1), 0.8, colors.HexColor("#E5A72D")),
        ("ALIGN", (0,0), (-1,2), "CENTER"), ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 9), ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("LEFTPADDING", (0,0), (-1,-1), 12), ("RIGHTPADDING", (0,0), (-1,-1), 12),
    ]))
    story.append(result_box)

    story.append(P("What do the grades mean?", section))
    grade_rows = [
        [P("<b>GRADE</b>", bold), P("<b>RISK LEVEL</b>", bold), P("<b>IN SIMPLE WORDS</b>", bold)],
        [P("<b>Grade 1</b>"), P("<b>LOW</b>"), P("Few OA-related risk markers found by the system.")],
        [P("<b>Grade 2</b>"), P("<b>MEDIUM</b>"), P("Some OA-related risk markers found. A doctor may suggest a check-up.")],
        [P("<b>Grade 3</b>"), P("<b>HIGH</b>"), P("More OA-related risk markers found. A doctor's assessment is advised.")],
    ]
    gt = Table(grade_rows, colWidths=[88, 105, 322], rowHeights=[27, 28, 36, 36])
    gt.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), navy), ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("BACKGROUND", (0,1), (-1,1), pale_green), ("BACKGROUND", (0,2), (-1,2), pale_yellow), ("BACKGROUND", (0,3), (-1,3), pale_red),
        ("GRID", (0,0), (-1,-1), 0.55, grid), ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0), (-1,-1), 8), ("RIGHTPADDING", (0,0), (-1,-1), 8),
    ]))
    story.append(gt)
    story.append(Spacer(1, 8))
    story.append(P("Grades describe screening risk only. They do not confirm OA or show the amount of joint damage. Grade boundaries must be defined and validated for the AI model.", small))

    story.append(PageBreak())

    story.append(P("3. What Did the System Find?", section))
    story.append(P("The system checked sound-related patterns and other assessment data to look for signs that may be linked to osteoarthritis."))
    detail_rows = [
        [P("<b>SCREENING DETAIL</b>", bold), P("<b>RESULT</b>", bold), P("<b>WHAT IT MEANS</b>", bold)],
        [P("OA-related risk markers"), P(f"<b>{level.title()}</b>"), P(simple_words.replace("A doctor", "Further clinical review may be considered by a doctor"))],
        [P("Data quality"), P(f"<b>{data_quality}% — Good</b>"), P("The system captured the input clearly; this is not the chance of having OA.")],
        [P("Sound patterns detected"), P(f"<b>{sound_events}</b>"), P("Patterns picked up during screening.")],
    ]
    dt = Table(detail_rows, colWidths=[150, 105, 260], rowHeights=[27, 34, 44, 30])
    dt.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), navy), ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 0.55, grid), ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0), (-1,-1), 8), ("RIGHTPADDING", (0,0), (-1,-1), 8),
    ]))
    story.append(dt)

    story.append(P("4. What Does This Mean for You?", section))
    meaning = {
        1: f"Your result is Grade 1 (Low Risk). This does not mean you definitely do not have osteoarthritis. It means the system found few OA-related risk markers. If you have joint pain, stiffness, swelling, or trouble moving, share this with a doctor.",
        2: f"Your result is Grade 2 (Medium Risk). This does not mean you definitely have osteoarthritis. It means the system found some signs that may need further checking. If you have joint pain, stiffness, swelling, or trouble moving, share this with a doctor.",
        3: f"Your result is Grade 3 (High Risk). This does not mean you definitely have osteoarthritis. It means the system found more OA-related risk markers that warrant further checking. If you have joint pain, stiffness, swelling, or trouble moving, share this with a doctor."
    }[grade]
    mt = Table([[P(meaning)]], colWidths=[515])
    mt.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,-1), pale_blue), ("BOX", (0,0), (-1,-1), 0.8, teal), ("LEFTPADDING", (0,0), (-1,-1), 10), ("RIGHTPADDING", (0,0), (-1,-1), 10), ("TOPPADDING", (0,0), (-1,-1), 9), ("BOTTOMPADDING", (0,0), (-1,-1), 9)]))
    story.append(mt)

    story.append(P("5. What Might the Doctor Recommend?", section))
    story.append(P("After reviewing this report and checking your symptoms, a doctor may recommend:"))
    recs = [
        ("A joint check-up", "The doctor may ask about pain, stiffness, swelling, and when symptoms happen."),
        ("A movement check", "The doctor may check how well the joint bends and moves."),
        ("Further tests, if needed", "An X-ray or other tests may be suggested based on the examination."),
        ("Exercise or physiotherapy", "Suitable exercises may help support movement and joint strength."),
        ("A follow-up visit", "A repeat check may be advised if symptoms continue or become worse."),
    ]
    for head, desc in recs:
        story.append(Spacer(1, 7))
        story.append(P(f"• <b>{head}</b> — {desc}"))
    story.append(Spacer(1, 8))
    story.append(P("These are possible next steps, not a fixed treatment plan. The doctor will decide what is suitable for the patient.", small))

    story.append(P("6. Important Information", section))
    info = f"<b>This report is for screening and demonstration only.</b> It is not a medical diagnosis and cannot replace a doctor's examination. The result is based on the information provided to the system and may not capture every aspect of joint health. A qualified healthcare professional should make diagnosis and treatment decisions."
    it = Table([[P(info)]], colWidths=[515])
    it.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#F1F4F5")), ("BOX", (0,0), (-1,-1), 0.55, grid), ("LEFTPADDING", (0,0), (-1,-1), 10), ("RIGHTPADDING", (0,0), (-1,-1), 10), ("TOPPADDING", (0,0), (-1,-1), 8), ("BOTTOMPADDING", (0,0), (-1,-1), 8)]))
    story.append(it)
    story.append(Spacer(1, 10))
    story.append(P("<b>Generated by:</b> ArthroSonic | AI-Assisted OA Risk Screening System", subtitle))
    story.append(P(f"<b>Data status:</b> Simulated data for prototype demonstration{' • ' + str(uploaded_count) + ' supporting file(s) attached' if uploaded_count else ''}", subtitle))
    story.append(Spacer(1, 18))
    end_style = styles["BodyText"]
    end_style.fontName = "Times-Roman"; end_style.fontSize = 13; end_style.textColor = muted; end_style.alignment = TA_CENTER
    story.append(P("— END OF REPORT —", end_style))

    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    buffer.seek(0)
    return buffer


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    logo_path = LOGO_PATH

    if logo_path.exists():

        st.image(
            str(logo_path),
            use_container_width=True
        )

    else:

        render_markdown(
            "<div style='text-align:center;font-size:55px;'>🦴</div>",
            unsafe_allow_html=True
        )

    render_markdown(
        "<h2 style='text-align:center;'>ARTHROSONIC</h2>",
        unsafe_allow_html=True
    )

    st.caption(
        "AI-Assisted Osteoarthritis Risk Screening"
    )

    render_markdown("---")

    nav_options = [
        "🏠 Overview",
        "👤 Patient Profile",
        "📡 Assessment",
        "🧠 AI Analysis",
        "🧬 Digital Twin",
        "📋 Patient History"
    ]

    default_index = nav_options.index(st.session_state.current_page)
    selected_page = st.radio(
        "NAVIGATION",
        nav_options,
        index=default_index
    )
    if selected_page != st.session_state.current_page:
        st.session_state.current_page = selected_page
    page = selected_page

    render_markdown("---")

    st.caption("SYSTEM STATUS")

    render_markdown("<div class='status-row'>🟢 <span>AI Engine — Ready</span></div>", unsafe_allow_html=True)
    render_markdown("<div class='status-row'>🟢 <span>Joint Signal Sensor — Connected</span></div>", unsafe_allow_html=True)
    render_markdown("<div class='status-row'>🟢 <span>IMU Module — Connected</span></div>", unsafe_allow_html=True)
    render_markdown("<div class='status-row'>🟢 <span>Local Database — Ready</span></div>", unsafe_allow_html=True)

    render_markdown("---")

    st.caption("DEPLOYMENT")

    render_markdown("📍 NER / Rural Healthcare")
    render_markdown("📡 Offline-ready architecture")
    render_markdown("🔐 Secure patient records")

    render_markdown("---")

    st.caption("ArthroSonic Prototype • SIH 2026")


# ============================================================
# PAGE 1 — OVERVIEW
# ============================================================

if page == "🏠 Overview":

    page_header(
        "AI-Assisted Osteoarthritis Screening",
        "Portable multimodal assessment platform for early OA risk identification"
    )

    # Hero

    render_markdown(
        """
        <div class="hero-box">

            <div style="font-size:13px;font-weight:800;
                        letter-spacing:1px;color:#2563eb;">
                ARTHROSONIC • FIELD SCREENING PLATFORM
            </div>

            <h1 style="font-size:36px;margin-top:12px;">
                Turning joint signals into
                <span style="color:#2563eb;">
                actionable risk markers.
                </span>
            </h1>

            <p style="font-size:17px;max-width:850px;line-height:1.7;">
                ArthroSonic combines joint joint sound emissions,
                movement analysis, patient-reported symptoms and
                longitudinal data to support preliminary
                osteoarthritis risk screening in low-resource
                healthcare environments.
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    render_markdown(
        "<div class='section-title'>Live System Overview</div>",
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card(
            "ACTIVE PATIENT",
            "AS-2026-0147",
            "Assessment ready"
        )

    with c2:
        metric_card(
            "SENSOR STATUS",
            "ONLINE",
            "Joint Signal + IMU"
        )

    with c3:
        metric_card(
            "SIGNAL QUALITY",
            "94%",
            "Suitable for analysis"
        )

    with c4:
        metric_card(
            "ASSESSMENT MODE",
            "MULTIMODAL",
            "Joint signal + movement + symptoms"
        )

    # Visual area

    render_markdown(
        "<div class='section-title'>Multimodal Patient Profile</div>",
        unsafe_allow_html=True
    )

    left, right = st.columns([1.1, 1])

    with left:

        render_markdown(
            """
            <div class="card">

                <div style="display:flex;
                            justify-content:space-between;
                            align-items:center;">

                    <div>
                        <div style="font-size:12px;
                                    font-weight:800;
                                    color:#667085;">
                            CURRENT SCREENING
                        </div>

                        <h2 style="margin:5px 0;">
                            OA-associated risk markers
                        </h2>
                    </div>

                    <span class="status-chip status-yellow">
                        DEMO OUTPUT
                    </span>

                </div>

                <div style="font-size:52px;
                            font-weight:900;
                            color:#b54708;
                            margin-top:20px;">
                    MODERATE
                </div>

                <p>
                    Prototype multimodal analysis indicates
                    a moderate level of OA-associated markers.
                </p>

            </div>
            """,
            unsafe_allow_html=True
        )

        render_markdown("<br>", unsafe_allow_html=True)

        fig = acoustic_waveform(270)

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with right:

        render_markdown(
            """
            <div class="twin-box">

                <div style="text-align:center;">

                    <div style="font-size:12px;
                                font-weight:800;
                                letter-spacing:1px;
                                color:#667085;">
                        OA HUMAN DIGITAL TWIN
                    </div>

                    <div style="font-size:80px;
                                margin-top:25px;">
                        🧍
                    </div>

                    <div style="font-size:45px;
                                margin-top:-25px;">
                        🦿
                    </div>

                    <h2>Patient Movement State</h2>

                    <p>
                        Longitudinal representation of
                        movement, sound-pattern and symptom
                        characteristics.
                    </p>

                </div>

                <hr>

                <div style="display:flex;
                            justify-content:space-around;
                            text-align:center;">

                    <div>
                        <b>108°</b><br>
                        <small>Knee ROM</small>
                    </div>

                    <div>
                        <b>81%</b><br>
                        <small>Symmetry</small>
                    </div>

                    <div>
                        <b>0.84</b><br>
                        <small>Gait m/s</small>
                    </div>

                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    # Workflow

    render_markdown(
        "<div class='section-title'>Screening Workflow</div>",
        unsafe_allow_html=True
    )

    w1, w2, w3, w4 = st.columns(4)

    workflow = [
        ("01", "Patient Profile", "Symptoms + history"),
        ("02", "Sensor Capture", "Joint sound + movement"),
        ("03", "AI Fusion", "Feature extraction"),
        ("04", "Risk Report", "Personalized output")
    ]

    for col, (num, title, desc) in zip(
        [w1, w2, w3, w4],
        workflow
    ):

        with col:

            render_markdown(
                f"""
                <div class="metric-card">

                    <div style="font-size:12px;
                                color:#2563eb;
                                font-weight:900;">
                        STEP {num}
                    </div>

                    <h3 style="margin:8px 0;">
                        {title}
                    </h3>

                    <div class="metric-small">
                        {desc}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )


    next_button("👤 Patient Profile", "START PATIENT PROFILE →")

# ============================================================
# PAGE 2 — PATIENT PROFILE
# ============================================================

elif page == "👤 Patient Profile":

    page_header(
        "Patient Profile",
        "Create or reconnect a patient record before assessment"
    )

    render_markdown("<div class='section-title'>1. Patient Information</div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        name = st.text_input("Full Name", "Ananya Sharma")
    with c2:
        age = st.number_input("Age", 18, 100, 56)
    with c3:
        sex = st.selectbox("Sex", ["Female", "Male", "Other"])

    c1, c2, c3 = st.columns(3)
    with c1:
        location = st.text_input("Location", "Assam, NER")
    with c2:
        occupation = st.text_input("Occupation", "Agricultural worker")
    with c3:
        activity = st.selectbox("Physical Activity", ["Low", "Moderate", "High"])

    render_markdown("<div class='section-title'>2. Connect Patient Record</div>", unsafe_allow_html=True)
    st.info("Confirm the identity first. ArthroSonic can then reconnect the current assessment with previous screening records available in the prototype session.")
    connect_col, save_col = st.columns([2, 1])
    with connect_col:
        connect_previous = st.checkbox("Connect to previous patient data", value=st.session_state.previous_data_connected)
    with save_col:
        if st.button("✓ CONFIRM PATIENT", type="primary", use_container_width=True):
            st.session_state.profile_confirmed = True
            st.session_state.previous_data_connected = connect_previous
            st.success(f"Patient record confirmed for {name}.")

    if st.session_state.profile_confirmed:
        render_markdown("<div class='card'><b>✓ Patient record confirmed</b><br>Current screening can now be linked with the patient's longitudinal record.</div>", unsafe_allow_html=True)

        render_markdown("<div class='section-title'>3. Latest Reports & Medical Documents</div>", unsafe_allow_html=True)
        st.write("Upload any recent reports that may help the healthcare worker review the patient's history. These can include X-rays, MRI scans, CT scans, ultrasound reports, blood work, prescriptions, or other relevant documents.")
        uploads = st.file_uploader(
            "Upload latest reports",
            type=["pdf", "png", "jpg", "jpeg", "webp", "doc", "docx", "xls", "xlsx", "csv"],
            accept_multiple_files=True,
            help="Prototype only: files are available during the current app session."
        )
        if uploads:
            st.session_state.uploaded_reports = [f.name for f in uploads]
        if st.session_state.uploaded_reports:
            st.markdown("**Attached for this assessment:**")
            for filename in st.session_state.uploaded_reports:
                st.markdown(f"- 📎 {filename}")

        render_markdown("<div class='section-title'>4. OA Risk Factors & Symptoms</div>", unsafe_allow_html=True)
        r1, r2, r3 = st.columns(3)
        with r1:
            injury = st.selectbox("Previous Knee Injury", ["No", "Yes"])
        with r2:
            family = st.selectbox("Family History of OA", ["No", "Yes"])
        with r3:
            terrain = st.selectbox("Terrain Exposure", ["Low", "Moderate", "High"])

        s1, s2, s3 = st.columns(3)
        with s1:
            pain = st.slider("Pain Level", 0, 10, 5)
        with s2:
            stiffness = st.slider("Stiffness", 0, 10, 4)
        with s3:
            mobility = st.slider("Mobility Difficulty", 0, 10, 4)

        st.session_state.joint_screened = st.selectbox("Joint to screen", ["Knee", "Hip", "Other"], index=0)
        next_button("📡 Assessment", "SAVE & CONTINUE TO ASSESSMENT →")
    else:
        st.warning("Confirm the patient record to unlock document upload and the next step.")


# ============================================================
# PAGE 3 — SENSOR ASSESSMENT
# ============================================================

elif page == "📡 Assessment":

    page_header(
        "Sensor Assessment",
        "Guided acquisition of joint sound and movement signals"
    )

    render_markdown(
        f"""
        <div class="card">

            <b>ACTIVE PATIENT</b>

            <span style="margin-left:15px;
                         font-size:20px;
                         font-weight:800;">
                {st.session_state.patient_id}
            </span>

            <span class="status-chip status-green"
                  style="float:right;">
                READY
            </span>

        </div>
        """,
        unsafe_allow_html=True
    )

    render_markdown(
        "<div class='section-title'>Sensor Network</div>",
        unsafe_allow_html=True
    )

    a, b, c, d = st.columns(4)

    with a:
        metric_card(
            "JOINT SIGNAL SENSOR",
            "● ONLINE",
            "Joint sound patterns"
        )

    with b:
        metric_card(
            "IMU",
            "● ONLINE",
            "Movement tracking"
        )

    with c:
        metric_card(
            "CAMERA",
            "● READY",
            "Gait assessment"
        )

    with d:
        metric_card(
            "SIGNAL QUALITY",
            "94%",
            "Excellent acquisition"
        )

    # Assessment steps

    render_markdown(
        "<div class='section-title'>Guided Assessment Protocol</div>",
        unsafe_allow_html=True
    )

    p1, p2, p3 = st.columns(3)

    with p1:

        render_markdown(
            """
            <div class="card">

                <div style="font-size:35px;">🎧</div>

                <h3>01 · Joint Signal</h3>

                <p>
                    Place the joint signal sensor over the
                    knee joint and perform controlled
                    flexion-extension movements.
                </p>

                <span class="status-chip status-green">
                    READY
                </span>

            </div>
            """,
            unsafe_allow_html=True
        )

    with p2:

        render_markdown(
            """
            <div class="card">

                <div style="font-size:35px;">🚶</div>

                <h3>02 · Movement</h3>

                <p>
                    Capture knee movement, gait,
                    range of motion and left-right
                    movement symmetry.
                </p>

                <span class="status-chip status-blue">
                    READY
                </span>

            </div>
            """,
            unsafe_allow_html=True
        )

    with p3:

        render_markdown(
            """
            <div class="card">

                <div style="font-size:35px;">📝</div>

                <h3>03 · Symptoms</h3>

                <p>
                    Combine patient-reported pain,
                    stiffness, mobility and relevant
                    risk factors.
                </p>

                <span class="status-chip status-blue">
                    READY
                </span>

            </div>
            """,
            unsafe_allow_html=True
        )

    render_markdown(
        "<div class='section-title'>Joint Signal Acquisition</div>",
        unsafe_allow_html=True
    )

    if st.button(
        "🔴 START SENSOR RECORDING",
        type="primary",
        use_container_width=True
    ):

        progress = st.progress(0)

        import time as tm

        for i in range(101):

            progress.progress(i)

            tm.sleep(0.008)

        st.session_state.recording_complete = True

        st.success(
            "Joint-signal and movement sequence captured successfully."
        )

    if st.session_state.recording_complete:

        render_markdown(
            """
            <div class="card">

                <div style="display:flex;
                            justify-content:space-between;">

                    <div>
                        <h3>✓ Acquisition Complete</h3>

                        <p>
                            Signal quality is suitable for
                            feature extraction and prototype
                            AI analysis.
                        </p>
                    </div>

                    <div style="font-size:42px;">
                        📡
                    </div>

                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

        render_markdown(
            "<div class='section-title'>Live Joint Signal</div>",
            unsafe_allow_html=True
        )

        st.plotly_chart(
            acoustic_waveform(350),
            use_container_width=True
        )

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            metric_card(
                "DURATION",
                "10.4 s",
                "Recording"
            )

        with c2:
            metric_card(
                "EVENTS",
                "17",
                "Detected sound events"
            )

        with c3:
            metric_card(
                "SAMPLING",
                "16 kHz",
                "Acquisition rate"
            )

        with c4:
            metric_card(
                "QUALITY",
                "94%",
                "Signal quality index"
            )

        render_markdown(
            "<div class='section-title'>Time-Frequency Analysis</div>",
            unsafe_allow_html=True
        )

        st.plotly_chart(
            create_spectrogram(),
            use_container_width=True
        )

        if st.button(
            "🧠 RUN MULTIMODAL AI ANALYSIS",
            type="primary",
            use_container_width=True
        ):

            st.session_state.analysis_generated = True

            st.success(
                "Prototype multimodal analysis completed."
            )


    if st.session_state.recording_complete:
        next_button("🧠 AI Analysis", "CONTINUE TO AI ANALYSIS →")

# ============================================================
# PAGE 4 — AI ANALYSIS
# ============================================================

elif page == "🧠 AI Analysis":

    page_header(
        "AI Risk Analysis",
        "Screening grade, risk markers and supporting assessment findings"
    )

    score = int(st.session_state.risk_score)
    grade, level, simple_words = risk_grade(score)

    render_markdown(
        """
        <div class="card">
            <span class="status-chip status-yellow">PROTOTYPE / SIMULATED AI OUTPUT</span>
            <p style="margin-top:12px;">This page presents a preliminary screening interpretation for demonstration. It does not establish a medical diagnosis.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    render_markdown("<div class='section-title'>Screening Grade</div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1.2, 1, 1])
    with c1:
        risk_class = "risk-moderate" if grade == 2 else "card"
        render_markdown(f"""
        <div class="{risk_class}">
            <div style="font-size:12px;font-weight:800;letter-spacing:1px;">OA-ASSOCIATED RISK MARKERS</div>
            <div class="risk-score">GRADE {grade}</div>
            <div style="font-size:20px;font-weight:800;margin-top:8px;">{level} RISK</div>
            <div style="margin-top:10px;">{simple_words}</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        metric_card("OA-ASSOCIATED RISK SCORE", f"{score} / 100", "Prototype screening index")
    with c3:
        metric_card("DATA QUALITY", "94%", "Good input quality; not OA probability")

    render_markdown("<div class='section-title'>What Do the Grades Mean?</div>", unsafe_allow_html=True)
    grade_df = pd.DataFrame({
        "GRADE": ["Grade 1", "Grade 2", "Grade 3"],
        "RISK LEVEL": ["LOW", "MEDIUM", "HIGH"],
        "IN SIMPLE WORDS": [
            "Few OA-related risk markers found by the system.",
            "Some OA-related risk markers found. A doctor may suggest a check-up.",
            "More OA-related risk markers found. A doctor's assessment is advised."
        ]
    })
    st.dataframe(grade_df, use_container_width=True, hide_index=True)
    st.caption("Grades describe screening risk only. They do not confirm OA or show the amount of joint damage. Grade boundaries must be defined and validated for the AI model.")

    render_markdown("<div class='section-title'>What Did the System Find?</div>", unsafe_allow_html=True)
    detail = pd.DataFrame({
        "SCREENING DETAIL": ["OA-related risk markers", "Data quality", "Sound patterns detected"],
        "RESULT": [level.title(), "94% — Good", "17"],
        "WHAT IT MEANS": [simple_words, "The system captured the input clearly; this is not the chance of having OA.", "Patterns picked up during screening."]
    })
    st.dataframe(detail, use_container_width=True, hide_index=True)

    render_markdown("<div class='section-title'>Movement & Patient-Reported Findings</div>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    for col, label, value, small in [
        (m1, "KNEE ROM", "108°", "Movement range"),
        (m2, "GAIT SYMMETRY", "81%", "Left-right symmetry"),
        (m3, "PAIN", "6 / 10", "Patient reported"),
        (m4, "STIFFNESS", "4 / 10", "Patient reported"),
    ]:
        with col:
            metric_card(label, value, small)

    render_markdown("<div class='section-title'>Joint Signal Analysis</div>", unsafe_allow_html=True)
    left, right = st.columns(2)
    with left:
        st.plotly_chart(acoustic_waveform(340), use_container_width=True)
    with right:
        st.plotly_chart(create_spectrogram(), use_container_width=True)

    render_markdown("<div class='section-title'>Explainable Screening Factors</div>", unsafe_allow_html=True)
    factors = [
        ("🔊", "Sound-pattern events", "17 patterns detected during the prototype movement sequence."),
        ("🚶", "Movement symmetry", "Mild left-right movement asymmetry is present in the demonstration profile."),
        ("🦿", "Range of motion", "The recorded knee range of motion is 108° in the demonstration profile."),
        ("📝", "Reported symptoms", "Pain and stiffness inputs contribute to the multimodal screening profile."),
    ]
    cols = st.columns(4)
    for col, (icon, title_txt, desc) in zip(cols, factors):
        with col:
            render_markdown(f"<div class='card'><div style='font-size:30px'>{icon}</div><h3>{title_txt}</h3><p>{desc}</p></div>", unsafe_allow_html=True)

    render_markdown("<div class='section-title'>Longitudinal Risk Monitoring</div>", unsafe_allow_html=True)
    dates = ["Jan 2026", "Apr 2026", "Jul 2026", "Sep 2026"]
    risk = [38, 44, 56, score]
    trend = go.Figure(go.Scatter(x=dates, y=risk, mode="lines+markers", line=dict(width=4), name="Risk Index"))
    trend.update_layout(height=330, template="plotly_white", yaxis=dict(range=[0,100], title="Risk Index"), xaxis_title="Assessment Date")
    st.plotly_chart(trend, use_container_width=True)

    render_markdown("<div class='section-title'>What Does This Mean for You?</div>", unsafe_allow_html=True)
    meaning = {
        1: "Your result is Grade 1 (Low Risk). This does not mean you definitely do not have osteoarthritis. It means the system found few OA-related risk markers. If you have joint pain, stiffness, swelling, or trouble moving, share this with a doctor.",
        2: "Your result is Grade 2 (Medium Risk). This does not mean you definitely have osteoarthritis. It means the system found some signs that may need further checking. If you have joint pain, stiffness, swelling, or trouble moving, share this with a doctor.",
        3: "Your result is Grade 3 (High Risk). This does not mean you definitely have osteoarthritis. It means the system found more OA-related risk markers that may need further checking. If you have joint pain, stiffness, swelling, or trouble moving, share this with a doctor."
    }[grade]
    render_markdown(f"<div class='card'>{meaning}</div>", unsafe_allow_html=True)

    st.info("Screening support only. A qualified healthcare professional should make diagnosis and treatment decisions.")

    pdf = generate_pdf()
    st.download_button("📄 DOWNLOAD SCREENING REPORT", data=pdf, file_name=f"ArthroSonic_Report_{st.session_state.patient_id}.pdf", mime="application/pdf", type="primary", use_container_width=True)
    next_button("🧬 Digital Twin", "CONTINUE TO OA HUMAN DIGITAL TWIN →")


# ============================================================
# PAGE 5 — DIGITAL TWIN
# ============================================================

elif page == "🧬 Digital Twin":

    page_header(
        "OA Human Digital Twin",
        "Longitudinal digital representation of patient-specific OA-related characteristics"
    )

    render_markdown(
        """
        <div class="hero-box">

            <div style="font-size:12px;
                        font-weight:800;
                        letter-spacing:1px;
                        color:#2563eb;">
                PATIENT DIGITAL REPRESENTATION
            </div>

            <h1>
                From one-time screening
                to longitudinal monitoring.
            </h1>

            <p style="max-width:850px;
                      font-size:17px;
                      line-height:1.7;">
                The ArthroSonic Digital Twin organizes sound,
                movement, symptom and contextual measurements
                into a patient-specific longitudinal profile.
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    render_markdown(
        "<div class='section-title'>Patient Twin State</div>",
        unsafe_allow_html=True
    )

    left, right = st.columns([1, 1.5])

    with left:

        render_markdown(
            """
            <div class="twin-box">

                <div style="text-align:center;">

                    <div style="font-size:12px;
                                font-weight:800;
                                color:#667085;">
                        DIGITAL PATIENT MODEL
                    </div>

                    <div style="font-size:115px;
                                margin-top:25px;">
                        🧍
                    </div>

                    <div style="font-size:65px;
                                margin-top:-45px;">
                        🦿
                    </div>

                    <h2>Right Knee Profile</h2>

                    <span class="status-chip status-yellow">
                        MODERATE MARKER STATE
                    </span>

                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with right:

        render_markdown(
            """
            <div class="card">

                <h3>Patient-Specific State Variables</h3>

                <p>
                    These variables form the current
                    demonstration state of the digital twin.
                </p>

            </div>
            """,
            unsafe_allow_html=True
        )

        metrics = [
            ("Joint Sound Signature", "17 events"),
            ("Knee Range of Motion", "108°"),
            ("Gait Symmetry", "81%"),
            ("Reported Pain", "6 / 10"),
            ("Gait Speed", "0.84 m/s"),
            ("Signal Quality", "94%")
        ]

        for label, value in metrics:

            c1, c2 = st.columns([2, 1])

            with c1:
                st.write(f"**{label}**")

            with c2:
                st.write(f"**{value}**")

    render_markdown(
        "<div class='section-title'>Digital Twin Timeline</div>",
        unsafe_allow_html=True
    )

    timeline = [
        (
            "12 JAN 2026",
            "Baseline Assessment",
            "Initial patient movement and joint-signal profile recorded."
        ),
        (
            "18 APR 2026",
            "Follow-up Assessment",
            "Longitudinal measurements added to patient profile."
        ),
        (
            "20 JUL 2026",
            "Movement Assessment",
            "Updated gait and knee movement characteristics."
        ),
        (
            "18 SEP 2026",
            "Current Assessment",
            "Latest multimodal screening profile generated."
        )
    ]

    for date, title, desc in timeline:

        render_markdown(
            f"""
            <div class="timeline-item">

                <div class="timeline-date">
                    {date}
                </div>

                <div class="timeline-title">
                    {title}
                </div>

                <div>
                    {desc}
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    render_markdown(
        "<div class='section-title'>Why a Digital Twin?</div>",
        unsafe_allow_html=True
    )

    d1, d2, d3 = st.columns(3)

    twin_features = [
        (
            "📈",
            "Longitudinal",
            "Compare future measurements against the patient's own baseline."
        ),
        (
            "🔄",
            "Multimodal",
            "Combine sound, movement and symptom information."
        ),
        (
            "🧠",
            "Personalized",
            "Represent patient-specific characteristics rather than relying only on population averages."
        )
    ]

    for col, (icon, title, desc) in zip(
        [d1, d2, d3],
        twin_features
    ):

        with col:

            render_markdown(
                f"""
                <div class="card">

                    <div style="font-size:35px;">
                        {icon}
                    </div>

                    <h3>{title}</h3>

                    <p>{desc}</p>

                </div>
                """,
                unsafe_allow_html=True
            )


    next_button("📋 Patient History", "VIEW PATIENT HISTORY →")

# ============================================================
# PAGE 6 — HISTORY
# ============================================================

elif page == "📋 Patient History":

    page_header(
        "Patient History",
        "Longitudinal screening records and personalized baseline tracking"
    )

    render_markdown(
        f"""
        <div class="card">

            <div style="font-size:12px;
                        font-weight:800;
                        color:#667085;">
                PATIENT RECORD
            </div>

            <h2>
                {st.session_state.patient_id}
            </h2>

            <p>
                Ananya Sharma • Assam, North Eastern Region
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    render_markdown(
        "<div class='section-title'>Previous Assessments</div>",
        unsafe_allow_html=True
    )

    history = pd.DataFrame({
        "Date": [
            "12 Jan 2026",
            "18 Apr 2026",
            "20 Jul 2026",
            "18 Sep 2026"
        ],
        "Risk Markers": [
            "Low",
            "Low",
            "Moderate",
            "Moderate"
        ],
        "Risk Index": [
            38,
            44,
            56,
            67
        ],
        "Pain": [
            2,
            3,
            5,
            6
        ],
        "Sound Events": [
            9,
            11,
            15,
            17
        ],
        "Knee ROM": [
            "121°",
            "118°",
            "112°",
            "108°"
        ]
    })

    st.dataframe(
        history,
        use_container_width=True,
        hide_index=True
    )

    render_markdown(
        "<div class='section-title'>Longitudinal Trends</div>",
        unsafe_allow_html=True
    )

    c1, c2 = st.columns(2)

    with c1:

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=history["Date"],
                y=history["Risk Index"],
                mode="lines+markers",
                line=dict(width=4),
                name="Risk"
            )
        )

        fig.update_layout(
            title="Prototype Risk Index",
            yaxis=dict(range=[0, 100]),
            height=350,
            template="plotly_white"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with c2:

        fig2 = go.Figure()

        fig2.add_trace(
            go.Scatter(
                x=history["Date"],
                y=history["Sound Events"],
                mode="lines+markers",
                line=dict(width=4),
                name="Sound Events"
            )
        )

        fig2.update_layout(
            title="Sound Event Trend",
            height=350,
            template="plotly_white"
        )

        st.plotly_chart(
            fig2,
            use_container_width=True
        )

    render_markdown(
        "<div class='section-title'>Personalized Baseline</div>",
        unsafe_allow_html=True
    )

    b1, b2, b3, b4 = st.columns(4)

    with b1:
        metric_card(
            "BASELINE ROM",
            "121°",
            "Jan 2026"
        )

    with b2:
        metric_card(
            "CURRENT ROM",
            "108°",
            "Sep 2026"
        )

    with b3:
        metric_card(
            "BASELINE EVENTS",
            "9",
            "Jan 2026"
        )

    with b4:
        metric_card(
            "CURRENT EVENTS",
            "17",
            "Sep 2026"
        )

    render_markdown(
        "<div class='section-title'>Screening Interpretation</div>",
        unsafe_allow_html=True
    )

    render_markdown(
        """
        <div class="card">

            <h3>Longitudinal monitoring</h3>

            <p>
                ArthroSonic stores repeated screening measurements
                so that future assessments can be compared with
                the patient's own historical baseline.
            </p>

            <p>
                Changes in sound-pattern features, movement characteristics,
                symptoms and other recorded variables can therefore
                be visualized over time.
            </p>

            <span class="status-chip status-blue">
                PERSONALIZED MONITORING
            </span>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# FOOTER
# ============================================================

render_markdown(
    """
    <div class="footer">

        <b>ARTHROSONIC</b> • AI-Assisted OA Risk Screening • SIH 2026

        <br><br>

        Prototype for screening research and demonstration.
        Not a medical diagnostic system.

    </div>
    """,
    unsafe_allow_html=True
)
