import asyncio
from playwright.async_api import async_playwright
async def t():
  async with async_playwright() as p:
    b=await p.chromium.launch(headless=True)
    page=await b.new_page()
    await page.goto('http://www.my-auction.co.kr/member/login.php')
    await page.fill('#id', 'vibecoding')
    await page.fill('#passwd', '13579@Vv')
    await page.click('#btn_login')
    await page.wait_for_url('**/main.php')
    page.on('dialog', lambda d: print('ALERT:', d.message))
    await page.goto('http://www.my-auction.co.kr/auction/search_list.php?sno=2024&tno=5020')
    await page.wait_for_load_state('domcontentloaded')
    print(await page.locator('table.tbl_auction_list tbody tr').count())
    await b.close()
asyncio.run(t())