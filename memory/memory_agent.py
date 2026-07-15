import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "warehouse.db"

HISTORY_WINDOW = 10


# Pattern Analysis Engine

def _consecutive_sentiment_streak(history):
    if not history:
        return 0, ""
    latest_sentiment = history[-1]["sentiment"]
    streak = 0
    for row in reversed(history):
        if row["sentiment"] == latest_sentiment:
            streak += 1
        else:
            break
    return streak, latest_sentiment


def _detect_trend(values, label):
    if len(values) < 3:
        return None
    diffs = [values[i] - values[i - 1] for i in range(1, len(values))]
    if all(d > 0 for d in diffs):
        return f"{label} has increased for {len(values)} consecutive pipeline runs."
    if all(d < 0 for d in diffs):
        return f"{label} has decreased for {len(values)} consecutive pipeline runs."
    recent = diffs[-2:]
    if all(d > 0 for d in recent):
        return f"{label} has been rising over the last {len(recent) + 1} runs."
    if all(d < 0 for d in recent):
        return f"{label} has been declining over the last {len(recent) + 1} runs."
    return None


def _rolling_average(values, window):
    if len(values) < window:
        return None
    return sum(values[-window:]) / window


def _detect_spike_or_crash(current, rolling_avg, label, threshold=0.10):
    if rolling_avg is None or rolling_avg == 0:
        return None
    change = (current - rolling_avg) / abs(rolling_avg)
    if change > threshold:
        return f"{label} is {change * 100:.1f}% above the {label.lower()} 5-run rolling average — potential spike detected."
    if change < -threshold:
        return f"{label} is {abs(change) * 100:.1f}% below the {label.lower()} 5-run rolling average — potential crash detected."
    return None


def _detect_volume_sentiment_divergence(history):
    if len(history) < 3:
        return None
    recent = history[-3:]
    sentiments = [r["sentiment"] for r in recent]
    volumes = [r["total_volume"] for r in recent]
    vol_declining = all(volumes[i] > volumes[i + 1] for i in range(len(volumes) - 1))
    vol_rising = all(volumes[i] < volumes[i + 1] for i in range(len(volumes) - 1))
    if vol_declining and all(s == "Bullish" for s in sentiments):
        return "Bearish divergence detected: trading volume has declined over the last 3 runs despite persistent Bullish sentiment."
    if vol_rising and all(s == "Bearish" for s in sentiments):
        return "Bullish divergence detected: trading volume has risen over the last 3 runs despite persistent Bearish sentiment."
    return None


def _dominant_sentiment(history):
    if len(history) < 3:
        return None
    total = len(history)
    counts = {}
    for row in history:
        s = row["sentiment"]
        counts[s] = counts.get(s, 0) + 1
    for sentiment, count in counts.items():
        ratio = count / total
        if ratio >= 0.70:
            return f"{sentiment} sentiment has been dominant across {count} of {total} historical market snapshots ({ratio * 100:.0f}%)."
    return None


def _build_historical_insights(history, current):
    insights = []

    cap_values = [r["total_market_cap"] for r in history] + [current["total_market_cap"]]
    vol_values = [r["total_volume"] for r in history] + [current["total_volume"]]
    change_values = [r["average_change"] for r in history] + [current["average_change"]]
    all_history = history + [current]

    # Sentiment streak
    streak, sentiment = _consecutive_sentiment_streak(all_history)
    if streak >= 2:
        insights.append(
            f"{sentiment} sentiment has remained dominant for {streak} consecutive pipeline runs."
        )

    # Market cap trend
    cap_trend = _detect_trend(cap_values, "Market capitalization")
    if cap_trend:
        insights.append(cap_trend)

    # Volume trend
    vol_trend = _detect_trend(vol_values, "Trading volume")
    if vol_trend:
        insights.append(vol_trend)

    # Average change trend
    change_trend = _detect_trend(change_values, "Average 24h price change")
    if change_trend:
        insights.append(change_trend)

    # Rolling averages
    cap_avg_3 = _rolling_average(cap_values, 3)
    cap_avg_5 = _rolling_average(cap_values, 5)
    vol_avg_3 = _rolling_average(vol_values, 3)
    vol_avg_5 = _rolling_average(vol_values, 5)

    if cap_avg_3:
        insights.append(
            f"3-run rolling average market cap: ${cap_avg_3 / 1e12:.2f}T | "
            f"Current: ${current['total_market_cap'] / 1e12:.2f}T"
        )
    if vol_avg_3:
        insights.append(
            f"3-run rolling average trading volume: ${vol_avg_3 / 1e9:.2f}B | "
            f"Current: ${current['total_volume'] / 1e9:.2f}B"
        )

    # Spike / crash detection
    spike_cap = _detect_spike_or_crash(current["total_market_cap"], cap_avg_5, "Market capitalization")
    if spike_cap:
        insights.append(spike_cap)

    spike_vol = _detect_spike_or_crash(current["total_volume"], vol_avg_5, "Trading volume")
    if spike_vol:
        insights.append(spike_vol)

    # Volume / sentiment divergence
    divergence = _detect_volume_sentiment_divergence(all_history)
    if divergence:
        insights.append(divergence)

    # Dominant sentiment
    dominant = _dominant_sentiment(all_history)
    if dominant:
        insights.append(dominant)

    return insights


