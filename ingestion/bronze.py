import json

from pathlib import Path
from datetime import datetime


BASE_DIR = Path(__file__).resolve().parent.parent

BRONZE_DIR = BASE_DIR / "data" / "bronze"

BRONZE_DIR.mkdir(parents=True, exist_ok=True)


def save_bronze(raw_data):

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    bronze_file = BRONZE_DIR / f"{timestamp}.json"

    with open(bronze_file, "w", encoding="utf-8") as file:
        json.dump(raw_data, file, indent=4)

    print(f"Bronze file saved : {bronze_file.name}")

    return bronze_file