
# Fil: calibration.py
# Modul for kalibrering av porter – måler åpne-/lukketid med detaljer, lagrer og logger

import time
from datetime import datetime
from config import load_config, save_config
from calibration_logger import log_calibration_result
from event_log import log_event

garage = None  # settes fra app.py

def calibrate(port, action="open"):
    """Hovedrutine for å kalibrere en port for åpning eller lukking."""
    config = load_config()
    max_time = config.get("calibration_max_seconds", 60)

    # 🔍 Bekreft starttilstand
    status = garage.get_port_status(port)
    if action == "open" and status == "åpen":
        log_event("calibration", f"Porten {port} er allerede åpen – kalibrering avbrutt")
        return None
    if action == "close" and status == "lukket":
        log_event("calibration", f"Porten {port} er allerede lukket – kalibrering avbrutt")
        return None
    if status == "sensorfeil":
        log_event("error", f"Sensorfeil på {port} – kalibrering umulig")
        return None
    if status == "ukjent":
        log_event("calibration", f"Portstatus for {port} er ukjent – kalibrering krever tydelig posisjon")
        return None

    # 📢 Varsel og puls
    log_event("calibration", f"Starter {action}-kalibrering for {port}")
    rele_start = time.time()
    garage.send_pulse(port)

    # ⏱️ Mål forsinkelse til første sensor går inaktiv
    start_sensor = "closed" if action == "open" else "open"
    end_sensor = "open" if action == "open" else "closed"
    max_limit = rele_start + max_time

    # Vent til start_sensor går fra aktiv → inaktiv
    while time.time() < max_limit:
        if not garage.read_sensor(port, start_sensor):  # sensor inaktiv = port begynner å bevege seg
            delay_done = time.time()
            break
        time.sleep(0.05)
    else:
        log_event("error", f"{action}-kalibrering: port {port} reagerte ikke på start innen {max_time} sek")
        return None

    rele_delay = round(delay_done - rele_start, 2)

    # ⏱️ Mål fra start_sensor inaktiv → end_sensor aktiv
    while time.time() < max_limit:
        if garage.read_sensor(port, end_sensor):  # sluttposisjon aktiv
            end_time = time.time()
            break
        time.sleep(0.05)
    else:
        log_event("error", f"{action}-kalibrering: port {port} nådde ikke {end_sensor} innen {max_time} sek")
        return None

    sensor_to_sensor = round(end_time - delay_done, 2)
    total = round(end_time - rele_start, 2)

    # 💾 Lagre i config.json
    key = "open" if action == "open" else "close"
    timestamp_key = f"timestamp_{key}"
    delay_key = f"{key}_delay"
    time_key = f"{key}_time"
    source_key = f"source_{key}"

    config.setdefault("calibration", {}).setdefault(port, {})
    config["calibration"][port][delay_key] = rele_delay
    config["calibration"][port][time_key] = sensor_to_sensor
    config["calibration"][port][timestamp_key] = datetime.now().isoformat()
    config["calibration"][port][source_key] = "kalibrert"
    save_config(config)

    # 🪵 Logg til historikk
    log_calibration_result(
        port=port,
        direction=key,
        rele_delay=rele_delay,
        sensor_to_sensor=sensor_to_sensor,
        total_time=total
    )

    log_event("calibration", f"{action.title()}-kalibrering fullført for {port}: delay {rele_delay}s + tid {sensor_to_sensor}s")
    return {
        "rele_delay": rele_delay,
        "sensor_to_sensor": sensor_to_sensor,
        "total_time": total
    }

def calibrate_open(port):
    return calibrate(port, action="open")

def calibrate_close(port):
    return calibrate(port, action="close")

def calibrate_full(port):
    """Utfører både åpne- og lukke-kalibrering for port."""
    result_open = calibrate_open(port)
    if not result_open:
        return None
    time.sleep(2)  # liten pause mellom åpne/lukke
    result_close = calibrate_close(port)
    if not result_close:
        return None

    return {
        "open": result_open,
        "close": result_close
    }

def save_calibration(port, open_time=None, close_time=None, source="manuell"):
    config = load_config()
    config.setdefault("calibration", {}).setdefault(port, {})

    timestamp = datetime.now().isoformat()

    if open_time is not None:
        config["calibration"][port]["open_time"] = open_time
        config["calibration"][port]["source_open"] = source
        config["calibration"][port]["timestamp_open"] = timestamp

    if close_time is not None:
        config["calibration"][port]["close_time"] = close_time
        config["calibration"][port]["source_close"] = source
        config["calibration"][port]["timestamp_close"] = timestamp

    save_config(config)
    log_event("calibration", f"{source.title()} kalibrering lagret for {port}")
