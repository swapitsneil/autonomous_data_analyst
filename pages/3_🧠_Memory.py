import streamlit as st
from utils.report_manager import load_report
from ui.components import render_sidebar, SHARED_CSS, render_html

st.set_page_config(
    page_title="Memory — ADA",
    page_icon="🧠",
    layout="wide"
)

st.markdown(SHARED_CSS, unsafe_allow_html=True)
render_sidebar()

render_html("""
<div style="padding:0.5rem 0 0.5rem 0;">
    <div style="font-size:1.75rem; font-weight:800;
                background:linear-gradient(90deg,#fbbf24,#f87171);
                -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                margin-bottom:0.2rem;">🧠 Memory Intelligence</div>
    <div style="font-size:0.85rem; color:rgba(255,255,255,0.35);">
        Historical pattern analysis across all pipeline runs
    </div>
</div>
""")

try:
    memory = load_report("memory")
except Exception:
    st.warning("Memory report not found. Run the pipeline from the Home page.")
    st.stop()

if memory.get("status") != "success":
    st.error(f"Memory Agent failed: {memory.get('error', memory.get('reason', ''))}")
    with st.expander("Raw Output"):
        st.json(memory)
    st.stop()

snapshot = memory.get("current_snapshot", {})
mem = memory.get("memory", {})
runs = memory.get("runs_analyzed", 1)


# ── Market Intelligence Header ───────────────────────────────────────────────

render_html('<div class="section-header">📈 Market Intelligence</div>')

sentiment = snapshot.get("sentiment", "Neutral")
s_color = {"Bullish": "#34d399", "Bearish": "#f87171"}.get(sentiment, "#fbbf24")
avg_chg = snapshot.get("average_change", 0)
pos = snapshot.get("positive_coins", 0)
neg = snapshot.get("negative_coins", 0)
total_coins = pos + neg
pos_pct = f"{pos / total_coins * 100:.0f}%" if total_coins else "—"

col_s, col_c, col_d, col_a = st.columns(4)

with col_s:
    render_html(f"""
    <div style="background:rgba(255,255,255,0.03); border:1px solid {s_color}33;
                border-radius:14px; padding:1.3rem; border-top:3px solid {s_color};">
        <div style="font-size:0.65rem; font-weight:700; text-transform:uppercase;
                    letter-spacing:0.1em; color:rgba(255,255,255,0.3); margin-bottom:0.5rem;">Sentiment</div>
        <div style="font-size:1.7rem; font-weight:800; color:{s_color};">{sentiment}</div>
        <div style="font-size:0.78rem; color:rgba(255,255,255,0.35); margin-top:0.3rem;">{runs} runs analyzed</div>
    </div>
    """)

with col_c:
    conf_icon = "🟢" if sentiment == "Bullish" else "🔴" if sentiment == "Bearish" else "🟡"
    conf_label = "High" if pos / total_coins >= 0.6 else "Medium" if pos / total_coins >= 0.4 else "Low"
    conf_color = {"High": "#34d399", "Medium": "#fbbf24", "Low": "#f87171"}.get(conf_label, "#94a3b8")
    render_html(f"""
    <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.06);
                border-radius:14px; padding:1.3rem; border-top:3px solid {conf_color};">
        <div style="font-size:0.65rem; font-weight:700; text-transform:uppercase;
                    letter-spacing:0.1em; color:rgba(255,255,255,0.3); margin-bottom:0.5rem;">Confidence</div>
        <div style="font-size:1.7rem; font-weight:800; color:{conf_color};">{conf_label}</div>
        <div style="font-size:0.78rem; color:rgba(255,255,255,0.35); margin-top:0.3rem;">{pos_pct} positive coins</div>
    </div>
    """)

with col_d:
    chg_sign = "▲" if avg_chg >= 0 else "▼"
    chg_color = "#34d399" if avg_chg >= 0 else "#f87171"
    render_html(f"""
    <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.06);
                border-radius:14px; padding:1.3rem; border-top:3px solid {chg_color};">
        <div style="font-size:0.65rem; font-weight:700; text-transform:uppercase;
                    letter-spacing:0.1em; color:rgba(255,255,255,0.3); margin-bottom:0.5rem;">Avg 24h Change</div>
        <div style="font-size:1.7rem; font-weight:800; color:{chg_color};">{chg_sign} {avg_chg:+.2f}%</div>
        <div style="font-size:0.78rem; color:rgba(255,255,255,0.35); margin-top:0.3rem;">Across all assets</div>
    </div>
    """)

with col_a:
    mc = snapshot.get("total_market_cap", 0)
    vol = snapshot.get("total_volume", 0)
    render_html(f"""
    <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.06);
                border-radius:14px; padding:1.3rem; border-top:3px solid #a78bfa;">
        <div style="font-size:0.65rem; font-weight:700; text-transform:uppercase;
                    letter-spacing:0.1em; color:rgba(255,255,255,0.3); margin-bottom:0.5rem;">Market Cap</div>
        <div style="font-size:1.7rem; font-weight:800; color:#a78bfa;">${mc/1e12:.2f}T</div>
        <div style="font-size:0.78rem; color:rgba(255,255,255,0.35); margin-top:0.3rem;">Vol: ${vol/1e9:.1f}B</div>
    </div>
    """)


# ── Previous Run Comparison ──────────────────────────────────────────────────

comparison = mem.get("comparison")

