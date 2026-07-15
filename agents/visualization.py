import json

from google import genai

from config.settings import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)


def generate_visualizations(profile, analysis):

    payload = {
        "profile": profile,
        "analysis": analysis
    }

    prompt = f"""
You are a Senior Data Visualization Expert.

Based on the dataset profile and statistical analysis,
recommend the BEST visualizations.

Rules:

1. Return ONLY valid JSON.
2. No markdown.
3. Do NOT generate charts.
4. Only recommend charts.

Allowed chart types:

- scatter
- line
- bar
- histogram
- boxplot
- heatmap
- pie

Return EXACTLY this format:

{{
    "agent":"Visualization Agent",
    "status":"success",
    "visualizations":[
        {{
            "id":"V001",
            "title":"",
            "chart_type":"",
            "x_axis":"",
            "y_axis":"",
            "reason":""
        }}
    ]
}}

Input:

{json.dumps(payload, indent=2)}
"""

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={
                "response_mime_type": "application/json"
            }
        )

        return json.loads(response.text)

    except Exception as e:

        return {
            "agent": "Visualization Agent",
            "status": "failed",
            "error": str(e)
        }


if __name__ == "__main__":

    print("Visualization Agent Ready")