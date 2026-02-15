"""
Local photo capture, no network dependency, suitable for orchards without WiFi.
Raspberry Pi Camera (libcamera / rpicam-still)。
"""
import os
import subprocess
from datetime import datetime

# Default save to images directory in project (can be overridden by caller)
def take_photo(images_dir=None):
    if images_dir is None:
        images_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "images")
    os.makedirs(images_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(images_dir, f"{timestamp}.jpg")
    # Use absolute path, no dependency on current working directory or network
    subprocess.run(["rpicam-still", "-o", filename], check=False, timeout=30)
    return filename if os.path.isfile(filename) else None
