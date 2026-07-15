import json
import time
from utils.llm_fallback import generate_llm_content


def review_analysis(hypotheses, analysis):

    if analysis.get("status") != "success":

        return {
            "agent": "Critic Agent",
            "status": "skipped",
            "reason": "Analysis Agent failed.",
            "reviews": []
        }

    prompt = f"""
You are a Principal Data Science Reviewer.

You are reviewing the output of an autonomous Data Analyst.

Do NOT perform any new statistical analysis.

Only review the completed statistical analysis.

Review every hypothesis independently.

Evaluation Criteria:

1. Was the chosen statistical test appropriate?
2. Were the correct dataset columns analyzed?
3. Is the statistical evidence sufficient?
4. Is the interpretation statistically correct?
5. Is the business conclusion justified?
6. Should this hypothesis be approved?
7. Assign a confidence level:
   - High
   - Medium
   - Low

Return ONLY valid JSON.

Return EXACTLY this format:

{{
    "agent":"Critic Agent",
    "status":"success",
    "reviews":[
        {{
            "id":"H001",
            "approved":true,
            "confidence":"High",
            "feedback":""
        }}
    ]
}}

Hypotheses:

{json.dumps(hypotheses, indent=2)}

Analysis:

{json.dumps(analysis, indent=2)}
"""

    try:
        result = generate_llm_content(prompt, "Critic Agent")
        return result
    except Exception as e:
        print(f"[ERROR] Critic Agent failed: {e}")
        return {
            "agent": "Critic Agent",
            "status": "failed",
            "error": str(e),
            "reviews": []
        }


if __name__ == "__main__":
    print("Critic Agent Ready")