from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)
try:
    driver.get('http://localhost:8000/map.html?v=10')
    time.sleep(3)
    
    # Run the async function and catch any promise rejection
    print("Executing openDemandPanel with promise error catching...")
    driver.execute_script("""
        window.lastError = null;
        openDemandPanel(37.4773484, 126.650818, '2023 타경 18340', '인천광역시 동구 송림동 10-18', '아파트', 84.9)
            .catch(e => {
                window.lastError = { message: e.message, stack: e.stack };
            });
    """)
    time.sleep(5) # Give it 5 seconds
    
    # Retrieve any caught promise errors
    last_err = driver.execute_script("return window.lastError;")
    if last_err:
        print("ASYNC ERROR CAUGHT:", last_err)
    else:
        print("No async error caught from promise.")
        
    # Check if there are any error cards or if the content rendered successfully
    content = driver.execute_script("return document.getElementById('demand-panel-content').innerHTML;")
    print("\nRendered Panel Content (first 1000 chars):")
    print(content[:1000] if content else "None")
    
    # Get browser console logs
    print("\nBrowser console logs:")
    for log in driver.get_log('browser'):
        print(log)
        
finally:
    driver.quit()
