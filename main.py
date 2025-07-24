import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Mobile-optimized configuration
def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('user-agent=Mozilla/5.0 (Linux; Android 10; Mobile) AppleWebKit/537.36')
    return webdriver.Chrome(options=options)

def check_ipo(driver, ipo_name, boid, name):
    try:
        # Search IPO
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "companyShare"))
        )
        search_box.send_keys(ipo_name)
        time.sleep(2)
        
        # Select first match (simplified for mobile)
        driver.find_element(By.CSS_SELECTOR, "div.ng-option").click()
        
        # Fill account details
        driver.find_element(By.ID, "boid").send_keys(boid)
        driver.find_element(By.ID, "name").send_keys(name)
        
        print("ℹ️ Please solve CAPTCHA manually in browser...")
        input("Press Enter AFTER solving CAPTCHA...")
        
        # Submit and get result
        driver.find_element(By.ID, "resultCheck").click()
        result = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".result-status"))
        )
        return result.text
    except Exception as e:
        return f"Error: {str(e)}"

def main():
    driver = setup_driver()
    try:
        driver.get("https://iporesult.cdsc.com.np")
        
        # Load accounts
        accounts = pd.read_csv(os.path.join(os.path.dirname(__file__), '../assets/accounts.csv'))
        
        for _, row in accounts.iterrows():
            print(f"\nChecking {row['name']}...")
            result = check_ipo(driver, input("Enter IPO name: "), row['boid'], row['name'])
            print("Result:", result)
            
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
