import sys
import os
import asyncio
sys.path.append(os.path.abspath("backend"))

from crawler.myauction_scraper import scrape_myauction_case

async def run():
    print("Running scrape_myauction_case for 2025타경100759...")
    try:
        result = await scrape_myauction_case("2025타경100759")
        print("\nResult:")
        print("Success:", result.get("success"))
        if "error" in result:
            print("Error message:", result.get("error"))
        if "data" in result:
            print("Data fields:", list(result.get("data").keys()))
            print("Address:", result.get("data", {}).get("address"))
            print("risks:", result.get("data", {}).get("risks"))
    except Exception as e:
        import traceback
        print("Exception in test_scrape_100759:")
        traceback.print_exc()

asyncio.run(run())
