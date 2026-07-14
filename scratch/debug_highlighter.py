import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By

print("Initializing Chrome...")
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')
driver = webdriver.Chrome(options=options)

try:
    print("Navigating to http://localhost:8000/map.html...")
    driver.get('http://localhost:8000/map.html')
    time.sleep(3)
    
    btn = driver.find_element(By.ID, "btn-highlighter")
    mode_container = driver.find_element(By.ID, "highlighter-mode-container")
    count_el = driver.find_element(By.ID, "highlight-count")
    
    print(f"Highlighter button active state: {btn.get_attribute('class')}")
    print(f"Mode container display: {mode_container.value_of_css_property('display')}")
    print(f"Count element display: {count_el.value_of_css_property('display')}")
    
    print("Clicking highlighter button...")
    btn.click()
    time.sleep(1)
    
    print(f"After click - Highlighter button active state: {btn.get_attribute('class')}")
    print(f"After click - Mode container display: {mode_container.value_of_css_property('display')}")
    print(f"After click - Count element display: {count_el.value_of_css_property('display')}")
    print(f"After click - Count element text: '{count_el.text}'")
    
    # Save screenshot of the top-actions area
    driver.save_screenshot("highlighter_click_test.png")
    print("Screenshot saved to highlighter_click_test.png")
    
    # Also check if there are any console errors
    print("Browser console logs:")
    for log in driver.get_log('browser'):
        print(log)

except Exception as e:
    print("Error:", e)
finally:
    driver.quit()
    print("Done.")
