import asyncio
import json
from crawler.myauction_scraper import scrape_myauction_case

async def run():
    res = await scrape_myauction_case('2022타경58150')
    with open('result.json', 'w', encoding='utf-8') as f:
        json.dump(res, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    asyncio.run(run())
