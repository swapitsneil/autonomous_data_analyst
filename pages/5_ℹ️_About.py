import streamlit as st
from ui.components import render_sidebar, SHARED_CSS, render_html, kpi_card

st.set_page_config(
    page_title="About — ADA",
    page_icon="ℹ️",
    layout="wide"
)

st.markdown(SHARED_CSS, unsafe_allow_html=True)
render_sidebar()

render_html("""
<div style="padding:0.5rem 0 0.5rem 0;">
    <div style="font-size:1.75rem; font-weight:800;
                background:linear-gradient(90deg,#a78bfa,#60a5fa);
                -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                margin-bottom:0.2rem;">ℹ️ About ADA</div>
    <div style="font-size:0.85rem; color:rgba(255,255,255,0.35);">
        Platform overview, technology stack, architecture and project details
    </div>
</div>
""")


# ── Project Overview ─────────────────────────────────────────────────────────

render_html('<div class="section-header">🚀 Project Overview</div>')

render_html("""
<div class="summary-box" style="margin-bottom:1.5rem;">
    <b>Autonomous Data Analyst (ADA)</b> is an AI-powered analytics platform that
    automatically collects cryptocurrency market data, performs statistical analysis,
    generates and validates business hypotheses, produces executive reports,
    stores historical market memory, and visualizes insights through an interactive dashboard.
    The system utilizes a multi-agent LangGraph workflow to perform complex data analysis autonomously.
</div>
""")


# ── Architecture ─────────────────────────────────────────────────────────────

render_html('<div class="section-header">🏗️ System Architecture</div>')

render_html("""
<div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.06);
            border-radius:16px; padding:1.5rem 2rem; font-family:monospace; color:#a78bfa;
            font-size:0.88rem; line-height:1.75; overflow-x:auto;">
CoinGecko API<br>
&nbsp;&nbsp;&nbsp;&nbsp;│<br>
&nbsp;&nbsp;&nbsp;&nbsp;▼<br>
Bronze Layer (Raw JSON)<br>
&nbsp;&nbsp;&nbsp;&nbsp;│<br>
&nbsp;&nbsp;&nbsp;&nbsp;▼<br>
Silver Layer (Clean DataFrame)<br>
&nbsp;&nbsp;&nbsp;&nbsp;│<br>
&nbsp;&nbsp;&nbsp;&nbsp;▼<br>
SQLite Warehouse (Database)<br>
&nbsp;&nbsp;&nbsp;&nbsp;│<br>
&nbsp;&nbsp;&nbsp;&nbsp;▼<br>
LangGraph Workflow<br>
&nbsp;&nbsp;&nbsp;&nbsp;├── 📊 Profiler Agent<br>
&nbsp;&nbsp;&nbsp;&nbsp;├── 💡 Hypothesis Agent (Gemini)<br>
&nbsp;&nbsp;&nbsp;&nbsp;├── 📈 Analyst Agent<br>
&nbsp;&nbsp;&nbsp;&nbsp;├── ✅ Critic Agent (Gemini)<br>
&nbsp;&nbsp;&nbsp;&nbsp;├── 📝 Narrator Agent (Gemini)<br>
&nbsp;&nbsp;&nbsp;&nbsp;└── 🧠 Memory Agent<br>
&nbsp;&nbsp;&nbsp;&nbsp;│<br>
&nbsp;&nbsp;&nbsp;&nbsp;▼<br>
Reports (JSON) → Streamlit Dashboard / PDF Reports
</div>
""")


# ── AI Agents ────────────────────────────────────────────────────────────────

render_html('<div class="section-header">🤖 AI Agents</div>')

agents = [
    ("📊", "Profiler Agent", "Profiles dataset schema, missing values, summary statistics, correlation matrix and outliers."),
    ("💡", "Hypothesis Agent", "Formulates testable business hypotheses and selects appropriate statistical tests using Gemini."),
    ("📈", "Analyst Agent", "Autonomously runs statistical tests (Pearson/Spearman correlation, Linear Regression, T-Test, ANOVA)."),
    ("✅", "Critic Agent", "Peer-reviews statistical evidence and validations, approving or rejecting hypotheses using Gemini."),
    ("📝", "Narrator Agent", "Synthesizes approved insights into executive summaries, key findings, and recommendations using Gemini."),
    ("🧠", "Memory Agent", "Compares snapshots across multiple pipeline runs to detect trends, streaks, and rolling averages.")
]

for icon, title, desc in agents:
    with st.expander(f"{icon} {title}"):
        render_html(f"""
        <div style="padding:0.4rem 0.6rem; font-size:0.86rem; color:rgba(255,255,255,0.7); line-height:1.5;">
            {desc}
        </div>
        """)


# ── Technology Stack ─────────────────────────────────────────────────────────

