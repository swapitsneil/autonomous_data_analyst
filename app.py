import subprocess
import sys
import sqlite3
import streamlit as st
from pathlib import Path
from ui.components import (
    render_sidebar, SHARED_CSS, kpi_card,
    render_workflow_pipeline, calculate_health_score, render_html
)

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "database" / "warehouse.db"

st.set_page_config(
    page_title="ADA — Autonomous Data Analyst",
    page_icon="🤖",
    layout="wide"
)

st.markdown(SHARED_CSS, unsafe_allow_html=True)
render_sidebar()


# Pipeline runner

def run_pipeline():
    venv_python = BASE_DIR / ".venv" / "Scripts" / "python.exe"
    result = subprocess.run(
        [str(venv_python), "-m", "ingestion.api_loader"],
        capture_output=True, text=True,
        cwd=str(BASE_DIR)
    )
    return result.returncode == 0, result.stdout, result.stderr


def load_kpis():
    try:
        conn = sqlite3.connect(DB_PATH)
        import pandas as pd
        df = pd.read_sql_query("SELECT * FROM crypto_market", conn)
        conn.close()
        return df
    except Exception:
        return None


# ── Header ──────────────────────────────────────────────────────────────────

render_html("""
<div style="background:linear-gradient(135deg, #0f0c29 0%, #1a1040 50%, #0d1117 100%);
            border-radius:20px; padding:3rem 3rem 2.5rem 3rem; margin-bottom:2rem;
            border:1px solid rgba(255,255,255,0.06);
            box-shadow:0 20px 60px rgba(0,0,0,0.5);">

    <div style="display:flex; align-items:center; gap:1rem; margin-bottom:1.5rem;">
        <div style="width:52px; height:52px; border-radius:14px;
                    background:linear-gradient(135deg,#a78bfa,#60a5fa);
                    display:flex; align-items:center; justify-content:center;
                    font-size:1.5rem; font-weight:900; color:white; box-shadow:0 4px 16px rgba(167,139,250,0.4);">A</div>
        <div>
            <div style="font-size:0.7rem; letter-spacing:0.15em; text-transform:uppercase;
                        color:rgba(255,255,255,0.3); margin-bottom:0.2rem;">AI-Powered Platform</div>
            <div style="font-size:2rem; font-weight:800; line-height:1.1;
                        background:linear-gradient(90deg,#a78bfa,#60a5fa,#34d399);
                        -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
                Autonomous Data Analyst
            </div>
        </div>
    </div>

    <div style="font-size:1.05rem; color:rgba(255,255,255,0.5); margin-bottom:1.5rem; max-width:600px;">
        Real-time Cryptocurrency Intelligence Platform
    </div>

    <div style="display:flex; gap:0.6rem; flex-wrap:wrap;">
        <span style="background:rgba(167,139,250,0.12); border:1px solid rgba(167,139,250,0.25);
                     color:#a78bfa; padding:0.3rem 0.9rem; border-radius:100px;
                     font-size:0.72rem; font-weight:700; letter-spacing:0.06em; text-transform:uppercase;">
            AI-Powered Statistical Analysis
        </span>
        <span style="background:rgba(96,165,250,0.12); border:1px solid rgba(96,165,250,0.25);
                     color:#60a5fa; padding:0.3rem 0.9rem; border-radius:100px;
                     font-size:0.72rem; font-weight:700; letter-spacing:0.06em; text-transform:uppercase;">
            Historical Memory Intelligence
        </span>
        <span style="background:rgba(52,211,153,0.12); border:1px solid rgba(52,211,153,0.25);
                     color:#34d399; padding:0.3rem 0.9rem; border-radius:100px;
                     font-size:0.72rem; font-weight:700; letter-spacing:0.06em; text-transform:uppercase;">
            Executive Reports
        </span>
    </div>
</div>
""")


# ── Run Pipeline Button ──────────────────────────────────────────────────────

col_run, col_spacer = st.columns([2, 6])

with col_run:
    run_clicked = st.button("▶  Run Pipeline", type="primary", use_container_width=True)

if run_clicked:
    with st.status("Running Autonomous Analysis Pipeline...", expanded=True) as status:
        st.write("📡 Connecting to CoinGecko API...")
        st.write("🔄 Running ETL pipeline (Bronze → Silver → SQLite)...")
        st.write("🤖 Starting LangGraph multi-agent workflow...")
        st.write("   📊 Profiler → 💡 Hypothesis → 📈 Analyst → ✅ Critic → 📝 Narrator → 🧠 Memory")

        ok, stdout, stderr = run_pipeline()

        if ok:
            st.write("✅ All agents completed successfully.")
            st.write("💾 Reports saved.")
            status.update(label="Pipeline completed successfully!", state="complete")
            st.rerun()
        else:
            st.write("❌ Pipeline encountered an error.")
            st.code(stderr, language="text")
            status.update(label="Pipeline failed", state="error")


# ── Live KPI Cards ──────────────────────────────────────────────────────────

