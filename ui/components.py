import streamlit as st
import sqlite3
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "warehouse.db"
REPORTS_DIR = BASE_DIR / "reports"


def clean_html(html_str):
    # Strip each line, remove empty lines, and join into a single flat line
    # This prevents markdown parsers or HTML containers from seeing leading spaces
    lines = [line.strip() for line in html_str.splitlines()]
    return "".join(line for line in lines if line)


def render_html(html_str):
    st.html(clean_html(html_str))


# Status Helpers

def _get_last_updated():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT run_time FROM market_history ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        if row:
            dt = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
            return dt.strftime("%d %b %Y  %H:%M")
        return "Never"
    except Exception:
        return "Never"


def _get_pipeline_health():
    try:
        path = REPORTS_DIR / "narrator.json"
        if not path.exists():
            return "degraded"
        data = json.loads(path.read_text(encoding="utf-8"))
        return "healthy" if data.get("status") == "success" else "degraded"
    except Exception:
        return "degraded"


def _get_api_status():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM crypto_market")
        count = cursor.fetchone()[0]
        conn.close()
        return "connected" if count > 0 else "disconnected"
    except Exception:
        return "disconnected"


def _get_critic_confidence():
    try:
        path = REPORTS_DIR / "critic.json"
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        reviews = data.get("reviews", [])
        if not reviews:
            return None
        approved = sum(1 for r in reviews if r.get("approved"))
        return round(approved / len(reviews) * 100)
    except Exception:
        return None


# Sidebar

def render_sidebar():
    with st.sidebar:
        st.html(clean_html("""
        <div style="padding:0.6rem 0 1.2rem 0; text-align:center;">
            <div style="display:inline-flex; align-items:center; gap:0.4rem; margin-bottom:0.35rem;">
                <div style="width:32px; height:32px; border-radius:8px;
                            background:linear-gradient(135deg,#a78bfa,#60a5fa);
                            display:flex; align-items:center; justify-content:center;
                            font-size:1rem; font-weight:800; color:#fff;">A</div>
                <div style="font-size:1.3rem; font-weight:800;
                            background:linear-gradient(90deg,#a78bfa,#60a5fa);
                            -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                            letter-spacing:-0.02em;">ADA</div>
            </div>
            <div style="font-size:0.62rem; color:rgba(255,255,255,0.3);
                        letter-spacing:0.1em; text-transform:uppercase;">
                Autonomous Data Analyst
            </div>
        </div>
        """))

        api_status = _get_api_status()
        pipeline_status = _get_pipeline_health()
        last_updated = _get_last_updated()
        confidence = _get_critic_confidence()

        api_dot = "🟢" if api_status == "connected" else "🔴"
        pipe_dot = "🟢" if pipeline_status == "healthy" else "🟡"
        api_label = "Connected" if api_status == "connected" else "Disconnected"
        pipe_label = "Healthy" if pipeline_status == "healthy" else "Degraded"
        conf_label = f"{confidence}%" if confidence is not None else "—"

        st.html(clean_html(f"""
        <div style="margin-bottom:1rem;">
            <div style="font-size:0.62rem; font-weight:700; letter-spacing:0.1em;
                        text-transform:uppercase; color:rgba(255,255,255,0.25);
                        margin-bottom:0.5rem; padding-left:0.2rem;">System Status</div>
            <div style="display:flex; flex-direction:column; gap:0.35rem;">

                <div style="display:flex; justify-content:space-between; align-items:center;
                            background:rgba(255,255,255,0.03); border-radius:8px;
                            padding:0.45rem 0.75rem; border:1px solid rgba(255,255,255,0.05);">
                    <span style="font-size:0.75rem; color:rgba(255,255,255,0.4);">Live API</span>
                    <span style="font-size:0.75rem; color:#e2e8f0; font-weight:500;">{api_dot} {api_label}</span>
                </div>

                <div style="display:flex; justify-content:space-between; align-items:center;
                            background:rgba(255,255,255,0.03); border-radius:8px;
                            padding:0.45rem 0.75rem; border:1px solid rgba(255,255,255,0.05);">
                    <span style="font-size:0.75rem; color:rgba(255,255,255,0.4);">LLM</span>
                    <span style="font-size:0.75rem; color:#a78bfa; font-weight:500;">Gemini</span>
                </div>

                <div style="display:flex; justify-content:space-between; align-items:center;
                            background:rgba(255,255,255,0.03); border-radius:8px;
                            padding:0.45rem 0.75rem; border:1px solid rgba(255,255,255,0.05);">
                    <span style="font-size:0.75rem; color:rgba(255,255,255,0.4);">Pipeline</span>
                    <span style="font-size:0.75rem; color:#e2e8f0; font-weight:500;">{pipe_dot} {pipe_label}</span>
                </div>

                <div style="display:flex; justify-content:space-between; align-items:center;
                            background:rgba(255,255,255,0.03); border-radius:8px;
                            padding:0.45rem 0.75rem; border:1px solid rgba(255,255,255,0.05);">
                    <span style="font-size:0.75rem; color:rgba(255,255,255,0.4);">AI Confidence</span>
                    <span style="font-size:0.75rem; color:#34d399; font-weight:600;">{conf_label}</span>
                </div>

                <div style="display:flex; justify-content:space-between; align-items:center;
                            background:rgba(255,255,255,0.03); border-radius:8px;
                            padding:0.45rem 0.75rem; border:1px solid rgba(255,255,255,0.05);">
                    <span style="font-size:0.75rem; color:rgba(255,255,255,0.4);">Last Run</span>
                    <span style="font-size:0.75rem; color:#e2e8f0; font-weight:500; text-align:right;">{last_updated}</span>
                </div>

            </div>
        </div>
        """))


