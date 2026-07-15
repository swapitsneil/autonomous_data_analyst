import json
import pandas as pd
import streamlit as st
from pathlib import Path
from utils.report_manager import load_report
from ui.components import (
    render_sidebar, SHARED_CSS,
    render_pipeline_status, render_workflow_pipeline, render_html
)

BASE_DIR = Path(__file__).resolve().parent.parent
REPORTS_DIR = BASE_DIR / "reports"

st.set_page_config(
    page_title="AI Analysis — ADA",
    page_icon="🤖",
    layout="wide"
)

st.markdown(SHARED_CSS, unsafe_allow_html=True)
render_sidebar()


def get_report_status(name):
    path = REPORTS_DIR / f"{name}.json"
    if not path.exists():
        return "not_run"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data.get("status", "unknown")
    except Exception:
        return "unknown"


render_html("""
<div style="padding:0.5rem 0 0.5rem 0;">
    <div style="font-size:1.75rem; font-weight:800;
                background:linear-gradient(90deg,#a78bfa,#60a5fa);
                -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                margin-bottom:0.2rem;">🤖 AI Analysis Report</div>
    <div style="font-size:0.85rem; color:rgba(255,255,255,0.35);">
        Full output from every agent in the LangGraph workflow
    </div>
</div>
""")

# ── Pipeline Status (GitHub Actions style) ──────────────────────────────────

render_html('<div class="section-header">Pipeline Status</div>')

statuses = {
    "profile":    get_report_status("profile"),
    "hypotheses": get_report_status("hypotheses"),
    "analysis":   get_report_status("analysis"),
    "critic":     get_report_status("critic"),
    "narrator":   get_report_status("narrator"),
    "memory":     get_report_status("memory"),
}

render_html(render_pipeline_status(statuses))

# Load all reports

try:
    profile    = load_report("profile")
    hypotheses = load_report("hypotheses")
    analysis   = load_report("analysis")
    critic     = load_report("critic")
    narrator   = load_report("narrator")
    memory     = load_report("memory")
except Exception:
    st.warning("Reports not found. Run the pipeline from the Home page.")
    st.stop()


# ── Profiler Agent ──────────────────────────────────────────────────────────

render_html('<div class="section-header">📊 Profiler Agent</div>')

info = profile.get("dataset_info", {})

pc1, pc2, pc3, pc4 = st.columns(4)

with pc1:
    render_html(f"""
    <div style="background:rgba(167,139,250,0.06); border:1px solid rgba(167,139,250,0.2);
                border-radius:12px; padding:1rem 1.2rem; text-align:center;">
        <div style="font-size:0.65rem; font-weight:700; letter-spacing:0.08em;
                    text-transform:uppercase; color:rgba(255,255,255,0.35); margin-bottom:0.3rem;">Rows</div>
        <div style="font-size:1.8rem; font-weight:800; color:#e2e8f0;">{info.get('rows','—')}</div>
    </div>
    """)

with pc2:
    render_html(f"""
    <div style="background:rgba(96,165,250,0.06); border:1px solid rgba(96,165,250,0.2);
                border-radius:12px; padding:1rem 1.2rem; text-align:center;">
        <div style="font-size:0.65rem; font-weight:700; letter-spacing:0.08em;
                    text-transform:uppercase; color:rgba(255,255,255,0.35); margin-bottom:0.3rem;">Columns</div>
        <div style="font-size:1.8rem; font-weight:800; color:#e2e8f0;">{info.get('columns','—')}</div>
    </div>
    """)

with pc3:
    render_html(f"""
    <div style="background:rgba(52,211,153,0.06); border:1px solid rgba(52,211,153,0.2);
                border-radius:12px; padding:1rem 1.2rem; text-align:center;">
        <div style="font-size:0.65rem; font-weight:700; letter-spacing:0.08em;
                    text-transform:uppercase; color:rgba(255,255,255,0.35); margin-bottom:0.3rem;">Missing</div>
        <div style="font-size:1.8rem; font-weight:800; color:#e2e8f0;">{info.get('missing_values','—')}</div>
    </div>
    """)

with pc4:
    render_html(f"""
    <div style="background:rgba(251,191,36,0.06); border:1px solid rgba(251,191,36,0.2);
                border-radius:12px; padding:1rem 1.2rem; text-align:center;">
        <div style="font-size:0.65rem; font-weight:700; letter-spacing:0.08em;
                    text-transform:uppercase; color:rgba(255,255,255,0.35); margin-bottom:0.3rem;">Duplicates</div>
        <div style="font-size:1.8rem; font-weight:800; color:#e2e8f0;">{info.get('duplicates','—')}</div>
    </div>
    """)

