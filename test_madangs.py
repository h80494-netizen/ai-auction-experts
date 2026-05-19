import asyncio
from backend.crawler.madangs_scraper import scrape_madangs_images

async def main():
    case_number = "20245020"
    url = "https://madangs.com/popup/detail_report?link=photo&code=0320240058264001&type=1&photo_idx=2"
    await scrape_madangs_images(case_number, url)

if __name__ == "__main__":
    asyncio.run(main())
