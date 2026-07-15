import json
import time
from utils.llm_fallback import generate_llm_content


def generate_report(hypotheses, analysis, critic):

    if not analysis.get("analysis"):

        return {
            "agent": "Narrator Agent",
            "status": "skipped",
            "reason": "No approved analysis available."
        }

    prompt = f"""
You are a Senior Business Intelligence Consultant.

You are preparing an executive report for business stakeholders.

You are provided with outputs from three AI agents:

1. Hypothesis Agent
2. Analyst Agent
3. Critic Agent

Instructions:

• Use ONLY approved hypotheses.
• Ignore rejected hypotheses.
• Do NOT invent new findings.
• Write in clear business language.
• Avoid unnecessary technical jargon.
• Provide practical business recommendations.
• Keep the report concise and professional.

Return ONLY valid JSON.

Return EXACTLY this format:

{{
    "agent":"Narrator Agent",
    "status":"success",
    "executive_summary":"",
    "key_findings":[
        "...",
        "..."
    ],
    "recommendations":[
        "...",
        "..."
    ],
    "conclusion":""
}}

Hypotheses

{json.dumps(hypotheses, indent=2)}

Analysis

{json.dumps(analysis, indent=2)}

Critic Review

{json.dumps(critic, indent=2)}
"""

    try:
        result = generate_llm_content(prompt, "Narrator Agent")
        return result
    except Exception as e:
        print(f"[ERROR] Narrator Agent failed: {e}")
        return {
            "agent": "Narrator Agent",
            "status": "failed",
            "error": str(e),
            "executive_summary": "",
            "key_findings": [],
            "recommendations": [],
            "conclusion": ""
        }


if __name__ == "__main__":
    print("Narrator Agent Ready")