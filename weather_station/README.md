# Plant Photo Station

Designed for **offline use** (e.g. orchards without WiFi): the device takes photos on a schedule and records BME280 climate data locally. Data is copied out via **USB**; after a successful copy, the Pi’s local data is cleared to save space.

## Hardware

- Raspberry Pi 5
- Raspberry Pi Camera (libcamera)
- PiicoDev BME280 atmospheric sensor

## Features

1. **Custom schedule and number of photos**
   - Set `photo_times` in `config.json` (e.g. `["08:00","14:00","20:00"]`) for daily capture times, or
   - Set `photos_per_day` (e.g. `3`) and the app will spread that many shots evenly from 6:00.
2. **USB data copy**
   - When a USB drive is inserted, the following are copied to `orchard_data_YYYYMMDD_HHMM/` on the drive:
     - `data/` — climate log CSV
     - `images/` — captured photos
     - `log.txt` — run log (backup)
     - `config.json` — current config (backup)
   - In the drive root you also get `REPORT_YYYYMMDD_HHMM.txt` and `STATUS.txt` (success/failure summary).
   - On **success**: file counts are checked and synced to disk, then files in `data/` and `images/` on the Pi are removed. On **failure**: nothing is deleted on the Pi.
3. **Copy result feedback**
   - **Success**: onboard **green** LED blinks 3 times; `STATUS.txt` in the drive root says “Copy successful” and a short message.
   - **Failure**: onboard **red** LED blinks 3 times; `STATUS.txt` says “Copy failed” and the error message.

## Configuration: `config.json`

```json
{
  "enabled": true,
  "photos_per_day": 3,
  "photo_times": ["08:00", "14:00", "20:00"]
}
```

- `enabled`: Turn scheduled capture on or off (`true` / `false`).
- `photo_times`: List of daily capture times in `"HH:MM"` format. If set, this overrides `photos_per_day`.
- `photos_per_day`: When `photo_times` is not set, this many shots are spread evenly from 6:00 (e.g. 3 → about 6:00, 14:00, 22:00).
- Legacy single-time config is still supported: `photo_hour` and `photo_minute` (e.g. 8:00).

**Updating config via USB**: Put a `config.json` in the root of the USB drive; after insertion the app will sync it to the device.

## Install dependencies (first run on the Pi)

Install the PiicoDev BME280 driver (`piicodev`):

```bash
cd ~/weather_station
source venv/bin/activate   # if using a venv
pip install -r requirements.txt
```

Or: `pip install piicodev`

## Run

```bash
cd ~/weather_station
source venv/bin/activate   # if using a venv
python main.py
```

Use systemd or crontab to start the app at boot so it keeps running without WiFi.

## Directory layout

- `data/` — climate log CSV
- `images/` — captured photos
- `config.json` — local config (can be overwritten from USB)
- `log.txt` — run log

## Offline use

The app does not use the network: config and data are local or handled via USB, so it works in places with no WiFi.
