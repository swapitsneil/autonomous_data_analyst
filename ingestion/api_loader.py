import os
import json
import requests

from dotenv import load_dotenv

from ingestion.bronze import save_bronze
from ingestion.silver import create_silver
from warehouse.sqlite_store import load_to_sqlite

from orchestrator.workflow import graph

from utils.report_manager import save_report


# Load Environment Variables

load_dotenv()

API_KEY = os.getenv("COINGECKO_API")


# Fetch Crypto Data

def fetch_crypto_data():

    url = "https://api.coingecko.com/api/v3/coins/markets"

    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 100,
        "page": 1,
        "sparkline": False
    }

    headers = {
        "x-cg-demo-api-key": API_KEY
    }

    try:

        print("Fetching data from CoinGecko...")

        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        print(f"Successfully fetched {len(data)} records.")

        return data

    except requests.exceptions.RequestException as e:

        print(f"API Error: {e}")

        return None


if __name__ == "__main__":

    # Fetch Data

    crypto_data = fetch_crypto_data()

    if not crypto_data:
        exit()

    # Bronze Layer

    save_bronze(crypto_data)

    # Silver Layer

    silver_df = create_silver(crypto_data)

    # SQLite Warehouse

    load_to_sqlite(silver_df)

    print("\nETL Pipeline Completed Successfully.")

    # LangGraph Workflow

    state = {
        "df": silver_df,
        "profile": {},
        "hypotheses": {},
        "analysis": {},
        "critic": {},
        "report": {},
        "memory": {},
        "retry_count": 0
    }

    result = graph.invoke(state)

    print("\n========== PIPELINE COMPLETED ==========\n")

    print("Returned Keys:")
    print(result.keys())

    # Save Reports

    reports = {
        "profile": "profile",
        "hypotheses": "hypotheses",
        "analysis": "analysis",
        "critic": "critic",
        "report": "narrator",
        "memory": "memory"
    }

    for state_key, report_name in reports.items():

        if state_key in result:

            save_report(report_name, result[state_key])

            print(f"[OK] Saved {report_name}.json")

        else:

            print(f"[WARNING] {state_key} not found. Skipping...")

    # Display Results

    print("\n========== PROFILER AGENT ==========\n")
    print(json.dumps(result.get("profile", {}), indent=4, default=str))

    print("\n========== HYPOTHESIS AGENT ==========\n")
    print(json.dumps(result.get("hypotheses", {}), indent=4))

    print("\n========== ANALYST AGENT ==========\n")
    print(json.dumps(result.get("analysis", {}), indent=4))

    print("\n========== CRITIC AGENT ==========\n")
    print(json.dumps(result.get("critic", {}), indent=4))

    print("\n========== NARRATOR AGENT ==========\n")
    print(json.dumps(result.get("report", {}), indent=4))

    print("\n========== MEMORY AGENT ==========\n")
    print(json.dumps(result.get("memory", {}), indent=4))

    print("\nReports saved successfully.")

    print("\nWorkflow executed successfully.")