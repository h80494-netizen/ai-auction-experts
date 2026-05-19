import asyncio
from backend.crawler.myauction_scraper import search_myauction_list

async def main():
    res = await search_myauction_list("2025-0800-059271")
    print(res)

if __name__ == "__main__":
    asyncio.run(main())
