import os
import time
import threading
from pathlib import Path
from datetime import datetime
import requests
from flask import Flask, render_template_string
from google.cloud import storage

# Configuration
CAMERA_CONFIG = {
    "bungalow1": "https://images.gov.im/webcams/bungalow1.jpg",
    "bungalow2": "https://images.gov.im/webcams/bungalow2.jpg",
    "bungalow3": "https://images.gov.im/webcams/bungalow3.jpg",
    "Douglasouterharbour": "https://images.gov.im/webcams/ed_tower.jpg",
    "DouglasProm": "https://images.gov.im/webcams/DTL_00001.jpg",
    "Peel": "https://images.gov.im/webcams/peel_00001.jpg",
    "PortErin": "https://images.gov.im/webcams/PortErin.jpg",
    "Castletown": "https://images.gov.im/webcams/Castletown_Bay.jpg",
    "Ramsey": "https://images.gov.im/webcams/Ramsey_00001.jpg",
}

BUCKET_NAME = os.environ.get("BUCKET_NAME")
REFRESH_INTERVAL = int(os.environ.get("INTERVAL_SECONDS", "60"))

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Referer": "https://images.gov.im/webcams/",
    "Accept": "image/jpeg,image/png,image/*;q=0.8"
}

storage_client = storage.Client()
bucket = storage_client.bucket(BUCKET_NAME)
app = Flask(__name__)

def upload_image_to_gcs(image_data, camera_name):
    date_prefix = datetime.utcnow().strftime("%Y%m%d")
    prefix = f"{camera_name}/{date_prefix}/"
    blobs = list(bucket.list_blobs(prefix=prefix))

    max_index = 0
    for blob in blobs:
        name = Path(blob.name).name
        if name.endswith(".jpg") and name[:-4].isdigit():
            max_index = max(max_index, int(name[:-4]))

    next_index = max_index + 1
    filename = f"{next_index:04d}.jpg"
    blob = bucket.blob(f"{prefix}{filename}")
    blob.upload_from_string(image_data, content_type='image/jpeg')
    blob.make_public()

    print(f"Uploaded {camera_name}/{date_prefix}/{filename}")

def fetch_and_upload(camera_name, image_url):
    while True:
        try:
            response = requests.get(image_url, headers=HEADERS)
            response.raise_for_status()
            if response.content:
                upload_image_to_gcs(response.content, camera_name)
            else:
                print(f"Empty image from {camera_name}")
        except Exception as e:
            print(f"Error with {camera_name}: {e}")
        time.sleep(REFRESH_INTERVAL)

@app.route("/")
def index():
    html = "<html><body><h1>Latest Images</h1>"
    for camera in CAMERA_CONFIG:
        prefix = f"{camera}/{datetime.utcnow().strftime('%Y%m%d')}/"
        blobs = list(bucket.list_blobs(prefix=prefix))
        blobs = sorted(blobs, key=lambda b: b.updated, reverse=True)[:1]
        for blob in blobs:
            url = f"https://storage.googleapis.com/{BUCKET_NAME}/{blob.name}"
            html += f"<h2>{camera}</h2><img src='{url}' width='320' /><br/>"
    html += "</body></html>"
    return render_template_string(html)

# Start one thread per camera
for name, url in CAMERA_CONFIG.items():
    threading.Thread(target=fetch_and_upload, args=(name, url), daemon=True).start()
