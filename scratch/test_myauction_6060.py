import asyncio
import os
import sys

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from crawler.myauction_scraper import search_myauction_list

async def main():
    print("Starting search for 2024타경6060...")
    result = await search_myauction_list("2024타경6060")
    print("Result:")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
