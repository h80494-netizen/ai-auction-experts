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
    print("Waiting 5 seconds...")
    time.sleep(5)
    
    print("Getting console logs:")
    logs = driver.get_log('browser')
    for log in logs:
        print(log)
        
    print("Page Title:", driver.title)
except Exception as e:
    print("Error:", e)
finally:
    driver.quit()
