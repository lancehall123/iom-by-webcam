import os
import time
import threading
from datetime import datetime
from pathlib import Path
import requests
from flask import Flask, render_template_string
from google.cloud import storage

# Camera definitions
CAMERA_CONFIGS = [
    {"name": "bungalow1", "url": "https://images.gov.im/webcams/bungalow1.jpg"},
    {"name": "bungalow2", "url": "https://images.gov.im/webcams/bungalow2.jpg"},
    {"name": "bungalow3", "url": "https://images.gov.im/webcams/bungalow3.jpg"},
    {"name": "ed_tower", "url": "https://images.gov.im/webcams/ed_tower.jpg"},
    {"name": "DTL", "url": "https://images.gov.im/webcams/DTL_00001.jpg"},
    {"name": "peel", "url": "https://images.gov.im/webcams/peel_00001.jpg"},
    {"name": "PortErin", "url": "https://images.gov.im/webcams/PortErin.jpg"},
    {"name": "Castletown", "url": "https://images.gov.im/webcams/Castletown_Bay.jpg"},
    {"name": "Ramsey", "url": "https://images.gov.im/webcams/Ramsey_00001.jpg"},
]

# Config from environment
BUCKET_NAME = os.environ.get("BUCKET_NAME")
REFRESH_INTERVAL = int(os.environ.get("INTERVAL_SECONDS", "60"))

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Referer": "https://images.gov.im/webcams/",
    "Accept": "image/jpeg,image/png,image/*;q=0.8"
}

# GCS client
storage_client = storage.Client()
bucket = storage_client.bucket(BUCKET_NAME)

app = Flask(__name__)

def upload_image_to_gcs(camera, image_data):
    today = datetime.utcnow().strftime("%Y%m%d")
    prefix = f"{camera}/{today}/"
    blobs = list(bucket.list_blobs(prefix=prefix))
    max_index = max([int(Path(b.name).stem) for b in blobs if Path(b.name).stem.isdigit()] or [-1]) + 1
    filename = f"{prefix}{max_index:04d}.jpg"
    blob = bucket.blob(filename)
    blob.upload_from_string(image_data, content_type="image/jpeg")
    blob.make_public()
    print(f"[{camera}] Uploaded: {filename} -> {blob.public_url}")

def fetch_and_upload(camera, url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        if response.content:
            upload_image_to_gcs(camera, response.content)
        else:
            print(f"[{camera}] Empty content")
    except Exception as e:
        print(f"[{camera}] ERROR: {e}")

def background_loop():
    while True:
        for cam in CAMERA_CONFIGS:
            threading.Thread(target=fetch_and_upload, args=(cam["name"], cam["url"]), daemon=True).start()
        time.sleep(REFRESH_INTERVAL)

@app.route("/")
def index():
    today = datetime.utcnow().strftime("%Y%m%d")
    html = "<html><body><h1>Latest Images</h1>"
    for cam in CAMERA_CONFIGS:
        blobs = list(bucket.list_blobs(prefix=f"{cam['name']}/{today}/"))
        latest = sorted(blobs, key=lambda b: b.updated, reverse=True)[:1]
        for blob in latest:
            url = f"https://storage.googleapis.com/{BUCKET_NAME}/{blob.name}"
            html += f"<h3>{cam['name']}</h3><img src='{url}' width='320' /><br/>"
    html += "</body></html>"
    return render_template_string(html)

# Start background image capture
threading.Thread(target=background_loop, daemon=True).start()
