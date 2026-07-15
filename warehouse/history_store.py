import sqlite3

DB_PATH = "warehouse/crypto.db"


def create_history_table():

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS market_history (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        run_time TEXT,

        total_market_cap REAL,

        total_volume REAL,

        average_change REAL,

        positive_coins INTEGER,

        negative_coins INTEGER,

        sentiment TEXT,

        summary TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_market_snapshot(profile, report):

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    stats = profile["summary_statistics"]

    total_market_cap = stats["market_cap"]["mean"] * profile["dataset_info"]["rows"]

    total_volume = stats["total_volume"]["mean"] * profile["dataset_info"]["rows"]

    avg_change = stats["price_change_percentage_24h"]["mean"]

    positive = report.get("positive_coins", 0)

    negative = report.get("negative_coins", 0)

    sentiment = report.get("market_sentiment", "Unknown")

    summary = report.get("executive_summary", "")

    cursor.execute(
        """
        INSERT INTO market_history
        (
            run_time,
            total_market_cap,
            total_volume,
            average_change,
            positive_coins,
            negative_coins,
            sentiment,
            summary
        )
        VALUES (datetime('now'),?,?,?,?,?,?,?)
        """,
        (
            total_market_cap,
            total_volume,
            avg_change,
            positive,
            negative,
            sentiment,
            summary
        )
    )

    conn.commit()
    conn.close()

    