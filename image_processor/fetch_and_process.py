import os
import time
import threading
from datetime import datetime
from pathlib import Path

import requests
from flask import Flask, render_template_string
from google.cloud import storage
from google.api_core.exceptions import GoogleAPIError

# Configuration from environment
IMAGE_URL = os.environ.get("IMAGE_URL", "https://images.gov.im/webcams/bungalow1.jpg")
BUCKET_NAME = os.environ.get("BUCKET_NAME")
INTERVAL_SECONDS = int(os.environ.get("INTERVAL_SECONDS", "60"))

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Referer": "https://images.gov.im/webcams/",
    "Accept": "image/jpeg,image/png,image/*;q=0.8"
}

# Flask app
app = Flask(__name__)

# GCS client
storage_client = storage.Client()
bucket = storage_client.bucket(BUCKET_NAME)

def upload_image_to_gcs(image_data):
    """Uploads image data to GCS in sequential format under today's folder."""
    today_prefix = datetime.utcnow().strftime("%Y%m%d")

    try:
        # Get current index
        blobs = list(bucket.list_blobs(prefix=f"{today_prefix}/"))
        max_index = 0
        for blob in blobs:
            filename = Path(blob.name).name
            if filename.endswith(".jpg") and filename[:-4].isdigit():
                max_index = max(max_index, int(filename[:-4]))

        next_index = max_index + 1
        new_filename = f"{today_prefix}/{next_index:04d}.jpg"

        blob = bucket.blob(new_filename)
        blob.upload_from_string(image_data, content_type="image/jpeg")
        blob.make_public()

        print(f"Uploaded image as {new_filename}")
    except GoogleAPIError as e:
        print(f"GCS upload error: {e}")
    except Exception as e:
        print(f"Unexpected upload error: {e}")

def fetch_and_upload_loop():
    """Fetches an image every N seconds and uploads to GCS."""
    while True:
        try:
            print("Fetching image...")
            resp = requests.get(IMAGE_URL, headers=HEADERS)
            resp.raise_for_status()

            if resp.content:
                upload_image_to_gcs(resp.content)
            else:
                print("Empty image received.")

        except Exception as e:
            print(f"Download or upload failed: {e}")

        time.sleep(INTERVAL_SECONDS)

@app.route("/")
def index():
    """Displays the 5 most recent images from GCS."""
    try:
        prefix = datetime.utcnow().strftime("%Y%m%d")
        blobs = list(bucket.list_blobs(prefix=f"{prefix}/"))

        if not blobs:
            return "No images found."

        sorted_blobs = sorted(blobs, key=lambda b: b.updated, reverse=True)[:5]
        image_urls = [f"https://storage.googleapis.com/{BUCKET_NAME}/{blob.name}" for blob in sorted_blobs]

        image_html = "\n".join([f"<img src='{url}' width='320'>" for url in image_urls])
        return render_template_string(f"<html><body><h1>Latest Images</h1>{image_html}</body></html>")

    except Exception as e:
        print(f"Error in index route: {e}")
        return f"Internal Server Error: {e}", 500

# Start download loop in background thread
threading.Thread(target=fetch_and_upload_loop, daemon=True).start()