# Memory Agent

def memory_agent(df, profile, report):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Fetch historical records
    cursor.execute("""
        SELECT
            run_time,
            total_market_cap,
            total_volume,
            average_change,
            positive_coins,
            negative_coins,
            sentiment,
            summary
        FROM market_history
        ORDER BY id DESC
        LIMIT ?
    """, (HISTORY_WINDOW,))

    rows = cursor.fetchall()
    columns = [
        "run_time", "total_market_cap", "total_volume",
        "average_change", "positive_coins", "negative_coins",
        "sentiment", "summary"
    ]
    history = [dict(zip(columns, row)) for row in reversed(rows)]

    # Build current snapshot
    total_market_cap = float(df["market_cap"].sum())
    total_volume = float(df["total_volume"].sum())
    average_change = float(df["price_change_percentage_24h"].mean())
    positive_coins = int((df["price_change_percentage_24h"] > 0).sum())
    negative_coins = int((df["price_change_percentage_24h"] < 0).sum())

    if positive_coins > negative_coins:
        sentiment = "Bullish"
    elif negative_coins > positive_coins:
        sentiment = "Bearish"
    else:
        sentiment = "Neutral"

    summary = report.get("executive_summary", "") if isinstance(report, dict) else ""

    current = {
        "run_time": "now",
        "total_market_cap": total_market_cap,
        "total_volume": total_volume,
        "average_change": average_change,
        "positive_coins": positive_coins,
        "negative_coins": negative_coins,
        "sentiment": sentiment,
        "summary": summary
    }

    # Previous run comparison (backward compatible)
    previous = history[-1] if history else None

    if previous is None:
        comparison = None
        comparison_insights = ["First market snapshot stored. Historical intelligence will activate from the next run."]
    else:
        prev_cap = previous["total_market_cap"]
        prev_vol = previous["total_volume"]
        prev_change = previous["average_change"]

        cap_change = ((total_market_cap - prev_cap) / prev_cap * 100) if prev_cap else 0
        vol_change = ((total_volume - prev_vol) / prev_vol * 100) if prev_vol else 0
        avg_change_diff = average_change - prev_change

        comparison = {
            "previous_run": previous["run_time"],
            "market_cap_change_percent": round(cap_change, 2),
            "volume_change_percent": round(vol_change, 2),
            "average_change_difference": round(avg_change_diff, 2),
            "positive_coin_difference": positive_coins - previous["positive_coins"],
            "negative_coin_difference": negative_coins - previous["negative_coins"],
            "previous_sentiment": previous["sentiment"],
            "current_sentiment": sentiment,
            "previous_summary": previous["summary"]
        }

        comparison_insights = [
            f"Market capitalization changed by {round(cap_change, 2)}% vs previous run.",
            f"Trading volume changed by {round(vol_change, 2)}% vs previous run.",
            f"Average 24h return changed by {round(avg_change_diff, 2)}% vs previous run.",
            f"Positive coins changed by {positive_coins - previous['positive_coins']} vs previous run.",
            f"Negative coins changed by {negative_coins - previous['negative_coins']} vs previous run.",
            f"Market sentiment: {previous['sentiment']} -> {sentiment}."
        ]

    # Advanced historical intelligence
    historical_insights = _build_historical_insights(history, current)

    # Persist current snapshot
    cursor.execute("""
        INSERT INTO market_history
        (run_time, total_market_cap, total_volume, average_change,
         positive_coins, negative_coins, sentiment, summary)
        VALUES (datetime('now'), ?, ?, ?, ?, ?, ?, ?)
    """, (
        total_market_cap, total_volume, average_change,
        positive_coins, negative_coins, sentiment, summary
    ))

    conn.commit()
    conn.close()

    # Build memory output
    memory_output = {
        "agent": "Memory Agent",
        "status": "success",
        "runs_analyzed": len(history) + 1,
        "current_snapshot": current,
        "memory": {
            "comparison": comparison,
            "business_insights": comparison_insights,
            "historical_insights": historical_insights,
            "previous_run": previous["run_time"] if previous else None,
            "previous_sentiment": previous["sentiment"] if previous else None,
            "current_sentiment": sentiment,
            "previous_summary": previous["summary"] if previous else ""
        }
    }

    # Backward compatible keys at top level (used by Memory page)
    if comparison:
        memory_output["memory"].update(comparison)

    return memory_output


if __name__ == "__main__":
    print("Memory Agent Ready")