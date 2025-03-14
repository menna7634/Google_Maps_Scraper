from flask import Flask, render_template, request, send_file, url_for
from scraper import scrape_google_maps
import os

app = Flask(__name__)

SCRAPING_DIR = "Results"
os.makedirs(SCRAPING_DIR, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    csv_path = None
    if request.method == "POST":
        search_query = request.form.get("query")
        if search_query:
            csv_path = scrape_google_maps(search_query)
           

    return render_template("index.html", csv_path=csv_path)

@app.route("/download/<filename>")
def download(filename):
    file_path = os.path.join(SCRAPING_DIR, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return "File not found", 404

if __name__ == "__main__":
    app.run(debug=True)
