
# Fil: calibration.py
# Modul for kalibrering av porter – måling av åpne/lukketid, lagring og feilhåndtering

import time
from datetime import datetime
from config import load_config, save_config
from event_log import log_event

# Referanse til garage-controller (må settes i app.py eller ved init)
garage = None  # denne må settes utenfra

def calibrate_open(port, timeout=60):
    """Måler hvor lang tid det tar å åpne en port fra lukket posisjon."""
    log_event("calibration", f"Starter måling av åpnetid for {port}")
    duration = garage.maal_aapnetid(port, timeout=timeout)
    if duration is None:
        log_event("error", f"Åpning av {port} tok for lang tid (> {timeout}s)")
        return None
    log_event("calibration", f"Åpnetid for {port}: {round(duration,2)} sek")
    return round(duration, 2)

def calibrate_close(port, timeout=60):
    """Måler hvor lang tid det tar å lukke en port fra åpen posisjon."""
    log_event("calibration", f"Starter måling av lukketid for {port}")
    duration = garage.maal_lukketid(port, timeout=timeout)
    if duration is None:
        log_event("error", f"Lukking av {port} tok for lang tid (> {timeout}s)")
        return None
    log_event("calibration", f"Lukketid for {port}: {round(duration,2)} sek")
    return round(duration, 2)

def calibrate_full(port, timeout=60):
    """Måler både åpne- og lukketid for porten."""
    open_time = calibrate_open(port, timeout)
    if open_time is None:
        return None
    close_time = calibrate_close(port, timeout)
    if close_time is None:
        return None
    return {
        "open_time": open_time,
        "close_time": close_time
    }

def save_calibration(port, open_time=None, close_time=None, source="auto"):
    """Lagrer kalibreringsverdier til config.json med timestamp."""
    config = load_config()
    calibration_data = config.get("calibration", {}).get(port, {})
    now = datetime.now().isoformat(timespec="seconds")

    if open_time is not None:
        calibration_data["open_time"] = open_time
    if close_time is not None:
        calibration_data["close_time"] = close_time

    calibration_data["timestamp"] = now
    calibration_data["source"] = source

    config.setdefault("calibration", {})[port] = calibration_data
    save_config(config)
    log_event("calibration", f"Lagrer kalibreringsdata for {port}", data=calibration_data)
    return True
