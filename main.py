#!/data/data/com.termux/files/usr/bin/python
import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from rapidfuzz import fuzz, process

# Termux Android configuration
MIN_CONFIDENCE = 45
TIMEOUT = 30

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service as FirefoxService

def setup_termux_browser():
    firefox_options = Options()
    firefox_options.binary_location = "/data/data/com.termux/files/usr/bin/firefox"
    firefox_options.add_argument("--headless")
    firefox_options.add_argument("--width=360")
    firefox_options.add_argument("--height=640")

    service = FirefoxService(executable_path="/data/data/com.termux/files/usr/bin/geckodriver")
    
    return webdriver.Firefox(service=service, options=firefox_options, selenium_manager=False )

def scroll_click(driver, element):
    """Mobile-optimized click with scroll"""
    driver.execute_script("arguments[0].scrollIntoView()", element)
    element.click()
    time.sleep(1)

def extract_result(driver):
    """Extract result text with mobile selectors"""
    selectors = [
        "p.text-success b",    # Success message
        "p.text-danger",       # Failure message
        "div.result-status",   # Alternative container
        "table.result-table"   # Tabular data
    ]
    
    for selector in selectors:
        try:
            el = driver.find_element(By.CSS_SELECTOR, selector)
            if el.is_displayed():
                return el.text.strip()
        except:
            continue
    return "Result not found"

def main():
    print("📱 Mobile IPO Checker for Termux")
    
    # Load accounts
    try:
        accounts = pd.read_csv("accounts.csv")
        accounts['boid'] = accounts['boid'].astype(str).str.replace(r'\D', '', regex=True)
    except Exception as e:
        print(f"❌ Error loading accounts: {e}")
        return

    # Get IPO name
    ipo_name = input("🔍 Enter IPO name: ").strip()
    if not ipo_name:
        print("❌ IPO name required")
        return

    driver = setup_termux_browser()
    results = []
    
    try:
        for idx, (_, row) in enumerate(accounts.iterrows(), 1):
            print(f"\n🔄 Processing {idx}/{len(accounts)}: {row['name']}")
            
            # Load page
            driver.get("https://iporesult.cdsc.com.np/")
            
            # Select IPO
            dropdown = WebDriverWait(driver, TIMEOUT).until(
                EC.presence_of_element_located((By.ID, "companyShare"))
            )
            scroll_click(driver, dropdown)
            
            # Search IPO
            search = WebDriverWait(driver, TIMEOUT).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "div.ng-input > input"))
            )
            search.send_keys(ipo_name)
            time.sleep(2)
            
            # Select best match
            options = driver.find_elements(By.CSS_SELECTOR, "div.ng-option")
            if options:
                best_match = max(
                    [(opt.text.strip(), fuzz.token_sort_ratio(ipo_name, opt.text.strip())) 
                    for opt in options],
                    key=lambda x: x[1]
                )
                if best_match[1] >= MIN_CONFIDENCE:
                    for opt in options:
                        if opt.text.strip() == best_match[0]:
                            scroll_click(driver, opt)
                            break
            
            # Enter BOID
            boid_field = driver.find_element(By.ID, "boid")
            boid_field.send_keys(row['boid'])
            
            # CAPTCHA handling
            print("⏳ Please solve CAPTCHA on your device...")
            submit = WebDriverWait(driver, 120).until(
                EC.element_to_be_clickable((By.ID, "resultCheck"))
            )
            submit.click()
            
            # Get result
            result = extract_result(driver)
            results.append({
                'Name': row['name'],
                'BOID': row['boid'],
                'Result': result,
                'Timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            })
            
            # Save progress
            pd.DataFrame(results).to_csv("ipo_results.csv", index=False)
            
        print("\n✅ All done! Results saved to ipo_results.csv")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
