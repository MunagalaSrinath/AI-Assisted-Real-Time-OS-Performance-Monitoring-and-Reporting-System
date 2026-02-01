import os
from google import genai
from dotenv import load_dotenv
import json

# ✅ Load .env file
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found. Check your .env file.")

client = genai.Client(api_key=API_KEY)

def explain_system_change(system_data):
    prompt = f"""
You are an operating system performance analysis assistant.

Explain the following system behavior in clear, simple language.
Structure your response as:
1. What changed
2. Why it changed
3. Impact on the system
4. General recommendations

System data (JSON):
{json.dumps(system_data, indent=2)}
"""

    response = client.models.generate_content(
        model="models/gemini-2.5-flash",
        contents=prompt
    )

    return response.text
