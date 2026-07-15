import json
from datetime import datetime
from pathlib import Path
from jinja2 import Template

BASE_DIR = Path(__file__).resolve().parent.parent
REPORTS_DIR = BASE_DIR / "reports"

REPORT_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ADA Executive Report — {{ date }}</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    font-family: 'Segoe UI', Arial, sans-serif;
    background: #ffffff;
    color: #1a202c;
    font-size: 11pt;
    line-height: 1.6;
  }

  /* Cover Page */
  .cover {
    page-break-after: always;
    height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: flex-start;
    padding: 4rem 5rem;
    background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    color: white;
  }

  .cover-logo {
    font-size: 3rem;
    font-weight: 900;
    background: linear-gradient(90deg, #a78bfa, #60a5fa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.04em;
    margin-bottom: 0.5rem;
  }

  .cover-sub {
    font-size: 0.9rem;
    color: rgba(255,255,255,0.4);
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 3rem;
  }

  .cover-title {
    font-size: 2.5rem;
    font-weight: 700;
    color: white;
    line-height: 1.2;
    margin-bottom: 1rem;
    max-width: 600px;
  }

  .cover-date {
    font-size: 1rem;
    color: rgba(255,255,255,0.5);
    margin-top: 1rem;
  }

  .cover-divider {
    width: 60px;
    height: 4px;
    background: linear-gradient(90deg, #a78bfa, #60a5fa);
    border-radius: 2px;
    margin: 2rem 0;
  }

  .cover-tag {
    display: inline-block;
    padding: 0.3rem 0.8rem;
    border-radius: 100px;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    border: 1px solid rgba(167,139,250,0.4);
    color: #a78bfa;
    margin-right: 0.5rem;
    margin-bottom: 0.5rem;
  }

  /* Content pages */
  .page {
    page-break-after: always;
    padding: 3.5rem 4rem;
    min-height: 100vh;
  }

  .page:last-child {
    page-break-after: auto;
  }

  /* Page header */
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2.5rem;
    padding-bottom: 1rem;
    border-bottom: 2px solid #f0f4f8;
  }

  .page-header-brand {
    font-size: 0.75rem;
    font-weight: 800;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #a78bfa;
  }

  .page-header-date {
    font-size: 0.75rem;
    color: #94a3b8;
  }

  /* Section titles */
  h1 {
    font-size: 1.8rem;
    font-weight: 800;
    color: #1a202c;
    margin-bottom: 0.25rem;
  }

  h2 {
    font-size: 1.1rem;
    font-weight: 700;
    color: #2d3748;
    margin: 2rem 0 0.8rem 0;
    padding-bottom: 0.4rem;
    border-bottom: 2px solid #e2e8f0;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-size: 0.82rem;
  }

  h3 {
    font-size: 1rem;
    font-weight: 600;
    color: #4a5568;
    margin: 1.2rem 0 0.5rem 0;
  }

  p {
    color: #4a5568;
    margin-bottom: 0.6rem;
    line-height: 1.7;
  }

  /* KPI Grid */
  .kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin: 1.5rem 0;
  }

  .kpi-box {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    border-top: 3px solid #a78bfa;
  }

  .kpi-label {
    font-size: 0.65rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #94a3b8;
    margin-bottom: 0.3rem;
  }

  .kpi-value {
    font-size: 1.4rem;
    font-weight: 800;
    color: #1a202c;
  }

  .kpi-sub {
    font-size: 0.72rem;
    color: #94a3b8;
    margin-top: 0.2rem;
  }

  /* Summary box */
  .summary-box {
    background: linear-gradient(135deg, #f5f3ff, #eff6ff);
    border: 1px solid #ddd6fe;
    border-left: 4px solid #a78bfa;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin: 1rem 0;
    color: #4a5568;
    line-height: 1.75;
  }

  /* Findings */
  .finding {
    background: #f0fdf4;
    border-left: 3px solid #34d399;
    border-radius: 0 8px 8px 0;
    padding: 0.6rem 1rem;
    margin-bottom: 0.5rem;
    font-size: 0.88rem;
    color: #1a202c;
  }

  .recommendation {
    background: #eff6ff;
    border-left: 3px solid #60a5fa;
    border-radius: 0 8px 8px 0;
    padding: 0.6rem 1rem;
    margin-bottom: 0.5rem;
    font-size: 0.88rem;
    color: #1a202c;
  }

  .insight {
    background: #faf5ff;
    border-left: 3px solid #a78bfa;
    border-radius: 0 8px 8px 0;
    padding: 0.6rem 1rem;
    margin-bottom: 0.5rem;
    font-size: 0.88rem;
    color: #1a202c;
  }

  /* Hypothesis table */
  .hyp-card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.7rem;
  }

  .hyp-id {
    display: inline-block;
    background: #ede9fe;
    color: #7c3aed;
    padding: 0.15rem 0.6rem;
    border-radius: 100px;
    font-size: 0.68rem;
    font-weight: 700;
    margin-right: 0.5rem;
    letter-spacing: 0.05em;
  }

  .hyp-test {
    display: inline-block;
    background: #e0f2fe;
    color: #0369a1;
    padding: 0.15rem 0.6rem;
    border-radius: 100px;
    font-size: 0.68rem;
    font-weight: 700;
    margin-right: 0.5rem;
  }

  .hyp-approved {
    display: inline-block;
    background: #dcfce7;
    color: #15803d;
    padding: 0.15rem 0.6rem;
    border-radius: 100px;
    font-size: 0.68rem;
    font-weight: 700;
  }

  .hyp-rejected {
    display: inline-block;
    background: #fee2e2;
    color: #dc2626;
    padding: 0.15rem 0.6rem;
    border-radius: 100px;
    font-size: 0.68rem;
    font-weight: 700;
  }

  .hyp-statement {
    font-size: 0.88rem;
    color: #374151;
    margin-top: 0.4rem;
  }

  .stat-chips {
    margin-top: 0.5rem;
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
  }

  .stat-chip {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 0.2rem 0.6rem;
    font-size: 0.72rem;
    color: #4a5568;
  }

  /* Footer */
  .footer {
    text-align: center;
    padding: 2rem;
    color: #94a3b8;
    font-size: 0.75rem;
    border-top: 1px solid #e2e8f0;
    margin-top: 2rem;
  }

  .conclusion-box {
    background: linear-gradient(135deg, #0f0c29, #302b63);
    color: white;
    border-radius: 16px;
    padding: 2rem;
    margin-top: 1.5rem;
    line-height: 1.75;
  }

  @media print {
    body { print-color-adjust: exact; -webkit-print-color-adjust: exact; }
    .page { page-break-after: always; }
    .cover { page-break-after: always; }
  }
</style>
</head>
<body>

<!-- Cover Page -->
<div class="cover">
  <div class="cover-logo">ADA</div>
  <div class="cover-sub">Autonomous Data Analyst</div>
  <div class="cover-divider"></div>
  <div class="cover-title">Executive Intelligence Report<br>Cryptocurrency Market Analysis</div>
  <div class="cover-date">Generated: {{ date }}</div>
  <div style="margin-top:2rem;">
    <span class="cover-tag">Gemini 2.5 Flash</span>
    <span class="cover-tag">LangGraph</span>
    <span class="cover-tag">{{ sentiment }}</span>
  </div>
</div>

<!-- Page 1: Executive Summary + KPIs -->
<div class="page">
  <div class="page-header">
    <div class="page-header-brand">ADA — Autonomous Data Analyst</div>
    <div class="page-header-date">{{ date }}</div>
  </div>

  <h1>Executive Summary</h1>
  <p style="color:#94a3b8; margin-bottom:1.5rem;">AI-Generated Market Intelligence Report</p>

  <div class="summary-box">{{ executive_summary }}</div>

  <h2>Market KPIs</h2>
  <div class="kpi-grid">
    <div class="kpi-box">
      <div class="kpi-label">Total Market Cap</div>
      <div class="kpi-value">{{ market_cap }}</div>
      <div class="kpi-sub">Across 100 assets</div>
    </div>
    <div class="kpi-box">
      <div class="kpi-label">24h Volume</div>
      <div class="kpi-value">{{ volume }}</div>
      <div class="kpi-sub">Trading activity</div>
    </div>
    <div class="kpi-box">
      <div class="kpi-label">Market Sentiment</div>
      <div class="kpi-value">{{ sentiment }}</div>
      <div class="kpi-sub">{{ positive_coins }} positive coins</div>
    </div>
    <div class="kpi-box">
      <div class="kpi-label">Avg 24h Change</div>
      <div class="kpi-value">{{ avg_change }}%</div>
      <div class="kpi-sub">Across all assets</div>
    </div>
  </div>

  <h2>Key Findings</h2>
  {% for finding in key_findings %}
  <div class="finding">{{ loop.index }}. {{ finding }}</div>
  {% endfor %}
</div>

<!-- Page 2: Hypotheses & Statistical Analysis -->
<div class="page">
  <div class="page-header">
    <div class="page-header-brand">ADA — Autonomous Data Analyst</div>
    <div class="page-header-date">{{ date }}</div>
  </div>

  <h1>Statistical Analysis</h1>
  <p style="color:#94a3b8; margin-bottom:1.5rem;">AI-generated hypotheses tested against live market data</p>

  <h2>Hypotheses & Results</h2>
  {% for hyp in hypotheses %}
  <div class="hyp-card">
    <div>
      <span class="hyp-id">{{ hyp.id }}</span>
      <span class="hyp-test">{{ hyp.test }}</span>
      {% if hyp.approved %}<span class="hyp-approved">✓ Approved</span>{% else %}<span class="hyp-rejected">✗ Rejected</span>{% endif %}
    </div>
    <div class="hyp-statement">{{ hyp.statement }}</div>
    {% if hyp.stats %}
    <div class="stat-chips">
      {% for stat in hyp.stats %}
      <span class="stat-chip">{{ stat }}</span>
      {% endfor %}
    </div>
    {% endif %}
  </div>
  {% endfor %}
</div>

<!-- Page 3: Recommendations + Memory -->
<div class="page">
  <div class="page-header">
    <div class="page-header-brand">ADA — Autonomous Data Analyst</div>
    <div class="page-header-date">{{ date }}</div>
  </div>

  <h1>Recommendations</h1>
  <p style="color:#94a3b8; margin-bottom:1.5rem;">AI-derived strategic guidance from statistical evidence</p>

  {% for rec in recommendations %}
  <div class="recommendation">{{ loop.index }}. {{ rec }}</div>
  {% endfor %}

  <h2>Historical Memory Intelligence</h2>
  {% for insight in historical_insights %}
  <div class="insight">🔍 {{ insight }}</div>
  {% endfor %}
  {% if not historical_insights %}
  <p>First pipeline run — historical intelligence will activate from the next run.</p>
  {% endif %}

  <h2>Conclusion</h2>
  <div class="conclusion-box">{{ conclusion }}</div>

  <div class="footer">
    Generated by ADA — Autonomous Data Analyst &nbsp;•&nbsp;
    Powered by Gemini 2.5 Flash + LangGraph &nbsp;•&nbsp; {{ date }}
  </div>
</div>

</body>
</html>
"""


def load_report(name):
    path = REPORTS_DIR / f"{name}.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def generate_html_report():
    narrator = load_report("narrator")
    hypotheses_data = load_report("hypotheses")
    analysis_data = load_report("analysis")
    critic_data = load_report("critic")
    memory_data = load_report("memory")

    # Build approved map
    approved_ids = {}
    for review in critic_data.get("reviews", []):
        approved_ids[review["id"]] = review.get("approved", False)

    # Build analysis map
    analysis_map = {}
    for a in analysis_data.get("analysis", []):
        analysis_map[a["id"]] = a

    # Build hypotheses list for template
    hyp_list = []
    for h in hypotheses_data.get("hypotheses", []):
        hid = h["id"]
        approved = approved_ids.get(hid, False)
        a = analysis_map.get(hid, {})

        stats = []
        if a.get("correlation") is not None:
            stats.append(f"r = {a['correlation']}")
        if a.get("r2_score") is not None:
            stats.append(f"R² = {a['r2_score']}")
        if a.get("p_value") is not None:
            stats.append(f"p = {a['p_value']}")
        if a.get("effect_strength"):
            stats.append(f"Effect: {a['effect_strength']}")
        if a.get("significant") is not None:
            stats.append("Significant" if a["significant"] else "Not Significant")

        test = h.get("recommended_test", "").replace("_", " ").title()

        hyp_list.append({
            "id": hid,
            "test": test,
            "approved": approved,
            "statement": h.get("statement", ""),
            "stats": stats
        })

    # Snapshot
    snapshot = memory_data.get("current_snapshot", {})
    mem = memory_data.get("memory", {})
    historical_insights = mem.get("historical_insights", [])

    market_cap = snapshot.get("total_market_cap", 0)
    volume = snapshot.get("total_volume", 0)
    avg_change = round(snapshot.get("average_change", 0), 2)
    positive_coins = snapshot.get("positive_coins", 0)
    sentiment = snapshot.get("sentiment", "—")

    date_str = datetime.now().strftime("%d %B %Y — %H:%M")

    template = Template(REPORT_TEMPLATE)
    html = template.render(
        date=date_str,
        executive_summary=narrator.get("executive_summary", "No summary available."),
        key_findings=narrator.get("key_findings", []),
        recommendations=narrator.get("recommendations", []),
        conclusion=narrator.get("conclusion", ""),
        hypotheses=hyp_list,
        market_cap=f"${market_cap / 1e12:.2f}T",
        volume=f"${volume / 1e9:.2f}B",
        avg_change=avg_change,
        positive_coins=positive_coins,
        sentiment=sentiment,
        historical_insights=historical_insights
    )

    return html.encode("utf-8")
