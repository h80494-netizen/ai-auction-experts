import asyncio
from playwright.async_api import async_playwright
async def t():
  async with async_playwright() as p:
    b=await p.chromium.launch(headless=True)
    page=await b.new_page()
    await page.goto('http://www.my-auction.co.kr/main/main.php')
    await page.evaluate('document.frm_top2.sno.value=2025; document.frm_top2.tno.value=102531; document.frm_top2.submit();')
    await page.wait_for_url('**/search_list.php*')
    print(await page.locator('table.tbl_auction_list tbody tr, table.tbl_auction_list tr').count())
    await b.close()
asyncio.run(t())