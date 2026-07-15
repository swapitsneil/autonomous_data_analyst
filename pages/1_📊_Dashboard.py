import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from utils.report_manager import load_report
from utils.report_generator import generate_html_report
from ui.components import (
    render_sidebar, SHARED_CSS, kpi_card, calculate_health_score, render_html
)

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "warehouse.db"

st.set_page_config(
    page_title="Dashboard — ADA",
    page_icon="📊",
    layout="wide"
)

st.markdown(SHARED_CSS, unsafe_allow_html=True)
render_sidebar()

T = "plotly_dark"
PURPLE = "#a78bfa"
BLUE   = "#60a5fa"
GREEN  = "#34d399"
RED    = "#f87171"
AMBER  = "#fbbf24"

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(t=10, b=10, l=10, r=10),
    font=dict(family="Inter", size=12, color="#94a3b8"),
    hoverlabel=dict(
        bgcolor="#1e293b",
        font_color="#e2e8f0",
        font_family="Inter",
        font_size=13,
        bordercolor="rgba(255,255,255,0.1)"
    ),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94a3b8")
    )
)


@st.cache_data
def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM crypto_market", conn)
    conn.close()
    return df


# Header with PDF button

col_title, col_pdf = st.columns([7, 2])

with col_title:
    render_html("""
    <div style="padding:0.5rem 0 0.5rem 0;">
        <div style="font-size:1.75rem; font-weight:800;
                    background:linear-gradient(90deg,#a78bfa,#60a5fa);
                    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                    margin-bottom:0.2rem;">📊 Dashboard</div>
        <div style="font-size:0.85rem; color:rgba(255,255,255,0.35);">
            Real-time market data &nbsp;•&nbsp; Statistical analysis &nbsp;•&nbsp; AI insights
        </div>
    </div>
    """)

with col_pdf:
    try:
        html_bytes = generate_html_report()
        st.download_button(
            label="⬇ Download Report",
            data=html_bytes,
            file_name=f"ADA_Executive_Report.html",
            mime="text/html",
            use_container_width=True,
            type="secondary"
        )
    except Exception:
        pass

with st.spinner("Loading market data..."):
    df = load_data()

try:
    narrator = load_report("narrator")
    memory   = load_report("memory")
except Exception:
    narrator = {}
    memory   = {}

if df.empty:
    st.warning("No data found. Run the pipeline from the Home page.")
    st.stop()

if "fetch_time" in df.columns:
    latest_df = df[df["fetch_time"] == df["fetch_time"].max()].copy()
else:
    latest_df = df.copy()

total       = len(latest_df)
market_cap  = latest_df["market_cap"].sum()
volume      = latest_df["total_volume"].sum()
avg_price   = latest_df["current_price"].mean()
avg_chg     = latest_df["price_change_percentage_24h"].mean()
bullish     = int((latest_df["price_change_percentage_24h"] > 0).sum())
bearish     = int((latest_df["price_change_percentage_24h"] < 0).sum())
score, health_color, mood = calculate_health_score(latest_df)


# ── KPI Cards ───────────────────────────────────────────────────────────────

render_html('<div class="section-header">Market Overview</div>')

c1, c2, c3, c4, c5, c6, c7 = st.columns(7)

with c1:
    render_html(kpi_card("🏥", "Market Health", f"{score}/100",
        delta=mood, delta_positive=score >= 50,
        sub="AI confidence"))
with c2:
    render_html(kpi_card("📈", "Coins Tracked", f"{total:,}",
        sub="Live from CoinGecko"))
with c3:
    render_html(kpi_card("💰", "Market Cap", f"${market_cap/1e12:.2f}T",
        sub="Total capitalisation"))
with c4:
    render_html(kpi_card("📦", "24h Volume", f"${volume/1e9:.2f}B",
        sub="Trading activity"))
with c5:
    pos = avg_chg >= 0
    render_html(kpi_card("📊", "Avg 24h Return", f"{avg_chg:+.2f}%",
        delta=f"{avg_chg:+.2f}% today", delta_positive=pos,
        sub="Across all assets"))
with c6:
    render_html(kpi_card("🟢", "Bullish Coins", str(bullish),
        delta=f"{bullish / total * 100:.0f}% of market", delta_positive=True,
        sub=f"{bearish} bearish today"))
with c7:
    next_update = "On demand"
    render_html(kpi_card("🔄", "Next Update", "On Demand",
        sub="Click ▶ Run Pipeline"))


# ── AI Executive Summary ─────────────────────────────────────────────────────

if narrator.get("status") == "success":
    summary = narrator.get("executive_summary", "")
    if summary:
        render_html('<div class="section-header">AI Executive Summary</div>')
        render_html(f'<div class="summary-box">💬 {summary}</div>')

    col_f, col_r = st.columns(2)
    with col_f:
        render_html('<div class="section-header">Key Findings</div>')
        for f in narrator.get("key_findings", []):
            render_html(f'<div class="info-box">🔍 {f}</div>')
    with col_r:
        render_html('<div class="section-header">Recommendations</div>')
        for r in narrator.get("recommendations", []):
            render_html(f'<div class="insight-box">💡 {r}</div>')


