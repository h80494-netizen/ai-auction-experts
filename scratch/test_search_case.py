import asyncio
import sys
import os

sys.path.append(os.path.abspath('backend'))

async def main():
    try:
        from crawler.myauction_scraper import search_myauction_list
        print("Searching for 2024타경6060...")
        res = await search_myauction_list('2024타경6060')
        print("Result:", res)
    except Exception as e:
        print("Error:", e)

if __name__ == '__main__':
    asyncio.run(main())
