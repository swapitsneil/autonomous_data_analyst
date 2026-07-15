import pandas as pd
from datetime import datetime


def create_silver(raw_data):

    df = pd.DataFrame(raw_data)

    keep_cols = [
        "id",
        "symbol",
        "name",
        "current_price",
        "market_cap",
        "market_cap_rank",
        "total_volume",
        "price_change_percentage_24h",
        "circulating_supply",
        "last_updated"
    ]

    silver_df = df[keep_cols].copy()

    silver_df["price_change_percentage_24h"] = (
        silver_df["price_change_percentage_24h"]
        .fillna(0)
    )

    silver_df["last_updated"] = pd.to_datetime(
        silver_df["last_updated"]
    )

    silver_df["fetch_time"] = datetime.now()

    print(f"Silver dataset created : {len(silver_df)} records")

    print(silver_df.head())

    return silver_df
