from dotenv import load_dotenv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import time

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
    driver.maximize_window() # DEBUG HELPER
    time.sleep(1)

    username_field = driver.find_element(By.XPATH, '//*[@id="input-11"]')
    password_field = driver.find_element(By.XPATH, '//*[@id="input-14"]')
    
    username_field.send_keys(username)
    password_field.send_keys(password)

    login_button = driver.find_element(By.XPATH, '//button[span[contains(text(),"Sign In")]]')
    login_button.click()
    time.sleep(4)
    return driver
 
def fetch_table(driver):
    global_screener_button = driver.find_element(By.XPATH, "//div[contains(text(), 'Global Screener')]")
    global_screener_button.click()  
    
    wait = WebDriverWait(driver, 5)
    general_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//a[contains(text(),"General")]')))
    general_button.click()
    
    wait = WebDriverWait(driver, 5)
    fetch_screen_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[span[contains(text(),"Fetch Screen")]]')))  
    # Fetch Screen is out ouf the Viewport, so we use JS to click it  
    driver.execute_script("arguments[0].click();", fetch_screen_button)
    
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
    return driver, prefixed_hrefs
          
def tikr_scraper():
    login_url = "https://app.tikr.com/login"  
    username = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")
    driver = init_driver()
    driver = login(driver, login_url, username, password)
    driver = fetch_table(driver)
    driver, links = get_links(driver)
    print(links)
    driver.quit()
    
if __name__ == "__main__":
    tikr_scraper()
