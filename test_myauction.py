import asyncio
import sys
sys.path.append('backend')
from crawler.myauction_scraper import search_myauction_list

async def main():
    res = await search_myauction_list('2023타경1234')
    print("RESULT:", res)

if __name__ == '__main__':
    asyncio.run(main())
