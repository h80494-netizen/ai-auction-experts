import asyncio
import os
from dotenv import load_dotenv

# Load .env from backend directory
load_dotenv(os.path.join("backend", ".env"))

from backend.crawler.myauction_scraper import scrape_myauction_case

async def run():
    print("Testing 2024타경106983...")
    res = await scrape_myauction_case("2024타경106983", "은평구 대조동")
    print("\n[RESULT]")
    print(res)

if __name__ == "__main__":
    asyncio.run(run())
