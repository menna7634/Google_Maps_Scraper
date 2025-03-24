import os
import time
import random
import re
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
from flask import Flask, render_template, request, send_from_directory, jsonify
from threading import Thread, Lock
import logging

app = Flask(__name__)

SCRAPING_DIR = "Results"
os.makedirs(SCRAPING_DIR, exist_ok=True)

# Initialize logging for errors
logging.basicConfig(filename='scraping_errors.log', level=logging.ERROR)

stop_scraping = False  # Flag to stop scraping
scraping_count = 0  # Number of scrapes performed
scraping_lock = Lock()  # Lock to protect access to stop_scraping

# Function to initialize the WebDriver
def get_driver():
    options = Options()
    options.add_argument("--headless")  # Run in headless mode (without opening browser window)
    driver = webdriver.Chrome(options=options)
    return driver

# Function to extract email from website using regex
def extract_email_from_website(website_url):
    """Extracts an email address from a website's HTML content."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(website_url, headers=headers, timeout=10)
        response.raise_for_status()

        email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        emails = re.findall(email_pattern, response.text)

        return emails[0] if emails else None
    except requests.exceptions.RequestException as e:
        logging.error(f"Error extracting email from {website_url}: {str(e)}")
        return None

# Function to scrape Google Maps search results using Selenium
def scrape_google_maps(search_query):
    global stop_scraping  # Use global variable to control stopping

    safe_filename = f"{search_query.replace(' ', '_')}.csv"
    file_path = os.path.join(SCRAPING_DIR, safe_filename)

    driver = get_driver()

    try:
        # Fetch the Google Maps search page
        print(f"Navigating to Google Maps for search query: {search_query}")
        driver.get(f'https://www.google.com/maps/search/{search_query}/')

        # Wait for the page to load
        time.sleep(2)

        results = []

        # Infinite scroll to load more results
        while not stop_scraping:
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            items = soup.find_all('div', {'jsaction': 'rcuQ6b:npT2md'})

            for item in items:
                data = {}
                try:
                    data['Business Name'] = item.find("span", {"class": "fontHeadlineSmall"}).text
                except Exception as e:
                    logging.error(f"Error extracting Business Name: {str(e)}")
                    data['Business Name'] = None

                try:
                    data['Address'] = item.find("span", {"class": "W4Efsd"}).text
                except Exception as e:
                    logging.error(f"Error extracting Address: {str(e)}")
                    data['Address'] = None

                try:
                    category_element = item.find("span", {"class": "W4Efsd"})
                    data['Category'] = category_element.text if category_element else None
                except Exception as e:
                    logging.error(f"Error extracting Category: {str(e)}")
                    data['Category'] = None

                try:
                    data['Google Maps Link'] = item.find("a")['href']
                except Exception as e:
                    logging.error(f"Error extracting Google Maps Link: {str(e)}")
                    data['Google Maps Link'] = None

                try:
                    website_element = item.find('a', {'class': 'lcr4fd'})
                    website_url = website_element['href'] if website_element else None
                    if website_url:
                        data['Website'] = website_url
                        data["Email"] = extract_email_from_website(website_url)
                    else:
                        data['Website'] = None
                        data['Email'] = None
                except Exception as e:
                    logging.error(f"Error extracting Website or Email: {str(e)}")
                    data['Website'] = None
                    data['Email'] = None

                try:
                    data['Phone Number'] = item.find('span', {'class': 'UsdlK'}).text
                except Exception as e:
                    logging.error(f"Error extracting Phone Number: {str(e)}")
                    data['Phone Number'] = None

                try:
                    data['Rating'] = item.find('span', {'class': 'MW4etd'}).text
                except Exception as e:
                    logging.error(f"Error extracting Rating: {str(e)}")
                    data['Rating'] = None

                try:
                    num_reviews_element = item.find('span', {'dir': 'ltr'})
                    data['Number of Reviews'] = num_reviews_element.text.strip("()") if num_reviews_element else None
                except Exception as e:
                    logging.error(f"Error extracting Number of Reviews: {str(e)}")
                    data['Number of Reviews'] = None

                if data['Business Name']:
                    results.append(data)

            # Scroll down to load more results
            try:
                body = driver.find_element_by_tag_name('body')
                body.send_keys(Keys.PAGE_DOWN)
                time.sleep(random.uniform(1.5, 3))  # Adding random delay between scrolls
            except Exception as e:
                logging.error(f"Error during scrolling: {str(e)}")
                break

        # Save results to CSV
        try:
            print(f"Saving results to CSV: {file_path}")
            df = pd.DataFrame(results)
            df.to_csv(file_path, index=False, encoding="utf-8-sig")
        except Exception as e:
            logging.error(f"Error saving CSV: {str(e)}")
            return None

        print(f"Scraping completed! {len(results)} items saved.")
        return safe_filename

    except Exception as e:
        logging.error(f"Error during scraping: {str(e)}")
        return None
    finally:
        driver.quit()  # Close the browser

# Flask routes

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/start_scraping", methods=["POST"])
def start_scraping():
    search_query = request.form.get("query")
    
    def background_scraping():
        global stop_scraping
        with scraping_lock:  # Ensure thread safety
            stop_scraping = False  # Reset stop flag when starting new scrape
        scrape_google_maps(search_query)
    
    # Run the scraping in a background thread
    thread = Thread(target=background_scraping)
    thread.start()

    return jsonify({"message": "Scraping started!"})

@app.route("/stop_scraping", methods=["POST"])
def stop_scraping_func():
    global stop_scraping
    with scraping_lock:  # Ensure thread safety
        stop_scraping = True  # Set flag to stop scraping
    return jsonify({"message": "Scraping stopping in progress..."})

@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(SCRAPING_DIR, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
