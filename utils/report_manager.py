import os
import json

REPORT_DIR = "reports"

os.makedirs(REPORT_DIR, exist_ok=True)


def save_report(filename, data):

    path = os.path.join(REPORT_DIR, f"{filename}.json")

    with open(path, "w", encoding="utf-8") as file:

        json.dump(
            data,
            file,
            indent=4,
            default=str
        )


def load_report(filename):

    path = os.path.join(REPORT_DIR, f"{filename}.json")

    with open(path, "r", encoding="utf-8") as file:

        return json.load(file)