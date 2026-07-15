import sqlite3
import pandas as pd
import plotly.express as px
import streamlit as st
from pathlib import Path
from ui.components import render_sidebar, SHARED_CSS, render_html

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "warehouse.db"

st.set_page_config(
    page_title="History — ADA",
    page_icon="📜",
    layout="wide"
)

st.markdown(SHARED_CSS, unsafe_allow_html=True)
render_sidebar()

T = "plotly_dark"
GREEN  = "#34d399"
RED    = "#f87171"
PURPLE = "#a78bfa"
BLUE   = "#60a5fa"
AMBER  = "#fbbf24"

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(t=10, b=10, l=10, r=10),
    font=dict(family="Inter", size=12, color="#94a3b8"),
    hoverlabel=dict(
        bgcolor="#1e293b", font_color="#e2e8f0",
        font_family="Inter", font_size=13,
        bordercolor="rgba(255,255,255,0.1)"
    )
)


@st.cache_data
def load_history():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT * FROM market_history ORDER BY id DESC", conn
    )
    conn.close()
    return df


render_html("""
<div style="padding:0.5rem 0 0.5rem 0;">
    <div style="font-size:1.75rem; font-weight:800;
                background:linear-gradient(90deg,#34d399,#60a5fa);
                -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                margin-bottom:0.2rem;">📜 Market History</div>
    <div style="font-size:0.85rem; color:rgba(255,255,255,0.35);">
        Historical snapshots from every pipeline run — trends, timelines and executive summaries
    </div>
</div>
""")

with st.spinner("Loading history..."):
    history = load_history()

if history.empty:
    st.warning("No history yet. Run the pipeline at least once.")
    st.stop()

latest    = history.iloc[0]
asc       = history.sort_values("id")
total_runs = len(history)


# ── Run Summary KPIs ─────────────────────────────────────────────────────────

render_html('<div class="section-header">Run Summary</div>')

h1, h2, h3, h4 = st.columns(4)

h1.metric("Pipeline Runs", total_runs)
h2.metric("Latest Sentiment", latest["sentiment"])
h3.metric("Latest Market Cap", f"${latest['total_market_cap'] / 1e12:.2f}T")
h4.metric("Latest Volume", f"${latest['total_volume'] / 1e9:.2f}B")


# ── Timeline ─────────────────────────────────────────────────────────────────

render_html('<div class="section-header">Timeline</div>')

for i, (_, row) in enumerate(history.iterrows()):
    run_num = total_runs - i
    sent = row["sentiment"]
    sent_color = {"Bullish": "#34d399", "Bearish": "#f87171"}.get(sent, "#fbbf24")
    sent_bg    = {"Bullish": "rgba(52,211,153,0.06)", "Bearish": "rgba(248,113,113,0.06)"}.get(sent, "rgba(251,191,36,0.06)")
    sent_brd   = {"Bullish": "rgba(52,211,153,0.2)", "Bearish": "rgba(248,113,113,0.2)"}.get(sent, "rgba(251,191,36,0.2)")

    cap_prev = history.iloc[i + 1]["total_market_cap"] if i + 1 < len(history) else row["total_market_cap"]
    vol_prev = history.iloc[i + 1]["total_volume"] if i + 1 < len(history) else row["total_volume"]
    cap_arrow = "▲" if row["total_market_cap"] >= cap_prev else "▼"
    vol_arrow = "▲" if row["total_volume"] >= vol_prev else "▼"
    cap_col = GREEN if cap_arrow == "▲" else RED
    vol_col = GREEN if vol_arrow == "▲" else RED

    try:
        from datetime import datetime
        dt = datetime.strptime(str(row["run_time"]), "%Y-%m-%d %H:%M:%S")
        date_str = dt.strftime("%d %b %Y")
        time_str = dt.strftime("%H:%M")
    except Exception:
        date_str = str(row["run_time"])[:10]
        time_str = ""

    with st.expander(
        f"Run #{run_num}  ·  {date_str} {time_str}  ·  {sent}  ·  ${row['total_market_cap']/1e12:.2f}T",
        expanded=(i == 0)
    ):
        tc1, tc2, tc3, tc4, tc5 = st.columns(5)

        with tc1:
            render_html(f"""
            <div style="text-align:center;">
                <div style="font-size:0.62rem; text-transform:uppercase; letter-spacing:0.08em;
                            color:rgba(255,255,255,0.3); margin-bottom:0.3rem;">Sentiment</div>
                <div style="font-size:1.1rem; font-weight:700; color:{sent_color};">{sent}</div>
            </div>
            """)

        with tc2:
            render_html(f"""
            <div style="text-align:center;">
                <div style="font-size:0.62rem; text-transform:uppercase; letter-spacing:0.08em;
                            color:rgba(255,255,255,0.3); margin-bottom:0.3rem;">Market Cap</div>
                <div style="font-size:1.1rem; font-weight:700; color:{cap_col};">{cap_arrow} ${row['total_market_cap']/1e12:.2f}T</div>
            </div>
            """)

        with tc3:
            render_html(f"""
            <div style="text-align:center;">
                <div style="font-size:0.62rem; text-transform:uppercase; letter-spacing:0.08em;
                            color:rgba(255,255,255,0.3); margin-bottom:0.3rem;">Volume</div>
                <div style="font-size:1.1rem; font-weight:700; color:{vol_col};">{vol_arrow} ${row['total_volume']/1e9:.1f}B</div>
            </div>
            """)

        with tc4:
            render_html(f"""
            <div style="text-align:center;">
                <div style="font-size:0.62rem; text-transform:uppercase; letter-spacing:0.08em;
                            color:rgba(255,255,255,0.3); margin-bottom:0.3rem;">Avg Return</div>
                <div style="font-size:1.1rem; font-weight:700;
                            color:{'#34d399' if row['average_change'] >= 0 else '#f87171'};">
                    {'+' if row['average_change'] >= 0 else ''}{row['average_change']:.2f}%
                </div>
            </div>
            """)

        with tc5:
            render_html(f"""
            <div style="text-align:center;">
                <div style="font-size:0.62rem; text-transform:uppercase; letter-spacing:0.08em;
                            color:rgba(255,255,255,0.3); margin-bottom:0.3rem;">Coins</div>
                <div style="font-size:1.1rem; font-weight:700; color:#e2e8f0;">
                    🟢{row['positive_coins']} / 🔴{row['negative_coins']}
                </div>
            </div>
            """)

        if row["summary"]:
            render_html(f"""
            <div style="margin-top:0.8rem; background:rgba(255,255,255,0.02);
                        border:1px solid rgba(255,255,255,0.06); border-radius:10px;
                        padding:0.85rem 1.1rem; font-size:0.84rem;
                        color:rgba(255,255,255,0.5); line-height:1.65;">
                {row['summary']}
            </div>
            """)
        else:
            st.caption("No AI summary stored for this run.")


