import time
import os

ACT_LED = "/sys/class/leds/ACT/brightness"   # Green ACT
PWR_LED = "/sys/class/leds/PWR/brightness"   # Red PWR (used for copy failure)

def _on_pi():
    return os.path.exists(os.path.dirname(ACT_LED))

def _pwr_available():
    return os.path.exists(os.path.dirname(PWR_LED))

def _set_led(path, state):
    if not os.path.exists(os.path.dirname(path)):
        return
    os.system(f"echo {state} | sudo tee {path} > /dev/null 2>&1")

def set_led(state):
    """Control green ACT LED (backwards compatibility)."""
    if not _on_pi():
        return
    _set_led(ACT_LED, state)

def led_success():
    """Success: green LED flashes 3 times"""
    if not _on_pi():
        return
    for _ in range(3):
        _set_led(ACT_LED, 1)
        time.sleep(0.2)
        _set_led(ACT_LED, 0)
        time.sleep(0.2)

def led_error():
    """Failure: red LED flashes 3 times; if no PWR, use green"""
    if _pwr_available():
        for _ in range(3):
            _set_led(PWR_LED, 1)
            time.sleep(0.2)
            _set_led(PWR_LED, 0)
            time.sleep(0.2)
    else:
        # No red LED, fallback to green flashes
        if _on_pi():
            for _ in range(3):
                _set_led(ACT_LED, 1)
                time.sleep(0.2)
                _set_led(ACT_LED, 0)
                time.sleep(0.2)

def led_busy_trigger():
    if not _on_pi():
        return
    try:
        with open(ACT_LED, "r") as f:
            state = f.read().strip()
        new_state = "0" if state in ("1", "255") else "1"
        set_led(int(new_state))
    except (OSError, ValueError):
        set_led(1)