import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--log-level=3')

driver = webdriver.Chrome(options=options)
driver.get('http://localhost:8000/map.html?v=3')
time.sleep(2)

logs = driver.get_log('browser')
for log in logs:
    print(log)

driver.quit()