# ── Trend Charts ─────────────────────────────────────────────────────────────

render_html('<div class="section-header">Trend Charts</div>')

col_a, col_b = st.columns(2)

with col_a:
    st.caption("💰 Market Capitalization Trend")
    fig = px.line(asc, x="run_time", y="total_market_cap",
                  markers=True, template=T, color_discrete_sequence=[PURPLE],
                  labels={"total_market_cap": "Market Cap (USD)", "run_time": ""})
    fig.update_traces(line_width=2.5, marker_size=8,
                      hovertemplate="<b>%{x}</b><br>$%{y:,.0f}<extra></extra>")
    fig.update_layout(**CHART_LAYOUT, height=280,
                      xaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
                      yaxis=dict(gridcolor="rgba(255,255,255,0.04)"))
    st.plotly_chart(fig, use_container_width=True)

with col_b:
    st.caption("📦 Trading Volume Trend")
    fig = px.line(asc, x="run_time", y="total_volume",
                  markers=True, template=T, color_discrete_sequence=[BLUE],
                  labels={"total_volume": "24h Volume (USD)", "run_time": ""})
    fig.update_traces(line_width=2.5, marker_size=8,
                      hovertemplate="<b>%{x}</b><br>$%{y:,.0f}<extra></extra>")
    fig.update_layout(**CHART_LAYOUT, height=280,
                      xaxis=dict(gridcolor="rgba(255,255,255,0.04)"),
                      yaxis=dict(gridcolor="rgba(255,255,255,0.04)"))
    st.plotly_chart(fig, use_container_width=True)

col_c, col_d = st.columns(2)

with col_c:
    st.caption("📊 Avg 24h Return by Run")
    fig = px.bar(asc, x="run_time", y="average_change",
                 color="average_change",
                 color_continuous_scale=["#f87171", "#475569", "#34d399"],
                 color_continuous_midpoint=0, template=T,
                 labels={"average_change": "Avg 24h Change (%)", "run_time": ""})
    fig.update_layout(**CHART_LAYOUT, height=260, coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

with col_d:
    st.caption("🟢 Bullish vs 🔴 Bearish Coins")
    fig = px.bar(asc, x="run_time",
                 y=["positive_coins", "negative_coins"],
                 barmode="group", template=T,
                 color_discrete_map={"positive_coins": GREEN, "negative_coins": RED},
                 labels={"run_time": "", "value": "Coin Count"})
    fig.update_layout(**CHART_LAYOUT, height=260, legend_title="")
    st.plotly_chart(fig, use_container_width=True)


# ── Download ─────────────────────────────────────────────────────────────────

st.markdown("---")
csv = history.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Download History (CSV)",
    data=csv,
    file_name="ada_market_history.csv",
    mime="text/csv"
)