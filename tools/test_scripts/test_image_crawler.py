import asyncio
from backend.crawler.myauction_scraper import scrape_myauction_case

async def main():
    res = await scrape_myauction_case("2024타경62469")
    print(res)

if __name__ == "__main__":
    asyncio.run(main())
