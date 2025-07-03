import os
import threading
import time
import requests
from datetime import datetime
from pathlib import Path
from flask import Flask, send_from_directory, render_template_string


IMAGE_URL = os.environ.get("IMAGE_URL", "https://images.gov.im/webcams/bungalow1.jpg")
BASE_DIR = Path("/data/images")
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Referer": "https://images.gov.im/webcams/",
    "Accept": "image/jpeg,image/png,image/*;q=0.8"
}

app = Flask(__name__)

def create_folder(path):
    path.mkdir(parents=True, exist_ok=True)

def remove_empty_jpgs(path):
    for f in path.glob("*.jpg"):
        if f.stat().st_size == 0:
            f.unlink()

def download_image(dest_folder):
    now = datetime.utcnow()
    filename = now.strftime("%m%d%Y%H%M%S") + ".jpg"
    dest_file = dest_folder / filename
    try:
        response = requests.get(IMAGE_URL, headers=HEADERS)
        response.raise_for_status()
        dest_file.write_bytes(response.content)
        print(f"Downloaded: {dest_file}")
    except Exception as e:
        print(f"Download error: {e}")

def rename_images_sequentially(folder):
    images = sorted(folder.glob("*.jpg"), key=lambda f: f.stat().st_mtime)
    for idx, img in enumerate(images):
        new_name = folder / f"{idx:04d}.jpg"
        if img.name != new_name.name:
            img.rename(new_name)

def process_images():
    today = datetime.utcnow().strftime("%m%d%Y")
    today_path = BASE_DIR / today
    create_folder(today_path)
    remove_empty_jpgs(today_path)
    download_image(today_path)
    rename_images_sequentially(today_path)

def run_downloader_loop():
    while True:
        process_images()
        time.sleep(60)

@app.route("/")
def index():
    today = datetime.utcnow().strftime("%m%d%Y")
    today_path = BASE_DIR / today
    if not today_path.exists():
        return "No images yet."
    images = sorted(today_path.glob("*.jpg"), key=os.path.getmtime)[-5:]
    image_tags = "\n".join([f"<img src='/images/{today}/{img.name}' width='320' />" for img in images])
    return render_template_string(f"<html><body><h1>Latest Images</h1>{image_tags}</body></html>")

@app.route("/images/<date>/<filename>")
def serve_image(date, filename):
    return send_from_directory(BASE_DIR / date, filename)

threading.Thread(target=run_downloader_loop, daemon=True).start()