render_html('<div class="section-header">📊 Live Market Snapshot</div>')

df = load_kpis()

if df is not None and not df.empty:
    if "fetch_time" in df.columns:
        latest_df = df[df["fetch_time"] == df["fetch_time"].max()]
    else:
        latest_df = df

    score, health_color, mood = calculate_health_score(latest_df)
    total = len(latest_df)
    market_cap = latest_df["market_cap"].sum()
    volume = latest_df["total_volume"].sum()
    bullish = int((latest_df["price_change_percentage_24h"] > 0).sum())
    bearish = int((latest_df["price_change_percentage_24h"] < 0).sum())
    avg_chg = float(latest_df["price_change_percentage_24h"].mean())

    c1, c2, c3, c4, c5, c6 = st.columns(6)

    with c1:
        render_html(kpi_card(
            "📈", "Total Coins", f"{total:,}",
            delta=f"{total} tracked", sub="Live from CoinGecko"
        ))
    with c2:
        render_html(kpi_card(
            "💰", "Market Cap",
            f"${market_cap / 1e12:.2f}T",
            sub="Total capitalisation"
        ))
    with c3:
        render_html(kpi_card(
            "📦", "24h Volume",
            f"${volume / 1e9:.2f}B",
            sub="Trading activity"
        ))
    with c4:
        pos = delta_positive = avg_chg >= 0
        render_html(kpi_card(
            "📊", "Avg 24h Return",
            f"{avg_chg:+.2f}%",
            delta=f"{avg_chg:+.2f}% today",
            delta_positive=pos,
            sub="Across all assets"
        ))
    with c5:
        render_html(kpi_card(
            "🟢", "Bullish Coins",
            f"{bullish}",
            delta=f"{bullish / total * 100:.0f}% of market",
            delta_positive=True,
            sub=f"{bearish} bearish"
        ))
    with c6:
        render_html(f"""
        <div class="kpi-card">
            <div class="kpi-icon">🏥</div>
            <div class="kpi-label">Market Health</div>
            <div class="kpi-value" style="color:{health_color};">{score}/100</div>
            <div class="kpi-delta" style="color:{health_color};">{mood}</div>
            <div class="kpi-sub">AI confidence score</div>
        </div>
        """)
else:
    st.info("No data yet. Click **▶ Run Pipeline** above to fetch live data.")


# ── AI Workflow Diagram ──────────────────────────────────────────────────────

render_html('<div class="section-header">🔄 AI Agent Pipeline</div>')

render_html("""
<div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.06);
            border-radius:16px; padding:1rem 2rem;">
""")

render_html(render_workflow_pipeline())

render_html("</div>")


# ── Agent Overview Cards ─────────────────────────────────────────────────────

render_html('<div class="section-header">🤖 AI Agents</div>')

agents = [
    ("📊", "Profiler Agent",   "#a78bfa", "Statistical",
     "Profiles schema, detects missing values, computes correlation matrix and outliers."),
    ("💡", "Hypothesis Agent", "#60a5fa", "Gemini",
     "Generates 5 statistically testable business hypotheses from the data profile."),
    ("📈", "Analyst Agent",    "#34d399", "Statistical",
     "Executes Pearson, Spearman, Linear Regression, T-Test and ANOVA autonomously."),
    ("✅", "Critic Agent",     "#fbbf24", "Gemini",
     "Peer-reviews every statistical result and approves findings with confidence ratings."),
    ("📝", "Narrator Agent",   "#f87171", "Gemini",
     "Writes executive summaries and business recommendations from approved analyses."),
    ("🧠", "Memory Agent",     "#a78bfa", "Historical",
     "Detects cross-run trends, streaks, rolling averages, anomalies and divergences."),
]

cols = st.columns(3)

for i, (icon, title, color, tag, desc) in enumerate(agents):
    with cols[i % 3]:
        render_html(f"""
        <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.06);
                    border-radius:14px; padding:1.2rem 1.3rem; margin-bottom:0.8rem;
                    border-left:3px solid {color}33;">
            <div style="display:flex; align-items:center; gap:0.6rem; margin-bottom:0.6rem;">
                <div style="font-size:1.3rem;">{icon}</div>
                <div>
                    <div style="font-size:0.88rem; font-weight:600; color:#e2e8f0;">{title}</div>
                    <div style="display:inline-block; padding:0.1rem 0.5rem;
                                border-radius:100px; font-size:0.62rem; font-weight:700;
                                background:{color}18; color:{color}; border:1px solid {color}33;
                                margin-top:0.2rem;">{tag}</div>
                </div>
            </div>
            <div style="font-size:0.82rem; color:rgba(255,255,255,0.45); line-height:1.5;">{desc}</div>
        </div>
        """)

render_html("""
<div style="text-align:center; color:rgba(255,255,255,0.2); font-size:0.75rem; padding:2rem 0 0.5rem 0;">
    ADA &nbsp;•&nbsp; Built with Python, LangGraph, Gemini AI, SQLite &amp; Streamlit
</div>
""")