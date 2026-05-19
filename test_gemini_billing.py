import asyncio
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv(os.path.join("backend", ".env"))

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("No API key found in backend/.env")
    exit(1)

genai.configure(api_key=api_key)

async def make_request(i):
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = await model.generate_content_async(f"Say hello {i}")
        print(f"Req {i}: SUCCESS")
        return True
    except Exception as e:
        print(f"Req {i}: FAILED - {e}")
        return False

async def test_rate_limit():
    print(f"Testing API key (ending in {api_key[-4:]}) with 20 concurrent requests...")
    tasks = [make_request(i) for i in range(20)]
    results = await asyncio.gather(*tasks)
    success_count = sum(results)
    fail_count = len(results) - success_count
    print(f"\nTotal Success: {success_count}, Total Failed: {fail_count}")
    if fail_count > 0:
        print("\n[CONCLUSION] You are STILL on the FREE tier (or hitting a strict rate limit).")
    else:
        print("\n[CONCLUSION] You are on the PAID tier! No 429 errors encountered for 20 requests.")

if __name__ == "__main__":
    asyncio.run(test_rate_limit())
