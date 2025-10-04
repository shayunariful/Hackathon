from dotenv import load_dotenv
import os, google.generativeai as genai, json

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

print("Loaded?", bool(os.getenv("GOOGLE_API_KEY")))

model = genai.GenerativeModel("gemini-2.5-flash")

prompt = (
    "Return **ONLY** valid JSON with this structure:\n"
    '{"ok": true, "message": "Gemini API test successful"}'
)

resp = model.generate_content(prompt)
print("Raw response:", resp.text)

try:
    data = json.loads(resp.text)
    print("✅ Parsed JSON:", data)
except json.JSONDecodeError:
    print("⚠️ Not JSON, but API responded correctly.")
