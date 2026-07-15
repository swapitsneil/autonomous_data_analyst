import sqlite3

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_DIR = BASE_DIR / "database"

DATABASE_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATABASE_DIR / "warehouse.db"


def load_to_sqlite(df):

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    # Create crypto_market table automatically
    df.to_sql(
        "crypto_market",
        conn,
        if_exists="append",
        index=False
    )

    # Create market_history table
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

    print(f"Inserted {len(df)} rows into crypto_market")