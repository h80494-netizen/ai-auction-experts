from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)
try:
    driver.get('http://localhost:8000/map.html?v=10')
    time.sleep(3)
    
    print("Executing raw fetch in browser...")
    js_test = """
        window.testFetchResult = null;
        window.testFetchError = null;
        fetch('/api/map/demographics?lat=37.4773484&lng=126.650818')
            .then(res => res.json())
            .then(json => { window.testFetchResult = json; })
            .catch(err => { window.testFetchError = err.message; });
    """
    driver.execute_script(js_test)
    time.sleep(3)
    
    result = driver.execute_script("return window.testFetchResult;")
    error = driver.execute_script("return window.testFetchError;")
    
    print("Fetch Result:", result)
    print("Fetch Error:", error)
    
finally:
    driver.quit()