# ── Charts ──────────────────────────────────────────────────────────────────

render_html('<div class="section-header">Market Analysis</div>')

gainers = latest_df.sort_values("price_change_percentage_24h", ascending=False).head(10)
losers  = latest_df.sort_values("price_change_percentage_24h", ascending=True).head(10)

col_g, col_l = st.columns(2)

with col_g:
    st.caption("🚀 Top 10 Gainers")
    fig = px.bar(gainers, x="name", y="price_change_percentage_24h",
                 color_discrete_sequence=[GREEN], template=T,
                 labels={"price_change_percentage_24h": "24h Change (%)", "name": ""})
    fig.update_traces(marker_line_width=0)
    fig.update_layout(**CHART_LAYOUT, height=300,
                      xaxis=dict(tickangle=-30, gridcolor="rgba(255,255,255,0.04)"),
                      yaxis=dict(gridcolor="rgba(255,255,255,0.04)"))
    st.plotly_chart(fig, use_container_width=True)

with col_l:
    st.caption("📉 Top 10 Losers")
    fig = px.bar(losers, x="name", y="price_change_percentage_24h",
                 color_discrete_sequence=[RED], template=T,
                 labels={"price_change_percentage_24h": "24h Change (%)", "name": ""})
    fig.update_traces(marker_line_width=0)
    fig.update_layout(**CHART_LAYOUT, height=300,
                      xaxis=dict(tickangle=-30, gridcolor="rgba(255,255,255,0.04)"),
                      yaxis=dict(gridcolor="rgba(255,255,255,0.04)"))
    st.plotly_chart(fig, use_container_width=True)


# Treemap

st.caption("💰 Market Cap — Top 20")
top_cap = latest_df.sort_values("market_cap", ascending=False).head(20)
fig = px.treemap(top_cap, path=["name"], values="market_cap",
                 color="price_change_percentage_24h",
                 color_continuous_scale=["#f87171", "#1e293b", "#34d399"],
                 color_continuous_midpoint=0, template=T,
                 hover_data={"market_cap": ":,.0f"})
fig.update_layout(**CHART_LAYOUT, height=370)
fig.update_traces(textfont_size=13)
st.plotly_chart(fig, use_container_width=True)


# Scatter

st.caption("📈 Price vs Market Cap (bubble = volume)")
fig = px.scatter(latest_df, x="current_price", y="market_cap",
                 hover_name="name",
                 color="price_change_percentage_24h",
                 size="total_volume", size_max=40,
                 color_continuous_scale=["#f87171", "#475569", "#34d399"],
                 color_continuous_midpoint=0, template=T,
                 labels={"current_price": "Price (USD)", "market_cap": "Market Cap (USD)"})
fig.update_layout(**CHART_LAYOUT, height=380)
st.plotly_chart(fig, use_container_width=True)


# Correlation Heatmap

col_heat, col_hist = st.columns([3, 2])

with col_heat:
    st.caption("🔥 Correlation Matrix")
    numeric_df = latest_df.select_dtypes(include="number")
    corr = numeric_df.corr()
    fig = px.imshow(corr, text_auto=".2f", aspect="auto",
                    color_continuous_scale="RdBu_r", template=T)
    fig.update_layout(**CHART_LAYOUT, height=370)
    st.plotly_chart(fig, use_container_width=True)

with col_hist:
    st.caption("📊 24h Return Distribution")
    fig = px.histogram(latest_df, x="price_change_percentage_24h",
                       nbins=25, color_discrete_sequence=[PURPLE], template=T,
                       labels={"price_change_percentage_24h": "24h Change (%)"})
    fig.add_vline(x=0, line_dash="dash", line_color="#94a3b8", line_width=1)
    fig.update_layout(**CHART_LAYOUT, height=370)
    st.plotly_chart(fig, use_container_width=True)


# Memory comparison

mem_data = memory.get("memory", {})
if memory.get("status") == "success" and mem_data.get("comparison"):
    render_html('<div class="section-header">Memory Agent — vs Previous Run</div>')
    mc1, mc2, mc3 = st.columns(3)
    cap_chg = mem_data.get("market_cap_change_percent", 0)
    vol_chg = mem_data.get("volume_change_percent", 0)
    avg_chg_d = mem_data.get("average_change_difference", 0)
    mc1.metric("Market Cap Change", f"{cap_chg}%", f"{cap_chg:+.2f}%")
    mc2.metric("Volume Change",     f"{vol_chg}%", f"{vol_chg:+.2f}%")
    mc3.metric("Avg Return Δ",      f"{avg_chg_d}%", f"{avg_chg_d:+.2f}%")


# Dataset table

render_html('<div class="section-header">Latest Dataset</div>')
st.dataframe(latest_df, use_container_width=True, hide_index=True)