# Shared CSS

SHARED_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d0b20 0%, #0f1117 100%);
    border-right: 1px solid rgba(255,255,255,0.05);
}

[data-testid="stSidebarNavLink"] {
    border-radius: 8px !important;
    font-size: 0.86rem !important;
    margin: 1px 0 !important;
    transition: background 0.15s ease !important;
}

[data-testid="stSidebarNavLink"]:hover {
    background: rgba(167,139,250,0.1) !important;
}

[data-testid="stSidebarNavLink"][aria-current="page"] {
    background: rgba(167,139,250,0.15) !important;
    border-left: 3px solid #a78bfa !important;
    font-weight: 600 !important;
}

.section-header {
    font-size: 0.85rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.35);
    margin: 1.8rem 0 0.7rem 0;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid rgba(255,255,255,0.06);
}

.kpi-card {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 1.2rem 1.3rem;
    transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
    height: 100%;
}

.kpi-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.3);
    border-color: rgba(167,139,250,0.18);
}

.kpi-icon { font-size: 1rem; margin-bottom: 0.45rem; opacity: 0.8; }
.kpi-label {
    font-size: 0.68rem; font-weight: 700;
    letter-spacing: 0.09em; text-transform: uppercase;
    color: rgba(255,255,255,0.35); margin-bottom: 0.25rem;
}
.kpi-value {
    font-size: 1.75rem; font-weight: 800;
    color: #e2e8f0; line-height: 1.1; margin-bottom: 0.25rem;
}
.kpi-delta { font-size: 0.78rem; font-weight: 500; }
.kpi-delta-up   { color: #34d399; }
.kpi-delta-down { color: #f87171; }
.kpi-delta-neu  { color: rgba(255,255,255,0.35); }
.kpi-sub { font-size: 0.76rem; color: rgba(255,255,255,0.3); margin-top: 0.15rem; }

.badge {
    display: inline-block; padding: 0.15rem 0.6rem;
    border-radius: 100px; font-size: 0.68rem; font-weight: 700;
    letter-spacing: 0.06em; text-transform: uppercase; margin-right: 0.3rem;
}
.badge-green  { background:rgba(52,211,153,0.12);  color:#34d399; border:1px solid rgba(52,211,153,0.25); }
.badge-red    { background:rgba(248,113,113,0.12); color:#f87171; border:1px solid rgba(248,113,113,0.25); }
.badge-purple { background:rgba(167,139,250,0.12); color:#a78bfa; border:1px solid rgba(167,139,250,0.25); }
.badge-blue   { background:rgba(96,165,250,0.12);  color:#60a5fa; border:1px solid rgba(96,165,250,0.25); }
.badge-amber  { background:rgba(251,191,36,0.12);  color:#fbbf24; border:1px solid rgba(251,191,36,0.25); }
.badge-gray   { background:rgba(148,163,184,0.1);  color:#94a3b8; border:1px solid rgba(148,163,184,0.2); }

.info-box {
    background: rgba(96,165,250,0.06);
    border-left: 3px solid #60a5fa;
    border-radius: 0 10px 10px 0;
    padding: 0.65rem 1rem;
    margin-bottom: 0.5rem;
    font-size: 0.86rem;
    color: #e2e8f0;
    line-height: 1.5;
}

.insight-box {
    background: rgba(167,139,250,0.06);
    border-left: 3px solid #a78bfa;
    border-radius: 0 10px 10px 0;
    padding: 0.65rem 1rem;
    margin-bottom: 0.5rem;
    font-size: 0.86rem;
    color: #e2e8f0;
    line-height: 1.5;
}

.summary-box {
    background: linear-gradient(135deg, rgba(167,139,250,0.07), rgba(96,165,250,0.04));
    border: 1px solid rgba(167,139,250,0.15);
    border-radius: 14px;
    padding: 1.2rem 1.4rem;
    color: #c4b5fd;
    font-size: 0.9rem;
    line-height: 1.75;
}
</style>
"""


# KPI Card HTML

def kpi_card(icon, label, value, delta=None, sub=None, delta_positive=True):
    delta_html = ""
    if delta:
        cls = "kpi-delta-up" if delta_positive else "kpi-delta-down"
        arrow = "▲" if delta_positive else "▼"
        delta_html = f'<div class="kpi-delta {cls}">{arrow} {delta}</div>'
    sub_html = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    return clean_html(f"""
    <div class="kpi-card">
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
        {sub_html}
    </div>
    """)


# Market Health Score

def calculate_health_score(df):
    if df.empty:
        return 50, "#94a3b8", "Neutral"
    total = len(df)
    bullish = int((df["price_change_percentage_24h"] > 0).sum())
    pos_ratio = bullish / total
    avg_change = float(df["price_change_percentage_24h"].mean())

    score = 50
    score += int((pos_ratio - 0.5) * 60)
    score += min(20, max(-20, int(avg_change * 6)))
    score = max(0, min(100, score))

    if score >= 70:
        return score, "#34d399", "Bullish"
    if score >= 45:
        return score, "#fbbf24", "Neutral"
    return score, "#f87171", "Bearish"


# Pipeline Workflow Diagram HTML

WORKFLOW_HTML = """
<div style="display:flex; align-items:center; justify-content:center;
            flex-wrap:wrap; gap:0; padding:1.5rem 0; overflow-x:auto;">
    {nodes}
</div>
"""

def workflow_node(icon, label, color="#a78bfa", active=True):
    opacity = "1" if active else "0.35"
    return f"""
    <div style="display:flex; align-items:center; opacity:{opacity};">
        <div style="text-align:center; min-width:72px;">
            <div style="width:44px; height:44px; border-radius:12px; margin:0 auto 0.4rem auto;
                        background:linear-gradient(135deg,{color}22,{color}11);
                        border:1px solid {color}44;
                        display:flex; align-items:center; justify-content:center;
                        font-size:1.25rem;">{icon}</div>
            <div style="font-size:0.68rem; font-weight:600; color:rgba(255,255,255,0.6);
                        letter-spacing:0.04em;">{label}</div>
        </div>
    </div>
    """

def workflow_arrow():
    return """
    <div style="color:rgba(255,255,255,0.2); font-size:1.1rem;
                padding:0 0.3rem; margin-bottom:1.2rem;">→</div>
    """

def render_workflow_pipeline(statuses=None):
    statuses = statuses or {}
    nodes = [
        ("📊", "Profiler",   "#a78bfa", statuses.get("profiler",   True)),
        ("💡", "Hypothesis", "#60a5fa", statuses.get("hypothesis", True)),
        ("📈", "Analyst",    "#34d399", statuses.get("analyst",    True)),
        ("✅", "Critic",     "#fbbf24", statuses.get("critic",     True)),
        ("📝", "Narrator",   "#f87171", statuses.get("narrator",   True)),
        ("🧠", "Memory",     "#a78bfa", statuses.get("memory",     True)),
    ]
    html = ""
    for i, (icon, label, color, active) in enumerate(nodes):
        html += workflow_node(icon, label, color, active)
        if i < len(nodes) - 1:
            html += workflow_arrow()
    return clean_html(WORKFLOW_HTML.format(nodes=html))


# Pipeline Status Row (GitHub Actions style)

def render_pipeline_status(report_statuses):
    agents = [
        ("📊", "Profiler",   report_statuses.get("profile",    "success")),
        ("💡", "Hypothesis", report_statuses.get("hypotheses", "success")),
        ("📈", "Analyst",    report_statuses.get("analysis",   "success")),
        ("✅", "Critic",     report_statuses.get("critic",     "success")),
        ("📝", "Narrator",   report_statuses.get("narrator",   "success")),
        ("🧠", "Memory",     report_statuses.get("memory",     "success")),
    ]

    cards = ""
    for icon, label, status in agents:
        if status == "success":
            dot = "🟢"
            color = "#34d399"
            bg = "rgba(52,211,153,0.06)"
            border = "rgba(52,211,153,0.2)"
        elif status == "failed":
            dot = "🔴"
            color = "#f87171"
            bg = "rgba(248,113,113,0.06)"
            border = "rgba(248,113,113,0.2)"
        elif status == "skipped":
            dot = "⚪"
            color = "#94a3b8"
            bg = "rgba(148,163,184,0.04)"
            border = "rgba(148,163,184,0.15)"
        else:
            dot = "⚪"
            color = "#94a3b8"
            bg = "rgba(148,163,184,0.04)"
            border = "rgba(148,163,184,0.15)"

        cards += f"""
        <div style="background:{bg}; border:1px solid {border}; border-radius:10px;
                    padding:0.6rem 0.8rem; text-align:center; min-width:90px;">
            <div style="font-size:1.1rem; margin-bottom:0.2rem;">{icon}</div>
            <div style="font-size:0.72rem; font-weight:600; color:rgba(255,255,255,0.7);
                        margin-bottom:0.25rem;">{label}</div>
            <div style="font-size:0.7rem; color:{color}; font-weight:600;">{dot} {status.title()}</div>
        </div>
        """

    return clean_html(f"""
    <div style="display:flex; gap:0.6rem; flex-wrap:wrap; margin-bottom:1.5rem;">
        {cards}
    </div>
    """)