render_html('<div class="section-header">🛠️ Technology Stack</div>')

col1, col2 = st.columns(2)

with col1:
    render_html("""
    <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.06);
                border-radius:14px; padding:1.2rem; height:100%; border-left:3px solid #a78bfa;">
        <div style="font-weight:700; color:#e2e8f0; margin-bottom:0.75rem; font-size:0.92rem;">Backend & Data</div>
        <ul style="margin:0; padding-left:1.2rem; font-size:0.85rem; color:rgba(255,255,255,0.55); line-height:1.65;">
            <li>Python</li>
            <li>Pandas &amp; NumPy</li>
            <li>SciPy &amp; Statsmodels</li>
            <li>SQLite Warehouse</li>
            <li>LangGraph Framework</li>
            <li>Requests</li>
        </ul>
    </div>
    """)

with col2:
    render_html("""
    <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.06);
                border-radius:14px; padding:1.2rem; height:100%; border-left:3px solid #60a5fa;">
        <div style="font-weight:700; color:#e2e8f0; margin-bottom:0.75rem; font-size:0.92rem;">AI &amp; Frontend</div>
        <ul style="margin:0; padding-left:1.2rem; font-size:0.85rem; color:rgba(255,255,255,0.55); line-height:1.65;">
            <li>Google Gemini 2.5 Flash</li>
            <li>Streamlit</li>
            <li>Plotly Express &amp; Graph Objects</li>
            <li>CoinGecko REST API</li>
            <li>Jinja2 templates</li>
        </ul>
    </div>
    """)


# ── Features ─────────────────────────────────────────────────────────────────

render_html('<div class="section-header">✨ Features</div>')

render_html("""
<div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap:0.75rem; margin-bottom:1rem;">
    <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.06); border-radius:10px; padding:0.8rem 1rem; font-size:0.82rem; color:rgba(255,255,255,0.65);">
        🟢 <b>Live Data Ingestion:</b> Real-time cryptocurrency snapshots from CoinGecko API.
    </div>
    <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.06); border-radius:10px; padding:0.8rem 1rem; font-size:0.82rem; color:rgba(255,255,255,0.65);">
        ⚙️ <b>Automated ETL:</b> Bronze JSON raw logs transformed into SQLite Silver relational tables.
    </div>
    <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.06); border-radius:10px; padding:0.8rem 1rem; font-size:0.82rem; color:rgba(255,255,255,0.65);">
        📈 <b>Statistical Testing:</b> Dynamic execution of correlations, t-tests, regressions, ANOVA.
    </div>
    <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.06); border-radius:10px; padding:0.8rem 1rem; font-size:0.82rem; color:rgba(255,255,255,0.65);">
        📝 <b>Executive Reporting:</b> Automatic creation of Deloitte/McKinsey-style HTML/PDF reports.
    </div>
    <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.06); border-radius:10px; padding:0.8rem 1rem; font-size:0.82rem; color:rgba(255,255,255,0.65);">
        🧠 <b>Advanced Memory:</b> Deep time-series pattern recognition across historical analysis snapshots.
    </div>
</div>
""")


# ── Statistics ───────────────────────────────────────────────────────────────

render_html('<div class="section-header">📊 Project Statistics</div>')

s1, s2, s3 = st.columns(3)
with s1:
    render_html(kpi_card("🤖", "AI Agents", "6", sub="LangGraph workflow"))
with s2:
    render_html(kpi_card("🌐", "Dashboard Pages", "5", sub="Streamlit navigation"))
with s3:
    render_html(kpi_card("🗄️", "Database", "SQLite", sub="warehouse.db"))


# ── Developer ────────────────────────────────────────────────────────────────

render_html('<div class="section-header">👨‍💻 Developer</div>')

render_html("""
<div style="background:rgba(255,255,255,0.025); border:1px solid rgba(255,255,255,0.06);
            border-radius:14px; padding:1.2rem 1.5rem; margin-bottom:2rem; border-left:3px solid #34d399;">
    <div style="font-weight:700; color:#e2e8f0; font-size:1.05rem; margin-bottom:0.3rem;">Swapnil Nicolson Dadel</div>
    <div style="font-size:0.75rem; text-transform:uppercase; letter-spacing:0.08em; color:#34d399; font-weight:700; margin-bottom:0.75rem;">Gen AI Data Analyst</div>
    <div style="font-size:0.86rem; color:rgba(255,255,255,0.5); line-height:1.6;">
        Designed and built with modern Data Engineering, Business Intelligence, Machine Learning,
        Generative AI, and Multi-Agent Systems architecture.
    </div>
</div>
""")

render_html("""
<div style="text-align:center; color:rgba(255,255,255,0.25); font-size:0.78rem; padding:1rem 0;">
    🚀 Autonomous Data Analyst • Version 1.0 • Stable Release
</div>
""")