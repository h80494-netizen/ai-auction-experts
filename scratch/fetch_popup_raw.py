import asyncio
import os
import requests
from dotenv import load_dotenv
from playwright.async_api import async_playwright

env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backend', '.env')
load_dotenv(dotenv_path=env_path)

MYAUCTION_ID = os.getenv("MYAUCTION_ID")
MYAUCTION_PW = os.getenv("MYAUCTION_PW")

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        print("Logging in...")
        await page.goto("https://www.my-auction.co.kr/member/login.php")
        await page.fill("#id", MYAUCTION_ID)
        await page.fill("#passwd", MYAUCTION_PW)
        await page.click("#btn_login")
        await page.wait_for_url("**/main.php", timeout=5000)
        
        # Get cookies
        cookies = await context.cookies()
        await browser.close()
        
    # Use requests to fetch
    session = requests.Session()
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'], path=cookie['path'])
        
    idx = "1479806"
    doc_url = f"https://www.my-auction.co.kr/view/pop_detail.php?type=mul&idx={idx}"
    print(f"Fetching via requests: {doc_url}")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': f"https://www.my-auction.co.kr/view/{idx}"
    }
    
    resp = session.get(doc_url, headers=headers)
    print("Response raw bytes:", resp.content)
    try:
        decoded_cp949 = resp.content.decode('cp949')
        print("Decoded as CP949:")
        print(decoded_cp949)
    except Exception as e:
        print("CP949 decode failed:", e)
        
    try:
        decoded_utf8 = resp.content.decode('utf-8')
        print("Decoded as UTF-8:")
        print(decoded_utf8)
    except Exception as e:
        print("UTF-8 decode failed:", e)

if __name__ == "__main__":
    asyncio.run(run())