col_n, col_c = st.columns(2)
with col_n:
    with st.expander("Numeric Columns"):
        st.write(profile.get("numeric_columns", []))
with col_c:
    with st.expander("Categorical Columns"):
        st.write(profile.get("categorical_columns", []))

with st.expander("📋 Summary Statistics"):
    stats = profile.get("summary_statistics", {})
    if stats:
        st.dataframe(pd.DataFrame(stats).T, use_container_width=True)


# ── Hypothesis Agent ────────────────────────────────────────────────────────

render_html('<div class="section-header">💡 Hypothesis Agent</div>')

if hypotheses.get("status") == "failed":
    st.error(f"Hypothesis Agent failed: {hypotheses.get('error', '')}")
else:
    for h in hypotheses.get("hypotheses", []):
        test = h.get("recommended_test", "").replace("_", " ").title()
        priority = h.get("priority", "Medium")
        p_color = {"High": "#34d399", "Medium": "#fbbf24", "Low": "#f87171"}.get(priority, "#94a3b8")

        with st.expander(f"{h.get('id','')}  —  {h.get('statement','')[:80]}..."):
            render_html(f"""
            <div style="margin-bottom:0.6rem;">
                <span class="badge badge-purple">{h.get('id','')}</span>
                <span class="badge badge-blue">{test}</span>
                <span style="display:inline-block; padding:0.15rem 0.6rem; border-radius:100px;
                             font-size:0.68rem; font-weight:700; background:{p_color}18;
                             color:{p_color}; border:1px solid {p_color}33;">{priority} Priority</span>
            </div>
            <div style="font-size:0.9rem; color:#e2e8f0; line-height:1.6;">{h.get('statement','')}</div>
            """)


# ── Analyst Agent ───────────────────────────────────────────────────────────

render_html('<div class="section-header">📈 Analyst Agent</div>')

if analysis.get("status") == "skipped":
    st.warning(f"Analyst skipped: {analysis.get('reason', '')}")
else:
    for result in analysis.get("analysis", []):
        sig = result.get("significant", False)
        status_label = result.get("status", "")
        test = result.get("test", "").replace("_", " ").title()
        sig_class = "badge-green" if sig else "badge-red"
        sig_label = "Significant" if sig else "Not Significant"

        chips = []
        if result.get("correlation") is not None:
            chips.append(f"<b>r</b> = {result['correlation']}")
        if result.get("r2_score") is not None:
            chips.append(f"<b>R²</b> = {result['r2_score']}")
        if result.get("adjusted_r2") is not None:
            chips.append(f"<b>Adj R²</b> = {result['adjusted_r2']}")
        if result.get("f_statistic") is not None:
            chips.append(f"<b>F</b> = {result['f_statistic']}")
        if result.get("t_statistic") is not None:
            chips.append(f"<b>t</b> = {result['t_statistic']}")
        if result.get("p_value") is not None:
            chips.append(f"<b>p</b> = {result['p_value']}")
        if result.get("effect_strength"):
            chips.append(f"Effect: {result['effect_strength']}")

        chips_html = "".join(
            f'<span style="background:rgba(255,255,255,0.04); border:1px solid rgba(255,255,255,0.08); '
            f'border-radius:6px; padding:0.2rem 0.7rem; font-size:0.76rem; '
            f'color:rgba(255,255,255,0.6);">{c}</span>'
            for c in chips
        )

        with st.expander(f"{result.get('id','')}  —  {result.get('statement','')[:75]}..."):
            render_html(f"""
            <div style="margin-bottom:0.7rem;">
                <span class="badge badge-purple">{result.get('id','')}</span>
                <span class="badge badge-blue">{test}</span>
                <span class="badge {sig_class}">{sig_label}</span>
                <span class="badge {'badge-green' if status_label=='Completed' else 'badge-amber'}">{status_label}</span>
            </div>
            <div style="font-size:0.88rem; color:#e2e8f0; margin-bottom:0.6rem;">{result.get('statement','')}</div>
            <div style="display:flex; gap:0.5rem; flex-wrap:wrap;">{chips_html}</div>
            """)


# ── Critic Agent ────────────────────────────────────────────────────────────

render_html('<div class="section-header">✅ Critic Agent</div>')

