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
    driver.execute_script("""
        var scrollableDiv = arguments[0];
        function scrollWithinElement(scrollableDiv) {
            return new Promise((resolve) => {
                var totalHeight = 0;
                var distance = 1000;
                var scrollDelay = 3000;
                var timer = setInterval(() => {
                    var scrollHeightBefore = scrollableDiv.scrollHeight;
                    scrollableDiv.scrollBy(0, distance);
                    totalHeight += distance;
                    if (totalHeight >= scrollHeightBefore) {
                        totalHeight = 0;
                        setTimeout(() => {
                            var scrollHeightAfter = scrollableDiv.scrollHeight;
                            if (scrollHeightAfter > scrollHeightBefore) return;
                            clearInterval(timer);
                            resolve();
                        }, scrollDelay);
                    }
                }, 200);
            });
        }
        return scrollWithinElement(scrollableDiv);
    """, scrollable_div)

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
            data['Website'] = item.find_element(By.CSS_SELECTOR, 'div > a').get_attribute('href')
        except:
            data['Website'] = None

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
            text_content = item.text
            phone_pattern = r'((\+?\d{1,2}[ -]?)?(\(?\d{3}\)?[ -]?\d{3,4}[ -]?\d{4}|\(?\d{2,3}\)?[ -]?\d{2,3}[ -]?\d{2,3}[ -]?\d{2,3}))'
            matches = re.findall(phone_pattern, text_content)
            data['Phone'] = matches[0][0] if matches else None
        except:
            data['Phone'] = None

        if data['Business Name']:
            results.append(data)

    df = pd.DataFrame(results)
    df.to_csv(file_path, index=False, encoding="utf-8-sig")


    driver.quit()

    return safe_filename
