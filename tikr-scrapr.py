from dotenv import load_dotenv
import os
import re
import time
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.common.exceptions import StaleElementReferenceException

load_dotenv()

# download ChromeDriver https://chromedriver.storage.googleapis.com/index.html?path=114.0.5735.90/
# curl -sS https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/google.gpg >/dev/null
# sudo apt update
# sudo apt install google-chrome-stable

def debug():
    while True:
        time.sleep(1)
        
def init_driver():
    driver_path = r'/drivers/chromedriver'
    options = ChromeOptions()
    options.add_argument('--headless-new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    service = ChromeService(options=options, executable_path=driver_path)
    return webdriver.Chrome(service=service)

def login(driver, login_url, username, password):
    driver.get(login_url)
    driver.maximize_window() 
    time.sleep(2)

    username_field = driver.find_element(By.XPATH, '//*[@id="input-11"]')
    password_field = driver.find_element(By.XPATH, '//*[@id="input-14"]')
    
    username_field.send_keys(username)
    password_field.send_keys(password)

    login_button = driver.find_element(By.XPATH, '//button[span[contains(text(),"Sign In")]]')
    login_button.click()
    time.sleep(5)
    return driver
 
def fetch_table(driver):
    global_screener_button = driver.find_element(By.XPATH, "//div[contains(text(), 'Global Screener')]")
    global_screener_button.click()  
    time.sleep(2)
    wait = WebDriverWait(driver, 10)
    general_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[contains(text(),"General")]')))
    general_button.click()
    time.sleep(2)
    wait = WebDriverWait(driver, 10)
    fetch_screen_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[span[contains(text(),"Fetch Screen")]]')))  
    # Fetch Screen is out ouf the Viewport, so we use JS to click it  
    driver.execute_script("arguments[0].click();", fetch_screen_button)
    time.sleep(2)
    # Wait until the table is loaded
    wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/div/div[1]/main/div/div/div[2]/div/div/div[3]')))
    return driver

def get_links(driver):
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    tbody = soup.find_all('tbody')[1]
    href_list = [a['href'] for a in tbody.find_all('a')]
    # Remove duplicates
    unique_hrefs = list(set(href_list))
    # Add prefix to href values
    prefixed_hrefs = ['https://app.tikr.com' + href for href in unique_hrefs]
    return prefixed_hrefs

def get_revenues_yoy(driver, company_link):
    attempts = 0
    while attempts < 5:
        try:
            financials_link = company_link.replace("/about?", "/financials?")
            driver.get(financials_link)
            time.sleep(3)
            wait = WebDriverWait(driver, 10)
            slider = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'v-slider__track-container')))
            driver.execute_script("arguments[0].click();", slider)
            time.sleep(3)
            row = wait.until(EC.presence_of_element_located((By.XPATH, '//td[contains(text(),"% Change YoY")]/..')))
            tds = row.find_elements(By.TAG_NAME, "td")
            values = []
            for td in tds[1:]:
                 if td.text.strip():
                    value = td.text.strip()
                    match = re.search(r'\((.*?)\)', value)
                    if match:
                        enclosed_value = match.group(1)
                        value = value.replace(f"({enclosed_value})", enclosed_value)
                        enclosed_value = enclosed_value.replace(',', '')
                        value = float(enclosed_value.replace('%', ''))
                        value *= -1
                    else:
                        value = value.replace(',', '')
                        value = float(value.replace('%', ''))
                    values.append(value)
            return values[-10:]  # Return the last 10 values
        except StaleElementReferenceException:
            attempts += 1
            continue
        break

def get_company_name(driver, company_link):
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    div_element = soup.find('div', class_='col')
    lines = div_element.text.strip().split('\n')
    company_name = lines[0].strip()
    ticker = None
    publ_found = False

    for item in lines[1:]:
        item = item.strip()
        match = re.search(r'\((.*?)\)', item)
        if match:
            if '(publ)' in item:
                company_name += ' (publ)'
                publ_found = True
            elif publ_found or not ticker:
                ticker = match.group(0)
                break
    return f"{company_name} {ticker if ticker else ''}"

def add_to_my_watchlist(driver, company_link, added_list):
    driver.get(company_link)
    add_to_my_watchlist_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/div/div/div[1]/main/div/div/div[1]/div[1]/div/div/div/div[1]/button[1]")))
    favorite_status = add_to_my_watchlist_button.find_element(By.TAG_NAME, "i").text
    
    if favorite_status == "favorite_border":
        driver.execute_script("arguments[0].click();", add_to_my_watchlist_button) 
    
    favorite_status = add_to_my_watchlist_button.find_element(By.TAG_NAME, "i").text   
    while favorite_status == "favorite_border":
        time.sleep(0.5)
        favorite_status = add_to_my_watchlist_button.find_element(By.TAG_NAME, "i").text 
        
    company_name = get_company_name(driver, company_link)
    if company_name:
        if favorite_status == "favorite_border":
            added_list.append(company_name)
        else:
            added_list.append(company_name)
    return

def remove_from_my_watchlist(driver, company_link, removed_list):
    driver.get(company_link)
    remove_from_watchlist_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div/div/div/div/main/div/div/div[1]/div[1]/div/div/div/div[1]/button[1]")))
    favorite_status = remove_from_watchlist_button.find_element(By.TAG_NAME, "i").text

    if favorite_status == "favorite":
        driver.execute_script("arguments[0].click();", remove_from_watchlist_button) 
        
    favorite_status = remove_from_watchlist_button.find_element(By.TAG_NAME, "i").text    
    while favorite_status == "favorite":
        time.sleep(0.5)
        favorite_status = remove_from_watchlist_button.find_element(By.TAG_NAME, "i").text   
        
    company_name = get_company_name(driver, company_link)
    if company_name:
        if favorite_status == "favorite":
            removed_list.append(company_name)      
    return

def update_my_watchlist(driver, links, min):
    added_list = []
    removed_list = []
    for link in links:
        revenues_yoy = get_revenues_yoy(driver, link)
        if all(value > min for value in revenues_yoy):
            add_to_my_watchlist(driver, link, added_list)
        else:
            remove_from_my_watchlist(driver, link, removed_list)
    return added_list, removed_list

def tikr_scraper():
    added_list = []
    removed_list = []
    try:
        login_url = "https://app.tikr.com/login"  
        username = os.getenv("EMAIL")
        password = os.getenv("PASSWORD")
        driver = init_driver()
        driver = login(driver, login_url, username, password)
        driver = fetch_table(driver)
        links = get_links(driver) # Shorten the list for testing
        print("Links to check:", len(links))
        accepted_min_value = -10

        added_list, removed_list = update_my_watchlist(driver, links, accepted_min_value)
        
    except KeyboardInterrupt:
        print("Program interrupted!")    
    except Exception as e:
        print("An error occurred during execution:\n", str(e))
        
    finally:
        print("\nMy Watchlist:")
        for company in added_list:
            print("- ", company)
            
        print("Removed from My Watchlist:")
        for link in removed_list:
            print("- ",link)
            
        driver.quit()

if __name__ == "__main__":
    tikr_scraper()