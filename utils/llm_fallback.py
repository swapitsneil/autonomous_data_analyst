import requests
import json
import re
import time
from google import genai
from config.settings import GEMINI_API_KEY, OPENROUTER_API_KEY

QUOTA_SIGNALS = ["429", "quota", "resource_exhausted", "limit_exceeded", "rate_limit", "exceeded"]


def is_quota_error(e):
    msg = str(e).lower()
    return any(signal in msg for signal in QUOTA_SIGNALS)


def parse_json_response(text):
    text = text.strip()

    # Strip markdown block wrappers if present
    if text.startswith("```"):
        match = re.search(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)
        if match:
            text = match.group(1).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Fallback regex search for first outer JSON object
        match = re.search(r"(\{.*\})", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1).strip())
            except json.JSONDecodeError:
                pass
        raise


def generate_llm_content(prompt, agent_name):
    """
    Tries to generate content using Gemini 2.5 Flash.
    If quota is exceeded or Gemini key is missing, falls back to OpenRouter
    using nvidia/nemotron-3-ultra-550b-a55b:free.
    """
    # 1. Try Gemini first if key exists
    if GEMINI_API_KEY:
        try:
            client = genai.Client(api_key=GEMINI_API_KEY)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config={
                    "response_mime_type": "application/json"
                }
            )
            return parse_json_response(response.text)
        except Exception as e:
            if is_quota_error(e):
                print(f"\n[WARNING] Gemini Quota Exceeded in {agent_name}. Falling back to OpenRouter...")
            else:
                print(f"\n[WARNING] Gemini error in {agent_name}: {e}. Falling back to OpenRouter...")
    else:
        print(f"\n[WARNING] Gemini API key is missing. Falling back to OpenRouter...")

    # 2. Try OpenRouter Fallback if key exists
    if not OPENROUTER_API_KEY:
        raise Exception("Both Gemini and OpenRouter keys are missing or exhausted.")

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "nvidia/nemotron-3-ultra-550b-a55b:free",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    retries = 3
    for attempt in range(retries):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"]
                return parse_json_response(content)
            else:
                print(f"[WARNING] OpenRouter attempt {attempt + 1} failed: {response.status_code} - {response.text}")
        except Exception as oe:
            print(f"[WARNING] OpenRouter attempt {attempt + 1} error: {oe}")

        if attempt < retries - 1:
            time.sleep(3)

    raise Exception("Failed to obtain a valid response from both Gemini and OpenRouter.")
