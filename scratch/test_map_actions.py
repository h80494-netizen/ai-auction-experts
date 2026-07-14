import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--log-level=3')

print("Starting Chrome...")
driver = webdriver.Chrome(options=options)
try:
    print("Navigating to http://localhost:8000/map.html?v=10 ...")
    driver.get('http://localhost:8000/map.html?v=10')
    time.sleep(3)
    
    print("Centering map to [37.4773484, 126.650818] (Songnim-dong) with zoom 16...")
    driver.execute_script("map.setView([37.4773484, 126.650818], 16);")
    time.sleep(3)
    
    # 1. Check all loaded auction markers
    print("Loaded auction markers:")
    cases = driver.execute_script("return layers.auction.getLayers().map(l => l.auctionData ? l.auctionData.case_no : 'No data');")
    print("Auction case numbers in view:", cases)
    
    # 2. Check if we can find any marker, or check if filters are active
    print("Checking filters:")
    filter_state = driver.execute_script("return getAuctionFilterState();")
    print("Filter state:", filter_state)
    
except Exception as e:
    print("Error:", e)
finally:
    driver.quit()
