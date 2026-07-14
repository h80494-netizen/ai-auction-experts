import os
import google.generativeai as genai
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), "..", "backend", ".env")
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY")
print(f"Loaded API Key: {api_key[:10]}... (len: {len(api_key) if api_key else 0})")

if not api_key:
    print("API Key not found!")
    exit(1)

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    print("Sending test prompt to Gemini...")
    response = model.generate_content("Hello, this is a test. Answer in 5 words.")
    print("Gemini response:")
    print(response.text)
except Exception as e:
    print("Gemini API call failed:", e)
