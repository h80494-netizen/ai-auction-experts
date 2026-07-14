from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)
try:
    driver.get('http://localhost:8000/map.html?v=10')
    time.sleep(3)
    
    # Check if functions and panel exist
    panel_exists = driver.execute_script("return document.getElementById('demand-panel') !== null;")
    panel_content_exists = driver.execute_script("return document.getElementById('demand-panel-content') !== null;")
    openDemandPanel_type = driver.execute_script("return typeof openDemandPanel;")
    isResidential_type = driver.execute_script("return typeof isResidential;")
    
    print("demand-panel exists:", panel_exists)
    print("demand-panel-content exists:", panel_content_exists)
    print("openDemandPanel type:", openDemandPanel_type)
    print("isResidential type:", isResidential_type)
    
    # Test isResidential function call
    is_res_test = driver.execute_script("return isResidential('아파트');")
    print("isResidential('아파트') result:", is_res_test)
    
    # Test openDemandPanel synchronous portion
    js_test = """
        try {
            console.log("Calling openDemandPanel from test script...");
            let p = openDemandPanel(37.4773484, 126.650818, '2023 타경 18340', '인천광역시 동구 송림동', '아파트', 84.9);
            console.log("Called openDemandPanel, promise:", p);
            return { success: true, is_promise: p instanceof Promise };
        } catch (e) {
            return { error: e.message, stack: e.stack };
        }
    """
    res = driver.execute_script(js_test)
    print("Direct execution result:", res)
    time.sleep(3)
    
    print("\nBrowser console logs:")
    for log in driver.get_log('browser'):
        print(log)
        
finally:
    driver.quit()
