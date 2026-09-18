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
st.logo("Assets/logo.png")

# ============================================================
# RESPONSIVE LIGHT / DARK THEME
# ============================================================

# ============================================================
# HIDE STREAMLIT TOP TOOLBAR
# ============================================================

render_markdown("""
<style>
header[data-testid="stHeader"] {
    display: none !important;
}

div[data-testid="stToolbar"] {
    display: none !important;
}

div[data-testid="stDecoration"] {
    display: none !important;
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

        logo_path = Path("assets/logo.png")

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
            name="Knee Acoustic Signal",
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

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    title_style = styles["Title"]
    title_style.alignment = TA_CENTER

    story = []

    story.append(
        Paragraph(
            "ARTHROSONIC",
            title_style
        )
    )

    story.append(
        Paragraph(
            "AI-Assisted OA Risk Screening Report",
            styles["Heading2"]
        )
    )

    story.append(Spacer(1, 20))

    data = [
        ["Patient ID", st.session_state.patient_id],
        ["Assessment Date", datetime.now().strftime("%d %B %Y")],
        ["OA-associated Risk Markers", "Moderate"],
        ["Prototype Risk Score", "67 / 100"],
        ["Signal Quality", "94%"],
        ["Assessment Type", "Multimodal screening"]
    ]

    table = Table(
        data,
        colWidths=[180, 290]
    )

    table.setStyle(
        TableStyle([
            ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
            ("BACKGROUND", (0,0), (0,-1), colors.lightgrey),
            ("PADDING", (0,0), (-1,-1), 8),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE")
        ])
    )

    story.append(table)

    story.append(Spacer(1, 20))

    story.append(
        Paragraph(
            "Acoustic Features",
            styles["Heading2"]
        )
    )

    feature_data = [
        ["Feature", "Value"],
        ["RMS Energy", "0.43"],
        ["Peak Amplitude", "0.81"],
        ["Acoustic Events", "17"],
        ["Dominant Frequency", "1.8 kHz"],
        ["Spectral Entropy", "0.67"]
    ]

    feature_table = Table(
        feature_data,
        colWidths=[250, 220]
    )

    feature_table.setStyle(
        TableStyle([
            ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
            ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
            ("PADDING", (0,0), (-1,-1), 8)
        ])
    )

    story.append(feature_table)

    story.append(Spacer(1, 20))

    story.append(
        Paragraph(
            "This prototype indicates moderate OA-associated risk markers based on simulated multimodal data.",
            styles["BodyText"]
        )
    )

    story.append(Spacer(1, 15))

    story.append(
        Paragraph(
            "Disclaimer: This prototype is intended for screening research and demonstration only. It does not constitute a medical diagnosis.",
            styles["BodyText"]
        )
    )

    doc.build(story)

    buffer.seek(0)

    return buffer


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    logo_path = Path("assets/logo.png")

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

    page = st.radio(
        "NAVIGATION",
        [
            "🏠 Overview",
            "👤 Patient Profile",
            "📡 Assessment",
            "🧠 AI Analysis",
            "🧬 Digital Twin",
            "📋 Patient History"
        ]
    )

    render_markdown("---")

    st.caption("SYSTEM STATUS")

    render_markdown("🟢 **AI Engine** — Ready")
    render_markdown("🟢 **Acoustic Sensor** — Connected")
    render_markdown("🟢 **IMU Module** — Connected")
    render_markdown("🟢 **Local Database** — Ready")

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
                ArthroSonic combines joint acoustic emissions,
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
            "Acoustic + IMU"
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
            "Acoustic + movement + symptoms"
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
                        movement, acoustic and symptom
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
        ("02", "Sensor Capture", "Acoustic + movement"),
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


# ============================================================
# PAGE 2 — PATIENT PROFILE
# ============================================================

elif page == "👤 Patient Profile":

    page_header(
        "Patient Profile",
        "Digital clinical record for multimodal OA risk assessment"
    )

    render_markdown(
        f"""
        <div class="card">

            <div style="font-size:12px;
                        font-weight:800;
                        color:#667085;">
                ACTIVE PATIENT
            </div>

            <div style="font-size:28px;
                        font-weight:850;
                        margin-top:5px;">
                {st.session_state.patient_id}
            </div>

            <div style="margin-top:8px;">
                Screening record ready for assessment
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    render_markdown(
        "<div class='section-title'>Patient Information</div>",
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        name = st.text_input(
            "Full Name",
            "Ananya Sharma"
        )

    with c2:
        age = st.number_input(
            "Age",
            18,
            100,
            56
        )

    with c3:
        sex = st.selectbox(
            "Sex",
            ["Female", "Male", "Other"]
        )

    c1, c2, c3 = st.columns(3)

    with c1:
        location = st.text_input(
            "Location",
            "Assam, NER"
        )

    with c2:
        occupation = st.text_input(
            "Occupation",
            "Agricultural worker"
        )

    with c3:
        activity = st.selectbox(
            "Physical Activity",
            ["Low", "Moderate", "High"]
        )

    render_markdown(
        "<div class='section-title'>OA Risk Factors</div>",
        unsafe_allow_html=True
    )

    r1, r2, r3 = st.columns(3)

    with r1:
        injury = st.selectbox(
            "Previous Knee Injury",
            ["No", "Yes"]
        )

    with r2:
        family = st.selectbox(
            "Family History of OA",
            ["No", "Yes"]
        )

    with r3:
        terrain = st.selectbox(
            "Terrain Exposure",
            ["Low", "Moderate", "High"]
        )

    render_markdown(
        "<div class='section-title'>Patient-Reported Symptoms</div>",
        unsafe_allow_html=True
    )

    s1, s2, s3 = st.columns(3)

    with s1:
        pain = st.slider(
            "Pain Level",
            0,
            10,
            5
        )

    with s2:
        stiffness = st.slider(
            "Stiffness",
            0,
            10,
            4
        )

    with s3:
        mobility = st.slider(
            "Mobility Difficulty",
            0,
            10,
            4
        )

    render_markdown("<br>", unsafe_allow_html=True)

    if st.button(
        "💾 SAVE PATIENT PROFILE",
        type="primary",
        use_container_width=True
    ):

        st.success(
            f"Patient {st.session_state.patient_id} saved successfully."
        )


# ============================================================
# PAGE 3 — SENSOR ASSESSMENT
# ============================================================

elif page == "📡 Assessment":

    page_header(
        "Sensor Assessment",
        "Guided acquisition of joint acoustic and movement signals"
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
            "ACOUSTIC SENSOR",
            "● ONLINE",
            "Joint acoustic emissions"
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

                <h3>01 · Acoustic</h3>

                <p>
                    Place the acoustic sensor over the
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
        "<div class='section-title'>Acoustic Acquisition</div>",
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
            "Acoustic and movement sequence captured successfully."
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
            "<div class='section-title'>Live Acoustic Signal</div>",
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
                "Detected acoustic events"
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


# ============================================================
# PAGE 4 — AI ANALYSIS
# ============================================================

elif page == "🧠 AI Analysis":

    page_header(
        "AI Risk Analysis",
        "Multimodal feature fusion and explainable OA-associated risk markers"
    )

    render_markdown(
        """
        <div class="card">

            <span class="status-chip status-yellow">
                PROTOTYPE / SIMULATED AI OUTPUT
            </span>

            <p style="margin-top:12px;">
                The values shown on this page are demonstration
                outputs for the SIH prototype and are not
                clinically validated predictions.
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    render_markdown(
        "<div class='section-title'>Overall Screening Profile</div>",
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns([1.2, 1, 1])

    with c1:

        render_markdown(
            """
            <div class="risk-moderate">

                <div style="font-size:12px;
                            font-weight:800;
                            letter-spacing:1px;">
                    OA-ASSOCIATED RISK MARKERS
                </div>

                <div class="risk-score">
                    MODERATE
                </div>

                <div style="margin-top:10px;">
                    Preliminary multimodal screening output
                </div>

            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:

        metric_card(
            "PROTOTYPE RISK INDEX",
            "67 / 100",
            "Demonstration output"
        )

    with c3:

        metric_card(
            "SIGNAL QUALITY",
            "94%",
            "Suitable for analysis"
        )

    render_markdown(
        "<div class='section-title'>Joint Acoustic Signature</div>",
        unsafe_allow_html=True
    )

    left, right = st.columns(2)

    with left:

        st.plotly_chart(
            acoustic_waveform(360),
            use_container_width=True
        )

    with right:

        st.plotly_chart(
            create_spectrogram(),
            use_container_width=True
        )

    # Features

    render_markdown(
        "<div class='section-title'>Extracted Acoustic Features</div>",
        unsafe_allow_html=True
    )

    f1, f2, f3, f4, f5 = st.columns(5)

    acoustic_features = [
        ("RMS ENERGY", "0.43"),
        ("PEAK AMPLITUDE", "0.81"),
        ("ACOUSTIC EVENTS", "17"),
        ("DOMINANT FREQUENCY", "1.8 kHz"),
        ("SPECTRAL ENTROPY", "0.67")
    ]

    for col, (label, value) in zip(
        [f1, f2, f3, f4, f5],
        acoustic_features
    ):

        with col:
            metric_card(
                label,
                value,
                "Prototype feature"
            )

    # Movement

    render_markdown(
        "<div class='section-title'>Movement & Gait Analytics</div>",
        unsafe_allow_html=True
    )

    g1, g2, g3, g4 = st.columns(4)

    gait_data = [
        ("GAIT SPEED", "0.84 m/s"),
        ("CADENCE", "94 steps/min"),
        ("KNEE ROM", "108°"),
        ("SYMMETRY", "81%")
    ]

    for col, (label, value) in zip(
        [g1, g2, g3, g4],
        gait_data
    ):

        with col:
            metric_card(
                label,
                value,
                "Movement analysis"
            )

    # Radar

    render_markdown(
        "<div class='section-title'>Multimodal Risk Profile</div>",
        unsafe_allow_html=True
    )

    categories = [
        "Acoustic",
        "Mobility",
        "Pain",
        "Gait",
        "History"
    ]

    values = [72, 61, 58, 64, 70]

    radar = go.Figure()

    radar.add_trace(
        go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill="toself",
            name="Prototype Profile"
        )
    )

    radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        height=430,
        template="plotly_white",
        title="Multimodal OA-associated Marker Profile"
    )

    st.plotly_chart(
        radar,
        use_container_width=True
    )

    # Explainable AI

    render_markdown(
        "<div class='section-title'>Explainable AI</div>",
        unsafe_allow_html=True
    )

    e1, e2, e3, e4 = st.columns(4)

    explanations = [
        (
            "🎧",
            "Acoustic Events",
            "Elevated event density in the demonstration signal."
        ),
        (
            "🚶",
            "Movement Symmetry",
            "Mild left-right movement asymmetry detected."
        ),
        (
            "🦿",
            "Knee ROM",
            "Reduced range of motion in the demonstration profile."
        ),
        (
            "📝",
            "Pain",
            "Moderate patient-reported discomfort."
        )
    ]

    for col, (icon, title, desc) in zip(
        [e1, e2, e3, e4],
        explanations
    ):

        with col:

            render_markdown(
                f"""
                <div class="card">

                    <div style="font-size:32px;">
                        {icon}
                    </div>

                    <h3>{title}</h3>

                    <p>{desc}</p>

                </div>
                """,
                unsafe_allow_html=True
            )

    # Trend

    render_markdown(
        "<div class='section-title'>Longitudinal Risk Monitoring</div>",
        unsafe_allow_html=True
    )

    dates = [
        "Jan 2026",
        "Apr 2026",
        "Jul 2026",
        "Sep 2026"
    ]

    risk = [38, 44, 56, 67]

    trend = go.Figure()

    trend.add_trace(
        go.Scatter(
            x=dates,
            y=risk,
            mode="lines+markers",
            name="Prototype Risk Index",
            line=dict(width=4)
        )
    )

    trend.update_layout(
        height=350,
        template="plotly_white",
        yaxis=dict(
            range=[0, 100],
            title="Risk Index"
        ),
        xaxis_title="Assessment Date"
    )

    st.plotly_chart(
        trend,
        use_container_width=True
    )

    st.info(
        "Screening support only. A clinical evaluation should be "
        "considered by an appropriately qualified healthcare professional "
        "when clinically indicated."
    )

    render_markdown("---")

    pdf = generate_pdf()

    st.download_button(
        "📄 DOWNLOAD SCREENING REPORT",
        data=pdf,
        file_name=f"ArthroSonic_Report_{st.session_state.patient_id}.pdf",
        mime="application/pdf",
        type="primary",
        use_container_width=True
    )


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
                The ArthroSonic Digital Twin organizes acoustic,
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
            ("Acoustic Signature", "17 events"),
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
            "Initial patient movement and acoustic profile recorded."
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
            "Combine acoustic, movement and symptom information."
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
        "Acoustic Events": [
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
                y=history["Acoustic Events"],
                mode="lines+markers",
                line=dict(width=4),
                name="Acoustic Events"
            )
        )

        fig2.update_layout(
            title="Acoustic Event Trend",
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
                Changes in acoustic features, movement characteristics,
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
