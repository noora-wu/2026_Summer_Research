"""
USB copy and cleanup: copy data to USB drive without WiFi, delete local data after successful copy.
Show success/failure via LED and STATUS.txt in USB root.
Copy result shown via LED and STATUS.txt in USB root (success/failure).
"""
import os
import shutil
from datetime import datetime
from .led_feedback import led_busy_trigger

# Common Raspberry Pi USB mount points (user copies data via USB when no WiFi)
def _usb_base_paths():
    candidates = ["/media/pi", "/media/noora"]
    if "USER" in os.environ:
        candidates.append(os.path.join("/media", os.environ["USER"]))
    for p in candidates:
        if os.path.exists(p):
            yield p
    if os.path.exists("/media"):
        for name in os.listdir("/media"):
            path = os.path.join("/media", name)
            if os.path.isdir(path) and not name.startswith("."):
                yield path

def get_usb_path():
    """Return path of current inserted USB drive (first available mount point), or None if no USB"""
    for base in _usb_base_paths():
        try:
            devices = [d for d in os.listdir(base) if not d.startswith(".")]
            if devices:
                return os.path.join(base, devices[0])
        except (OSError, PermissionError):
            continue
    return None

def sync_usb_config(usb_path, local_config_path):
    """If USB root has config.json, overwrite local config (user can plug USB to change settings)"""
    usb_config = os.path.join(usb_path, "config.json")
    if os.path.exists(usb_config):
        try:
            shutil.copy(usb_config, local_config_path)
            return True
        except Exception:
            return False
    return False

def _count_files(folder):
    if not os.path.isdir(folder):
        return 0
    return sum(1 for _ in os.listdir(folder) if os.path.isfile(os.path.join(folder, _)))

def _write_status(usb_path, success, message):
    """Write STATUS.txt in USB root for user to see success/failure after copy"""
    path = os.path.join(usb_path, "STATUS.txt")
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write("Copy successful\n" if success else "Copy failed\n")
            f.write(message)
        f.flush()
        os.sync() if hasattr(os, "sync") else None
    except Exception:
        pass

def _copy_file(src, dest_path, led_trigger=None):
    """Copy single file to target path, ensure target directory exists"""
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    shutil.copy2(src, dest_path)
    if led_trigger:
        led_trigger()

def transfer_and_clean(usb_path, data_dir, image_dir, config_file=None, system_log=None):
    """
    Copy data, images, and (if provided) config.json, log.txt to USB target path,
    then delete files in data/images on Pi after successful verification.
    Use provided usb_path to ensure writes to correct device.
    Return (success, message).
    """
    if not usb_path or not os.path.isdir(usb_path):
        return False, "Invalid USB path"

    # Check USB is writable (create test file in root)
    try:
        test_file = os.path.join(usb_path, ".write_test_plant_station")
        with open(test_file, "w") as f:
            f.write("1")
        os.remove(test_file)
    except Exception as e:
        return False, f"USB is not writable: {e}"

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    target_folder = os.path.join(usb_path, f"orchard_data_{timestamp}")
    report_path = os.path.join(usb_path, f"REPORT_{timestamp}.txt")

    n_data = _count_files(data_dir)
    n_images = _count_files(image_dir)

    try:
        os.makedirs(target_folder, exist_ok=True)
        dest_data = os.path.join(target_folder, "data")
        dest_images = os.path.join(target_folder, "images")
        os.makedirs(dest_data, exist_ok=True)
        os.makedirs(dest_images, exist_ok=True)

        # 1) Copy all files in data directory
        for f in os.listdir(data_dir):
            src = os.path.join(data_dir, f)
            if os.path.isfile(src):
                dest = os.path.join(dest_data, f)
                shutil.copy2(src, dest)
                led_busy_trigger()

        # 2) Copy all files in images directory
        for f in os.listdir(image_dir):
            src = os.path.join(image_dir, f)
            if os.path.isfile(src):
                dest = os.path.join(dest_images, f)
                shutil.copy2(src, dest)
                led_busy_trigger()

        # 3) Copy log.txt and config.json (for easy viewing on computer)
        if system_log and os.path.isfile(system_log):
            shutil.copy2(system_log, os.path.join(target_folder, "log.txt"))
            led_busy_trigger()
        if config_file and os.path.isfile(config_file):
            shutil.copy2(config_file, os.path.join(target_folder, "config.json"))
            led_busy_trigger()

        # Ensure writes are committed to USB before verification
        if hasattr(os, "sync"):
            os.sync()

        # Verify: only delete local files if data/images counts match
        n_data_dest = _count_files(dest_data)
        n_images_dest = _count_files(dest_images)
        if n_data_dest != n_data or n_images_dest != n_images:
            _write_status(usb_path, False, f"Verification failed: data {n_data_dest}/{n_data}, images {n_images_dest}/{n_images}")
            return False, "Verification failed, local data not deleted"

        # Verification passed, delete files in data/images on Pi
        for folder in [data_dir, image_dir]:
            for f in os.listdir(folder):
                fp = os.path.join(folder, f)
                if os.path.isfile(fp):
                    os.remove(fp)

        msg = f"Copied {n_data} data files, {n_images} image files; backed up log.txt and config.json. Local data/images cleared."
        with open(report_path, "w", encoding="utf-8") as r:
            r.write(f"Transfer Successful\nTime: {datetime.now()}\n{msg}\n")
        _write_status(usb_path, True, msg)
        if hasattr(os, "sync"):
            os.sync()
        return True, msg

    except Exception as e:
        err_msg = str(e)
        try:
            with open(report_path, "w", encoding="utf-8") as r:
                r.write(f"Transfer Failed\nError: {err_msg}\n")
            _write_status(usb_path, False, f"Error: {err_msg}")
        except Exception:
            pass
        return False, err_msg
