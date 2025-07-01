import os
import requests
from datetime import datetime, timedelta
from pathlib import Path

# Config
IMAGE_URL = os.environ.get("IMAGE_URL")
BASE_DIR = Path("/data/images")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Referer": "https://images.gov.im/webcams/",
    "Accept": "image/jpeg,image/png,image/*;q=0.8"
}

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
    response = requests.get(IMAGE_URL, headers=HEADERS)
    response.raise_for_status()
    dest_file.write_bytes(response.content)
    print(f"✅ Downloaded: {dest_file}")

def rename_images_sequentially(folder):
    images = sorted(folder.glob("*.jpg"), key=lambda f: f.stat().st_mtime)
    for idx, img in enumerate(images):
        new_name = folder / f"{idx:04d}.jpg"
        if img.name != new_name.name:
            img.rename(new_name)

def process_images():
    today = datetime.utcnow().strftime("%m%d%Y")
    yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%m%d%Y")

    today_path = BASE_DIR / today
    yesterday_path = BASE_DIR / yesterday

    for path in [today_path, yesterday_path]:
        create_folder(path)
        remove_empty_jpgs(path)

    download_image(today_path)
    rename_images_sequentially(today_path)
    rename_images_sequentially(yesterday_path)

if __name__ == "__main__":
    process_images()
