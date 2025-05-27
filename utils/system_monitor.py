import os
import time
import subprocess
import datetime
import psutil

from utils.config_loader import load_config
from config import config_paths
from utils.garage_logger import GarageLogger

logger = GarageLogger()

APP_START_TIME = time.time()

def get_uptime():
    uptime_seconds = time.time() - psutil.boot_time()
    return {
        "uptime_seconds": int(uptime_seconds),
        "uptime_human": str(datetime.timedelta(seconds=int(uptime_seconds)))
    }

def get_app_uptime():
    elapsed = time.time() - APP_START_TIME
    return {
        "app_uptime_seconds": int(elapsed),
        "app_uptime_human": str(datetime.timedelta(seconds=int(elapsed)))
    }

def get_system_time():
    return {
        "current_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def get_cpu_temperature():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp = int(f.read()) / 1000.0
            return {"cpu_temp_c": round(temp, 1)}
    except FileNotFoundError:
        return {"cpu_temp_c": None}

def get_disk_usage(path="/"):
    usage = psutil.disk_usage(path)
    return {
        "total_gb": round(usage.total / (1024**3), 2),
        "used_gb": round(usage.used / (1024**3), 2),
        "free_gb": round(usage.free / (1024**3), 2),
        "percent_used": usage.percent
    }

def get_memory_usage():
    mem = psutil.virtual_memory()
    return {
        "total_mb": round(mem.total / (1024**2), 1),
        "used_mb": round(mem.used / (1024**2), 1),
        "free_mb": round(mem.available / (1024**2), 1),
        "percent_used_mem": mem.percent
    }

def get_cpu_load():
    load1, load5, load15 = os.getloadavg()
    return {
        "load_1min": round(load1, 2),
        "load_5min": round(load5, 2),
        "load_15min": round(load15, 2)
    }

def get_pending_updates():
    try:
        result = subprocess.run(["apt", "list", "--upgradeable"], capture_output=True, text=True)
        lines = result.stdout.strip().splitlines()
        upgradeable = [line for line in lines if "/" in line and "Listing..." not in line]
        return {"pending_updates": len(upgradeable)}
    except Exception as e:
        return {"pending_updates": None, "error": str(e)}

def get_system_status():
    return {
        "system": {
            **get_system_time(),
            **get_uptime(),
        },
        "app": {
            **get_app_uptime(),
        },
        "cpu": {
            **get_cpu_temperature(),
            **get_cpu_load(),
        },
        "memory": {
            **get_memory_usage(),
        },
        "disk": {
            **get_disk_usage(),
        },
        "updates": {
            **get_pending_updates(),
        }
    }


def check_thresholds_and_log(status_data):
    config = load_config(config_paths.CONFIG_HEALTH_PATH)
    warnings = []

    # CPU temp
    max_cpu_temp = config.get("cpu_temp_max", 70)
    cpu_temp = status_data.get("cpu_temp_c")
    if cpu_temp is not None and cpu_temp > max_cpu_temp:
        msg = f"CPU-temperatur {cpu_temp}°C overstiger terskel {max_cpu_temp}°C"
        warnings.append(msg)
        logger.log_warning("health", msg)

    # Disk
    disk_usage = status_data.get("percent_used")
    max_disk = config.get("disk_percent_used_max", 85)
    if disk_usage is not None and disk_usage > max_disk:
        msg = f"Diskbruk {disk_usage}% overstiger grense på {max_disk}%"
        warnings.append(msg)
        logger.log_warning("health", msg)

    # Memory
    mem_usage = status_data.get("percent_used_mem")
    max_mem = config.get("memory_percent_used_max", 85)
    if mem_usage is not None and mem_usage > max_mem:
        msg = f"Minnebruk {mem_usage}% overstiger grense på {max_mem}%"
        warnings.append(msg)
        logger.log_warning("health", msg)

    # CPU load
    load_1min = status_data.get("load_1min", 0)
    max_load = config.get("max_load_avg", 1.0)
    if load_1min > max_load:
        msg = f"CPU load 1min er {load_1min} som overstiger terskel {max_load}"
        warnings.append(msg)
        logger.log_warning("health", msg)

    # Updates
    pending = status_data.get("pending_updates", 0)
    if config.get("warn_if_pending_updates", True) and pending > 0:
        msg = f"{pending} systemoppdateringer tilgjengelig"
        warnings.append(msg)
        logger.log_warning("health", msg)

    return warnings



def run_system_health_check():
    """
    Sjekker status for pigpiod, GPIO og sensor-monitor.
    Returnerer et resultat med boolske helsesjekker.
    """
    checks = {
        "pigpiod": False,
        "gpio_ready": False,
        "sensor_monitor": True  # Foreløpig statisk, evt. utvides
    }

    # Sjekk pigpiod kjører
    try:
        result = subprocess.run(["pgrep", "pigpiod"], stdout=subprocess.PIPE)
        checks["pigpiod"] = result.returncode == 0
    except Exception:
        checks["pigpiod"] = False

    # Sjekk GPIO (pigpio tilgjengelig)
    try:
        import pigpio
        pi = pigpio.pi()
        checks["gpio_ready"] = pi.connected
        pi.stop()
    except Exception:
        checks["gpio_ready"] = False

    # Beregn samlet systemstatus
    system_ok = all(checks.values())
    return {
        "checks": checks,
        "system_ok": system_ok
    }



def get_diagnostics(status_data):
    """
    Går gjennom systemstatus og vurderer den opp mot terskelverdier fra config_health.json.
    Returnerer en liste med menneskelesbare vurderinger, både varsler og bekreftelser.
    Forventer at status_data er strukturert med grupperte nøkler (f.eks. status_data['cpu']['cpu_temp_c']).
    """

    config = load_config(config_paths.CONFIG_HEALTH_PATH)
    thresholds = config.get("thresholds", {})

    diagnostics = []

    # --- CPU-temperatur ---
    cpu_temp = status_data.get("cpu", {}).get("cpu_temp_c")
    if cpu_temp is not None:
        max_temp = thresholds.get("cpu_temp_max", 70)
        if cpu_temp > max_temp:
            diagnostics.append(f"CPU-temperatur {cpu_temp}°C overstiger terskel {max_temp}°C")
        else:
            diagnostics.append(f"CPU-temperatur {cpu_temp}°C under terskel {max_temp}°C")

    # --- Minnebruk (i prosent) ---
    mem_percent = status_data.get("memory", {}).get("percent_used_mem")
    if mem_percent is not None:
        max_mem = thresholds.get("memory_usage_max_percent", 85)
        if mem_percent > max_mem:
            diagnostics.append(f"Minnebruk {mem_percent}% overstiger grense på {max_mem}%")
        else:
            diagnostics.append(f"Minnebruk {mem_percent}% under terskel {max_mem}%")

    # --- Diskbruk (i prosent) ---
    disk_used = status_data.get("disk", {}).get("percent_used")
    if disk_used is not None:
        max_disk = thresholds.get("disk_usage_max_percent", 90)
        if disk_used > max_disk:
            diagnostics.append(f"Diskbruk {disk_used}% overstiger grense på {max_disk}%")
        else:
            diagnostics.append(f"Diskbruk {disk_used}% under terskel {max_disk}%")

    # --- Ledig diskplass (i GB) ---
    free_disk = status_data.get("disk", {}).get("free_gb")
    if free_disk is not None:
        min_free_disk = thresholds.get("min_free_disk_gb", 2.0)
        if free_disk < min_free_disk:
            diagnostics.append(f"Ledig diskplass {free_disk} GB er under minimum {min_free_disk} GB")
        else:
            diagnostics.append(f"{free_disk} GB ledig diskplass – over minimum {min_free_disk} GB")

    # --- Ledig minne (i MB) ---
    free_mem = status_data.get("memory", {}).get("free_mb")
    if free_mem is not None:
        min_free_mem = thresholds.get("min_free_memory_mb", 100)
        if free_mem < min_free_mem:
            diagnostics.append(f"Ledig minne {free_mem} MB er under minimum {min_free_mem} MB")
        else:
            diagnostics.append(f"{free_mem} MB ledig minne – over minimum {min_free_mem} MB")

    # --- Systemoppdateringer tilgjengelig ---
    updates = status_data.get("updates", {}).get("pending_updates")
    if updates is not None:
        if updates > 0:
            diagnostics.append(f"{updates} systemoppdateringer tilgjengelig")
        else:
            diagnostics.append("Ingen kritiske systemoppdateringer tilgjengelig")

    return diagnostics
