import os
import threading
import time
from datetime import datetime
from pathlib import Path
import requests
from flask import Flask, render_template_string
from google.cloud import storage

# Environment Variables
CAMERA_CONFIG = [
    {"name": "bungalow1", "url": "https://images.gov.im/webcams/bungalow1.jpg"},
    {"name": "bungalow2", "url": "https://images.gov.im/webcams/bungalow2.jpg"},
    {"name": "bungalow3", "url": "https://images.gov.im/webcams/bungalow3.jpg"},
    {"name": "ed_tower",  "url": "https://images.gov.im/webcams/ed_tower.jpg"},
    {"name": "douglasprom", "url": "https://images.gov.im/webcams/DTL_00001.jpg"},
    {"name": "peel", "url": "https://images.gov.im/webcams/peel_00001.jpg"},
    {"name": "porterin", "url": "https://images.gov.im/webcams/PortErin.jpg"},
    {"name": "castletown", "url": "https://images.gov.im/webcams/Castletown_Bay.jpg"},
    {"name": "ramsey", "url": "https://images.gov.im/webcams/Ramsey_00001.jpg"},
    # Add or remove as needed
]

BUCKET_NAME = os.environ.get("BUCKET_NAME")
REFRESH_INTERVAL = int(os.environ.get("INTERVAL_SECONDS", "60"))

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Referer": "https://images.gov.im/webcams/",
    "Accept": "image/jpeg,image/png,image/*;q=0.8"
}

storage_client = storage.Client()
bucket = storage_client.bucket(BUCKET_NAME)

app = Flask(__name__)


def is_valid_jpeg(content: bytes) -> bool:
    return content.startswith(b'\xff\xd8') and content.endswith(b'\xff\xd9')


def download_image_with_validation(url: str) -> bytes | None:
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        content = response.content
        if not content or not is_valid_jpeg(content):
            print(f"Invalid or empty image from {url}, skipping.")
            return None
        return content
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None


def upload_image_to_gcs(image_data: bytes, camera: str):
    date_prefix = datetime.utcnow().strftime("%Y%m%d")
    prefix = f"{camera}/{date_prefix}/"
    blobs = list(bucket.list_blobs(prefix=prefix))

    # Find the next sequential index
    max_index = 0
    for blob in blobs:
        filename = Path(blob.name).name
        if filename.endswith(".jpg") and filename[:-4].isdigit():
            max_index = max(max_index, int(filename[:-4]))

    next_index = max_index + 1
    filename = f"{next_index:04d}.jpg"
    blob = bucket.blob(f"{prefix}{filename}")
    blob.upload_from_string(image_data, content_type="image/jpeg")
    blob.make_public()

    print(f"Uploaded {prefix}{filename} to GCS")


def process_camera(camera: dict):
    image_data = download_image_with_validation(camera["url"])
    if image_data:
        upload_image_to_gcs(image_data, camera["name"])


def loop_fetch_all_cameras():
    while True:
        threads = []
        for cam in CAMERA_CONFIG:
            t = threading.Thread(target=process_camera, args=(cam,))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
        time.sleep(REFRESH_INTERVAL)


@app.route("/")
def index():
    date_prefix = datetime.utcnow().strftime("%Y%m%d")
    img_tags = ""
    for cam in CAMERA_CONFIG:
        blobs = list(bucket.list_blobs(prefix=f"{cam['name']}/{date_prefix}/"))
        blobs = sorted(blobs, key=lambda b: b.updated, reverse=True)[:1]
        for blob in blobs:
            url = f"https://storage.googleapis.com/{BUCKET_NAME}/{blob.name}"
            img_tags += f"<h3>{cam['name']}</h3><img src='{url}' width='320' /><br/>"
    return render_template_string(f"<html><body><h1>Latest Camera Images</h1>{img_tags}</body></html>")


# Start background thread
threading.Thread(target=loop_fetch_all_cameras, daemon=True).start()
