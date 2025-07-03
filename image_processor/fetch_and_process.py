import os
import time
import threading
from datetime import datetime
import requests
from flask import Flask, render_template_string
from google.cloud import storage

# Environment variables
IMAGE_URL = os.environ.get("IMAGE_URL", "https://images.gov.im/webcams/bungalow1.jpg")
BUCKET_NAME = os.environ.get("BUCKET_NAME")
REFRESH_INTERVAL = int(os.environ.get("INTERVAL_SECONDS", "60"))

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Referer": "https://images.gov.im/webcams/",
    "Accept": "image/jpeg,image/png,image/*;q=0.8"
}

# Google Cloud Storage client
storage_client = storage.Client()
bucket = storage_client.bucket(BUCKET_NAME)

# Flask app
app = Flask(__name__)

def upload_image_to_gcs(image_data, filename):
    blob = bucket.blob(f"{datetime.utcnow().strftime('%Y%m%d')}/{filename}")
    blob.upload_from_string(image_data, content_type='image/jpeg')
    print(f"Uploaded {filename} to GCS bucket {BUCKET_NAME}")

def fetch_and_upload():
    while True:
        try:
            timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
            filename = f"{timestamp}.jpg"

            response = requests.get(IMAGE_URL, headers=HEADERS)
            response.raise_for_status()

            if response.content:
                upload_image_to_gcs(response.content, filename)
            else:
                print("Empty image data received.")

        except Exception as e:
            print(f"Error downloading or uploading image: {e}")

        time.sleep(REFRESH_INTERVAL)

@app.route("/")
def index():
    blobs = bucket.list_blobs(prefix=datetime.utcnow().strftime('%Y%m%d'))
    image_urls = [
        f"https://storage.googleapis.com/{BUCKET_NAME}/{blob.name}"
        for blob in sorted(blobs, key=lambda b: b.updated, reverse=True)[:5]
    ]
    img_tags = "\n".join([f"<img src='{url}' width='320' />" for url in image_urls])
    return render_template_string(f"<html><body><h1>Latest Images</h1>{img_tags}</body></html>")

# Start background thread
threading.Thread(target=fetch_and_upload, daemon=True).start()
