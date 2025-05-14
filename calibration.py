
# Fil: calibration.py
# Modul for kalibrering av porter – måling av åpne/lukketid, lagring og feilhåndtering

# Referanse til garage-controller (må settes i app.py eller ved init)
garage = None  # denne må settes utenfra

import time
from datetime import datetime
from config import load_config, save_config
from event_log import log_event
from calibration_logger import log_calibration_measurement



def calibrate_open(port, timeout=60):
    from time import time, sleep

    log_event("calibration", f"Starter kalibrering av åpning for {port}", port=port)
    start_pulse = time()
    garage.send_pulse(port)  # Rele aktiveres

    # Mål tid til "closed"-sensor går fra aktiv → inaktiv
    delay_start = time()
    delay_timeout = delay_start + timeout
    while time() < delay_timeout:
        if garage.read_sensor(port, "closed") == 0:
            delay_duration = time() - start_pulse
            break
        sleep(0.01)
    else:
        log_event("error", f"Releforsinkelse for {port} overskredet", port=port)
        return None

    # Nå venter vi på at "open" sensor skal bli aktiv
    sensor_start = time()
    sensor_timeout = sensor_start + timeout
    while time() < sensor_timeout:
        if garage.read_sensor(port, "open") == 1:
            sensor_duration = time() - delay_start
            total_duration = delay_duration + sensor_duration
            log_event("calibration", f"Åpningstid for {port}: {total_duration:.2f}s", port=port)
            log_calibration_measurement(
                port=port,
                action_type="open",
                rele_delay=delay_duration,
                sensor_transition=sensor_duration,
                total_time=total_duration
            )
            return round(total_duration, 2)
        sleep(0.01)

    log_event("error", f"Åpning av {port} feilet – sensor ikke aktivert", port=port)
    return None


def calibrate_close(port, timeout=60):
    from time import time, sleep

    log_event("calibration", f"Starter kalibrering av lukking for {port}", port=port)
    start_pulse = time()
    garage.send_pulse(port)

    # Mål tid til "open"-sensor går fra aktiv → inaktiv
    delay_start = time()
    delay_timeout = delay_start + timeout
    while time() < delay_timeout:
        if garage.read_sensor(port, "open") == 0:
            delay_duration = time() - start_pulse
            break
        sleep(0.01)
    else:
        log_event("error", f"Releforsinkelse for {port} ved lukking overskredet", port=port)
        return None

    # Nå venter vi på at "closed" sensor blir aktiv
    sensor_start = time()
    sensor_timeout = sensor_start + timeout
    while time() < sensor_timeout:
        if garage.read_sensor(port, "closed") == 1:
            sensor_duration = time() - delay_start
            total_duration = delay_duration + sensor_duration
            log_event("calibration", f"Lukketid for {port}: {total_duration:.2f}s", port=port)
            log_calibration_measurement(
                port=port,
                action_type="close",
                rele_delay=delay_duration,
                sensor_transition=sensor_duration,
                total_time=total_duration
            )
            return round(total_duration, 2)
        sleep(0.01)

    log_event("error", f"Lukking av {port} feilet – sensor ikke aktivert", port=port)
    return None



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
