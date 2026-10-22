import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

print("Starting Chrome...")
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
driver = webdriver.Chrome(options=options)

try:
    print("Loading map.html...")
    driver.get('http://localhost:8000/map.html')
    time.sleep(3)

    print("Clicking toggle-commercial...")
    driver.execute_script("document.getElementById('toggle-commercial').click();")
    time.sleep(3)

    print("Browser Logs after commercial:")
    for log in driver.get_log('browser'):
        print(log)

    print("Clicking toggle-subways...")
    driver.execute_script("document.getElementById('toggle-subways').click();")
    time.sleep(3)

    print("Browser Logs after subways:")
    for log in driver.get_log('browser'):
        print(log)

    print("Panning map...")
    driver.execute_script("map.panBy([100, 100]);")
    time.sleep(3)

    print("Browser Logs after pan:")
    for log in driver.get_log('browser'):
        print(log)

except Exception as e:
    print("Exception:", e)
finally:
    driver.quit()
    print("Done.")
