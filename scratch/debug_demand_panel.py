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
    
    # 1. Debug openDemandPanel for residential directly
    print("\n--- Test 1: Directly executing openDemandPanel (Residential) ---")
    js_test_demand = """
        try {
            openDemandPanel(37.4979, 127.0276, '2024타경5020', '인천광역시 동구 송림동', '아파트', 84.9);
            return { status: 'called' };
        } catch (e) {
            return { error: e.message, stack: e.stack };
        }
    """
    res = driver.execute_script(js_test_demand)
    print("Execution result:", res)
    time.sleep(3) # Wait for fetch
    
    # Check what is inside the demand-panel-content
    panel_content = driver.execute_script("return document.getElementById('demand-panel-content').innerHTML;")
    print("Panel Content (first 500 chars):", panel_content[:500] if panel_content else "None")
    
    # Get browser logs
    print("Console logs after Test 1:")
    for log in driver.get_log('browser'):
        print(log)
        
    # 2. Debug realprice grids fetch
    print("\n--- Test 2: Enabling realprice grids toggle and calling fetchRealpriceGrids ---")
    js_test_grid = """
        try {
            const toggle = document.getElementById('toggle-realprice-grids');
            if (toggle) {
                toggle.checked = true;
                // Dispatch change event
                toggle.dispatchEvent(new Event('change'));
                return { status: 'toggle_enabled' };
            }
            return { status: 'toggle_not_found' };
        } catch (e) {
            return { error: e.message, stack: e.stack };
        }
    """
    res_grid = driver.execute_script(js_test_grid)
    print("Grid toggle result:", res_grid)
    time.sleep(3)
    
    # Check if realprice grid layer has layers
    grid_layers_count = driver.execute_script("return layers.realpriceGrid ? layers.realpriceGrid.getLayers().length : 'No layer';")
    print("Realprice grid layers count:", grid_layers_count)
    
    # Get browser logs
    print("Console logs after Test 2:")
    for log in driver.get_log('browser'):
        print(log)
        
except Exception as e:
    print("Error:", e)
finally:
    driver.quit()
