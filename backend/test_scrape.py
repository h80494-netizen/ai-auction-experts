import asyncio
from crawler.myauction_scraper import search_myauction_list, scrape_myauction_case
import os

async def run():
    # Use the new credentials provided by the user
    os.environ["MYAUCTION_ID"] = "h804949"
    os.environ["MYAUCTION_PW"] = "spring11!!"
    
    res = await search_myauction_list("2024타경5020")
    print("Search Result:", res)
    
    if res.get("success") and len(res.get("items", [])) > 0:
        # Just test the first item
        address = res["items"][0]["address"]
        details = await scrape_myauction_case("2024타경5020", address)
        print("Details:", details)
        
if __name__ == "__main__":
    asyncio.run(run())