if comparison is None:
    st.markdown("---")
    st.info("First pipeline run — historical intelligence activates from the next run.")
else:
    render_html('<div class="section-header">📊 vs Previous Run</div>')

    cap_chg = comparison.get("market_cap_change_percent", 0)
    vol_chg = comparison.get("volume_change_percent", 0)
    avg_diff = comparison.get("average_change_difference", 0)
    pos_diff = comparison.get("positive_coin_difference", 0)

    def delta_html(val, suffix=""):
        color = "#34d399" if val >= 0 else "#f87171"
        arrow = "▲" if val >= 0 else "▼"
        return f'<span style="color:{color}; font-weight:700;">{arrow} {abs(val)}{suffix}</span>'

    cv1, cv2, cv3, cv4 = st.columns(4)

    with cv1:
        render_html(f"""
        <div style="background:rgba(255,255,255,0.025); border:1px solid rgba(255,255,255,0.06);
                    border-radius:12px; padding:1.1rem 1.2rem; text-align:center;">
            <div style="font-size:0.65rem; text-transform:uppercase; letter-spacing:0.08em;
                        color:rgba(255,255,255,0.3); margin-bottom:0.3rem;">Market Cap</div>
            <div style="font-size:1.4rem; font-weight:800; color:#e2e8f0;">{delta_html(cap_chg,'%')}</div>
        </div>
        """)

    with cv2:
        render_html(f"""
        <div style="background:rgba(255,255,255,0.025); border:1px solid rgba(255,255,255,0.06);
                    border-radius:12px; padding:1.1rem 1.2rem; text-align:center;">
            <div style="font-size:0.65rem; text-transform:uppercase; letter-spacing:0.08em;
                        color:rgba(255,255,255,0.3); margin-bottom:0.3rem;">Volume</div>
            <div style="font-size:1.4rem; font-weight:800; color:#e2e8f0;">{delta_html(vol_chg,'%')}</div>
        </div>
        """)

    with cv3:
        render_html(f"""
        <div style="background:rgba(255,255,255,0.025); border:1px solid rgba(255,255,255,0.06);
                    border-radius:12px; padding:1.1rem 1.2rem; text-align:center;">
            <div style="font-size:0.65rem; text-transform:uppercase; letter-spacing:0.08em;
                        color:rgba(255,255,255,0.3); margin-bottom:0.3rem;">Avg Return Δ</div>
            <div style="font-size:1.4rem; font-weight:800; color:#e2e8f0;">{delta_html(avg_diff,'%')}</div>
        </div>
        """)

    with cv4:
        prev_sent = comparison.get("previous_sentiment", "—")
        curr_sent = comparison.get("current_sentiment", "—")
        arrow_col = "#34d399" if curr_sent == "Bullish" else "#f87171"
        render_html(f"""
        <div style="background:rgba(255,255,255,0.025); border:1px solid rgba(255,255,255,0.06);
                    border-radius:12px; padding:1.1rem 1.2rem; text-align:center;">
            <div style="font-size:0.65rem; text-transform:uppercase; letter-spacing:0.08em;
                        color:rgba(255,255,255,0.3); margin-bottom:0.3rem;">Sentiment</div>
            <div style="font-size:1rem; font-weight:700; color:#e2e8f0;">
                {prev_sent} <span style="color:rgba(255,255,255,0.3);">→</span>
                <span style="color:{arrow_col};">{curr_sent}</span>
            </div>
        </div>
        """)


# ── AI Memory — Business Insights ────────────────────────────────────────────

render_html('<div class="section-header">🧠 AI Memory</div>')

business_insights = mem.get("business_insights", [])
for insight in business_insights:
    render_html(f'<div class="insight-box">  {insight}</div>')


# ── Historical Intelligence ──────────────────────────────────────────────────

historical = mem.get("historical_insights", [])
if historical:
    render_html(f'<div class="section-header">🔬 Historical Intelligence — {runs} Runs Analyzed</div>')
    for insight in historical:
        render_html(f'<div class="info-box">🔍 {insight}</div>')


# ── Sentiment Comparison ─────────────────────────────────────────────────────

if comparison:
    render_html('<div class="section-header">🎭 Sentiment Timeline</div>')
    col_prev, col_curr = st.columns(2)

    prev_sent = comparison.get("previous_sentiment", "—")
    curr_sent = comparison.get("current_sentiment", "—")

    for col, label, sent in [(col_prev, "Previous Run", prev_sent), (col_curr, "Current Run", curr_sent)]:
        sent_color = {"Bullish": "#34d399", "Bearish": "#f87171"}.get(sent, "#fbbf24")
        with col:
            render_html(f"""
            <div style="background:rgba(255,255,255,0.025); border:1px solid {sent_color}22;
                        border-radius:14px; padding:1.5rem; text-align:center;">
                <div style="font-size:0.65rem; text-transform:uppercase; letter-spacing:0.1em;
                            color:rgba(255,255,255,0.3); margin-bottom:0.6rem;">{label}</div>
                <div style="font-size:2rem; font-weight:800; color:{sent_color};">{sent}</div>
            </div>
            """)


# ── Previous Summary ─────────────────────────────────────────────────────────

prev_summary = mem.get("previous_summary", "")
if prev_summary:
    render_html('<div class="section-header">📝 Previous Executive Summary</div>')
    render_html(f'<div class="summary-box">{prev_summary}</div>')