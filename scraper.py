import os
import time
import re
import requests
import pandas as pd
from flask import Flask, render_template, request, send_from_directory, jsonify
from flask_socketio import SocketIO
from threading import Thread, Lock
from playwright.sync_api import sync_playwright

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

SCRAPING_DIR = "Results"
os.makedirs(SCRAPING_DIR, exist_ok=True)

stop_scraping = False  # Flag to stop the scraping
scraping_count = 0  # Number of scrapes performed
scraping_lock = Lock()  # Lock to protect access to stop_scraping

def extract_email_from_website(website_url):
    """Extracts an email address from a website's HTML content."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(website_url, headers=headers, timeout=10)
        response.raise_for_status()

        email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        emails = re.findall(email_pattern, response.text)

        return emails[0] if emails else None
    except requests.exceptions.RequestException:
        return None

def scrape_google_maps(search_query):
    """Scrapes Google Maps search results for businesses using Playwright."""
    global stop_scraping  # Use global variable to control stopping

    safe_filename = f"{search_query.replace(' ', '_')}.csv"
    file_path = os.path.join(SCRAPING_DIR, safe_filename)

    try:
        # Use sync_playwright for synchronous browser operations
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            try:
                print(f"Navigating to Google Maps for search query: {search_query}")
                page.goto(f'https://www.google.com/maps/search/{search_query}/')
                page.wait_for_selector('form:nth-child(2)', timeout=5000)
                page.click('form:nth-child(2)')
            except Exception as e:
                print(f"Error during navigation or interaction with page: {e}")
                return None

            # Scrolling and scraping data
            try:
                print("Starting scroll and scraping data")
                for _ in range(15):
                    page.evaluate('window.scrollBy(0, 1000);')
                    time.sleep(1)

                items = page.query_selector_all('div[role="feed"] > div > div[jsaction]')
                results = []

                for index, item in enumerate(items):
                    if stop_scraping:  # Check if scraping should stop
                        break

                    data = {}
                    try:
                        data['Business Name'] = item.query_selector(".fontHeadlineSmall").text_content()
                    except Exception as e:
                        print(f"Error extracting Business Name: {e}")
                        data['Business Name'] = None

                    try:
                        data['Address'] = item.query_selector('.W4Efsd > span:last-of-type span[dir="ltr"]').text_content()
                    except Exception as e:
                        print(f"Error extracting Address: {e}")
                        data['Address'] = None

                    try:
                        category_element = item.query_selector('.W4Efsd > span:first-child span')
                        data['Category'] = category_element.text_content() if category_element else None
                    except Exception as e:
                        print(f"Error extracting Category: {e}")
                        data['Category'] = None

                    try:
                        data['Google Maps Link'] = item.query_selector("a").get_attribute('href')
                    except Exception as e:
                        print(f"Error extracting Google Maps Link: {e}")
                        data['Google Maps Link'] = None

                    try:
                        website_element = item.query_selector('a.lcr4fd.S9kvJb')
                        website_url = website_element.get_attribute('href') if website_element else None
                        if website_url:
                            data['Website'] = website_url
                            data["Email"] = extract_email_from_website(website_url)
                        else:
                            data['Website'] = None
                            data['Email'] = None
                    except Exception as e:
                        print(f"Error extracting Website or Email: {e}")
                        data['Website'] = None
                        data['Email'] = None

                    try:
                        data['Phone Number'] = item.query_selector('.UsdlK').text_content()
                    except Exception as e:
                        print(f"Error extracting Phone Number: {e}")
                        data['Phone Number'] = None

                    try:
                        data['Rating'] = item.query_selector('.MW4etd').text_content()
                    except Exception as e:
                        print(f"Error extracting Rating: {e}")
                        data['Rating'] = None

                    try:
                        num_reviews_element = item.query_selector('.UY7F9 span[dir="ltr"]')
                        data['Number of Reviews'] = num_reviews_element.text_content().strip("()") if num_reviews_element else None
                    except Exception as e:
                        print(f"Error extracting Number of Reviews: {e}")
                        data['Number of Reviews'] = None

                    if data['Business Name']:
                        results.append(data)

            except Exception as e:
                print(f"Error during the scraping loop: {e}")
                return None

            # Save results to CSV
            try:
                print(f"Saving results to CSV: {file_path}")
                df = pd.DataFrame(results)
                df.to_csv(file_path, index=False, encoding="utf-8-sig")
            except Exception as e:
                print(f"Error saving CSV: {e}")
                return None

            browser.close()
            print(f"Scraping completed! {len(results)} items saved.")
            return safe_filename

    except Exception as e:
        print(f"Error during Playwright setup or execution: {e}")
        return None


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
    socketio.run(app, debug=True)
