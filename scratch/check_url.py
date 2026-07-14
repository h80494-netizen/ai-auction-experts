from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)
try:
    driver.get('http://localhost:8000/map.html?v=10')
    time.sleep(3)
    driver.execute_script('map.setView([37.4773484, 126.650818], 16);')
    time.sleep(1)
    url = driver.execute_script("return buildAuctionUrl('/api/map/auctions', map.getBounds());")
    print('Generated URL:', url)
finally:
    driver.quit()
