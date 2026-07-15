import json
import time
from utils.llm_fallback import generate_llm_content


def generate_hypotheses(profile):

    profile_summary = {
        "dataset_info": profile["dataset_info"],
        "numeric_columns": profile["numeric_columns"],
        "categorical_columns": profile["categorical_columns"],
        "summary_statistics": profile["summary_statistics"],
        "correlation_matrix": profile["correlation_matrix"]
    }

    prompt = f"""
You are an expert Senior Data Analyst.

You are given a statistical profile of a dataset.

Generate EXACTLY 5 statistically testable business hypotheses.

Rules:

1. Return ONLY valid JSON.
2. No markdown.
3. Do NOT explain your reasoning.
4. Use ONLY columns present in the dataset.
5. Hypotheses must be meaningful and business-oriented.
6. Choose ONLY ONE statistical test for each hypothesis.

Allowed statistical tests:

- pearson_correlation
- spearman_correlation
- linear_regression
- t_test
- anova
- chi_square

For Pearson / Spearman:

"columns": [
    "column1",
    "column2"
]

For Linear Regression:

"dependent": "column_name",

"independent": [
    "column_name"
]

For T-Test / ANOVA:

"group_column": "column_name",

"target_column": "column_name"

Return EXACTLY this JSON format:

{{
    "agent":"Hypothesis Agent",
    "status":"success",
    "hypotheses":[
        {{
            "id":"H001",
            "statement":"",
            "recommended_test":"",
            "columns":[],
            "dependent":"",
            "independent":[],
            "group_column":"",
            "target_column":"",
            "priority":"High"
        }}
    ]
}}

Dataset Profile:

{json.dumps(profile_summary, indent=2)}
"""

    try:
        result = generate_llm_content(prompt, "Hypothesis Agent")
        return result
    except Exception as e:
        print(f"[ERROR] Hypothesis Agent failed: {e}")
        return {
            "agent": "Hypothesis Agent",
            "status": "failed",
            "error": str(e),
            "hypotheses": []
        }


if __name__ == "__main__":
    print("Hypothesis Agent Ready")