if critic.get("status") in ("failed", "skipped"):
    st.warning(f"Critic {critic.get('status')}: {critic.get('error', critic.get('reason', ''))}")
else:
    reviews = critic.get("reviews", [])
    approved_count = sum(1 for r in reviews if r.get("approved"))

    cr1, cr2, cr3 = st.columns(3)
    cr1.metric("✅ Approved", approved_count)
    cr2.metric("❌ Rejected", len(reviews) - approved_count)
    cr3.metric("📊 Approval Rate", f"{approved_count / len(reviews) * 100:.0f}%" if reviews else "—")

    for review in reviews:
        approved = review.get("approved", False)
        bg   = "rgba(52,211,153,0.05)"  if approved else "rgba(248,113,113,0.05)"
        brd  = "rgba(52,211,153,0.2)"   if approved else "rgba(248,113,113,0.2)"
        icon = "✅" if approved else "❌"
        conf = review.get("confidence", "—")
        conf_c = {"High": "#34d399", "Medium": "#fbbf24", "Low": "#f87171"}.get(conf, "#94a3b8")

        render_html(f"""
        <div style="background:{bg}; border:1px solid {brd}; border-radius:12px;
                    padding:1rem 1.2rem; margin-bottom:0.6rem;">
            <div style="margin-bottom:0.4rem;">
                <span class="badge badge-purple">{review.get('id','')}</span>
                <span style="font-size:0.8rem; font-weight:600; color:#e2e8f0;">{icon} {'Approved' if approved else 'Rejected'}</span>
                &nbsp;
                <span style="font-size:0.72rem; color:{conf_c}; font-weight:600;">● {conf} Confidence</span>
            </div>
            <div style="font-size:0.82rem; color:rgba(255,255,255,0.5); line-height:1.5;">
                {review.get('feedback','')[:200]}{'...' if len(review.get('feedback','')) > 200 else ''}
            </div>
        </div>
        """)


# ── Narrator Agent ──────────────────────────────────────────────────────────

render_html('<div class="section-header">📝 Narrator Agent — Executive Report</div>')

if narrator.get("status") in ("failed", "skipped"):
    st.warning(f"Narrator {narrator.get('status')}: {narrator.get('error', narrator.get('reason', ''))}")
else:
    summary = narrator.get("executive_summary", "")
    if summary:
        render_html(f'<div class="summary-box">💬 {summary}</div>')

    col_f, col_r = st.columns(2)
    with col_f:
        st.markdown("**🔍 Key Findings**")
        for f in narrator.get("key_findings", []):
            render_html(f'<div class="info-box">{f}</div>')
    with col_r:
        st.markdown("**💡 Recommendations**")
        for r in narrator.get("recommendations", []):
            render_html(f'<div class="insight-box">{r}</div>')

    conclusion = narrator.get("conclusion", "")
    if conclusion:
        render_html(f"""
        <div style="background:linear-gradient(135deg,rgba(167,139,250,0.08),rgba(96,165,250,0.05));
                    border:1px solid rgba(167,139,250,0.15); border-radius:12px;
                    padding:1.1rem 1.3rem; margin-top:1rem;">
            <div style="font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.08em;
                        color:rgba(255,255,255,0.3); margin-bottom:0.4rem;">Conclusion</div>
            <div style="font-size:0.88rem; color:#c4b5fd; line-height:1.7;">{conclusion}</div>
        </div>
        """)


# ── Memory Agent ────────────────────────────────────────────────────────────

render_html('<div class="section-header">🧠 Memory Agent</div>')

if memory.get("status") in ("failed", "skipped"):
    st.warning(f"Memory {memory.get('status')}: {memory.get('error', memory.get('reason', ''))}")
else:
    snapshot = memory.get("current_snapshot", {})
    mem = memory.get("memory", {})

    ms1, ms2, ms3, ms4 = st.columns(4)
    ms1.metric("Runs Analyzed", memory.get("runs_analyzed", "—"))
    ms2.metric("Market Cap", f"${snapshot.get('total_market_cap',0)/1e12:.2f}T")
    ms3.metric("Volume", f"${snapshot.get('total_volume',0)/1e9:.2f}B")
    ms4.metric("Sentiment", snapshot.get("sentiment", "—"))

    historical = mem.get("historical_insights", [])
    if historical:
        st.markdown("**🔬 Historical Intelligence**")
        for insight in historical:
            render_html(f'<div class="info-box">🔍 {insight}</div>')