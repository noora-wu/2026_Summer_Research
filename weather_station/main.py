# main.py
# Plant photo station – runs fully offline (e.g. orchards without WiFi), local + USB copy.
import os
import csv
import json
import time
import datetime
import shutil

from sensors.climate import read_climate
from camera.capture import take_photo
from usb.usb_transfer import get_usb_path, transfer_and_clean, sync_usb_config
from usb.led_feedback import led_success, led_error, set_led

# -------------------- Paths and config --------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
IMAGES_DIR = os.path.join(BASE_DIR, "images")
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
CLIMATE_LOG = os.path.join(DATA_DIR, "climate_log.csv")
SYSTEM_LOG = os.path.join(BASE_DIR, "log.txt")

for folder in [DATA_DIR, IMAGES_DIR]:
    os.makedirs(folder, exist_ok=True)

# -------------------- Helpers --------------------
def write_log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(SYSTEM_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(f"[{timestamp}] {message}")

def load_config():
    """Load config from disk (works offline; user can update by placing config.json on USB)."""
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        write_log(f"Error loading config: {e}")
        return default_config()

def default_config():
    return {
        "enabled": True,
        "photos_per_day": 1,
        "photo_times": ["08:00"],
        "photo_hour": 8,
        "photo_minute": 0,
    }

def get_schedule_times(config):
    """
    Return list of (hour, minute) for today’s captures.
    Prefer photo_times (user-defined); else spread photos_per_day from 6:00.
    Legacy single time: photo_hour / photo_minute.
    """
    # 1) Explicit multiple times
    times = config.get("photo_times")
    if times and isinstance(times, list) and len(times) > 0:
        result = []
        for t in times:
            if isinstance(t, str) and ":" in t:
                parts = t.strip().split(":")
                try:
                    h, m = int(parts[0]), int(parts[1]) if len(parts) > 1 else 0
                    if 0 <= h <= 23 and 0 <= m <= 59:
                        result.append((h, m))
                except (ValueError, IndexError):
                    continue
        if result:
            return sorted(set(result))
    # 2) Legacy single time
    if "photo_hour" in config:
        try:
            h = int(config["photo_hour"])
            m = int(config.get("photo_minute", 0))
            if 0 <= h <= 23 and 0 <= m <= 59:
                return [(h, m)]
        except (TypeError, ValueError):
            pass
    # 3) Spread photos_per_day evenly from 6:00
    n = config.get("photos_per_day", 1)
    n = max(1, min(n, 48))
    start_minutes = 6 * 60   # 6:00
    day_minutes = 24 * 60
    interval = day_minutes // n
    result = []
    for i in range(n):
        m = (start_minutes + i * interval) % day_minutes
        result.append((m // 60, m % 60))
    return sorted(set(result))

def log_data_to_csv(image_file, climate_data):
    file_exists = os.path.isfile(CLIMATE_LOG)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(CLIMATE_LOG, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["timestamp", "temperature", "pressure", "humidity", "image_path"])
        writer.writerow([
            timestamp,
            climate_data["temperature"],
            climate_data["pressure"],
            climate_data["humidity"],
            image_file,
        ])

# -------------------- Core task --------------------
def run_capture_task():
    write_log("Starting scheduled capture task...")
    try:
        climate_data = read_climate()
        image_path = take_photo(IMAGES_DIR)
        if image_path:
            log_data_to_csv(os.path.basename(image_path), climate_data)
            write_log(f"Task success: {climate_data['temperature']}°C, Image: {image_path}")
        else:
            write_log("Task failed: Camera capture returned None")
    except Exception as e:
        write_log(f"Critical error in run_capture_task: {e}")

# -------------------- Main loop --------------------
def main():
    write_log("Plant photo station started (offline-friendly, USB copy supported).")
    # Track (date, hour, minute) already run to avoid duplicate in same minute
    run_done = set()
    usb_processed = False
    last_schedule_log = None  # Log schedule at most once per minute for debugging

    while True:
        config = load_config()
        now = datetime.datetime.now()
        today = now.date()

        # Scheduled capture (no network required)
        if config.get("enabled", True):
            schedule = get_schedule_times(config)
            # Log current time and schedule once per minute to verify alignment
            schedule_log_key = (today, now.hour, now.minute)
            if schedule_log_key != last_schedule_log:
                last_schedule_log = schedule_log_key
                times_str = ", ".join(f"{h:02d}:{m:02d}" for h, m in schedule)
                write_log(f"Current time {now.strftime('%H:%M')}, scheduled at: {times_str}")
            for h, m in schedule:
                if now.hour == h and now.minute == m:
                    key = (today, h, m)
                    if key not in run_done:
                        run_capture_task()
                        run_done.add(key)
        # Clear run_done at midnight (keep only today)
        if run_done and min(r[0] for r in run_done) < today:
            run_done = {(d, h, m) for d, h, m in run_done if d == today}

        # USB: detect drive, sync config, copy data and clean local; show success/failure
        usb_path = get_usb_path()
        if usb_path and not usb_processed:
            write_log(f"USB detected at {usb_path}")
            if sync_usb_config(usb_path, CONFIG_FILE):
                write_log("Config updated from USB.")
            success, message = transfer_and_clean(
                usb_path, DATA_DIR, IMAGES_DIR,
                config_file=CONFIG_FILE, system_log=SYSTEM_LOG
            )
            if success:
                write_log(f"USB transfer successful: {message}")
                led_success()
            else:
                write_log(f"USB transfer failed: {message}")
                led_error()
            usb_processed = True
        elif not usb_path:
            if usb_processed:
                write_log("USB removed.")
            usb_processed = False

        # Check every 5 seconds to reduce chance of missing the minute
        time.sleep(5)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        write_log("System stopped by user.")
        set_led(0)
    except Exception as e:
        write_log(f"System crashed: {e}")
        set_led(0)
