from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import re
import os
import requests

def extract_email_from_website(website_url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        }
        response = requests.get(website_url, headers=headers, timeout=10)
        response.raise_for_status()

        email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        emails = re.findall(email_pattern, response.text)

        return emails[0] if emails else None

    except requests.exceptions.RequestException as e:
        print(f"Error scraping {website_url}: {e}")
        return None

def scrape_google_maps(search_query):
    SCRAPING_DIR = "Results"
    os.makedirs(SCRAPING_DIR, exist_ok=True)

    safe_filename = f"{search_query.replace(' ', '_')}.csv"
    file_path = os.path.join(SCRAPING_DIR, safe_filename)

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    driver.get(f'https://www.google.com/maps/search/{search_query}/')

    try:
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "form:nth-child(2)"))).click()
    except Exception:
        pass

    scrollable_div = driver.find_element(By.CSS_SELECTOR, 'div[role="feed"]')
    for _ in range(8):  
     driver.execute_script("arguments[0].scrollBy(0, 1000);", scrollable_div)
    time.sleep(3)  
 

    items = driver.find_elements(By.CSS_SELECTOR, 'div[role="feed"] > div > div[jsaction]')

    results = []
    for item in items:
        data = {}
        try:
            data['Business Name'] = item.find_element(By.CSS_SELECTOR, ".fontHeadlineSmall").text
        except:
            data['Business Name'] = None

       

        try:
         data['Address'] = item.find_element(By.CSS_SELECTOR, '.W4Efsd > span:last-of-type span[dir="ltr"]').text
        except:
         data['Address'] = None


        try:  
         category_element = item.find_element(By.CSS_SELECTOR, '.W4Efsd > span:first-child span')
         data['Category'] = category_element.text if category_element.text.strip() else None
        except :
         data['Category'] = None


        try:
            data['Google Maps Link'] = item.find_element(By.CSS_SELECTOR, "a").get_attribute('href')
        except:
            data['Google Maps Link'] = None

        try:
            website_element = item.find_element(By.CSS_SELECTOR, 'a.lcr4fd.S9kvJb')
            website_url = website_element.get_attribute('href')
            if website_url:
              
              data['Website'] = website_url
              data["Email"] = extract_email_from_website(website_url)
            else :
               data['Website'] = None
               data['Email'] = None 
        except:
            data['Website'] = None
            data['Email']= None

        try:
            rating_text = item.find_element(By.CSS_SELECTOR, '.fontBodyMedium > span[role="img"]').get_attribute('aria-label')
            rating_numbers = [float(num.replace(",", ".")) for num in rating_text.split(" ") if num.replace(",", ".").replace(".", "", 1).isdigit()]
            if rating_numbers:
                data['Rating'] = rating_numbers[0]
                data['Reviews'] = int(rating_numbers[1]) if len(rating_numbers) > 1 else 0
        except:
            data['Rating'] = None
            data['Reviews'] = None

        try:
          phone_element = item.find_element(By.CSS_SELECTOR, '.UsdlK span[dir="ltr"]')
          data['Phone'] = phone_element.text.strip()
        except:
          data['Phone'] = None


        if data['Business Name']:
            results.append(data)

    df = pd.DataFrame(results)
    df.to_csv(file_path, index=False, encoding="utf-8-sig")


    driver.quit()

    return safe_filename
