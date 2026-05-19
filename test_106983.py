import asyncio
import json
from backend.crawler.myauction_scraper import search_myauction_list, scrape_myauction_case

async def run():
    print("Searching for 2024타경106983...")
    res = await search_myauction_list("2024타경106983")
    print(res)
    
    # Check if there is a match and get the URL
    # Wait, search_myauction_list returns {"status": "success", "data": [...]}
    if res.get("status") == "success" and res["data"]:
        # We need the link! Wait, search_myauction_list does NOT return the link in the "data" array!
        # It only returns address, status, raw_text, appraised, minimum, approval_date.
        # But wait, how does the frontend get the photo_url or link?
        pass

if __name__ == "__main__":
    asyncio.run(run())
