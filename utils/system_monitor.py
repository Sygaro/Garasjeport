import os
import time
import subprocess
import datetime
import psutil

from utils.config_loader import load_config
from config import config_paths as paths
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
        **get_system_time(),
        **get_uptime(),
        **get_app_uptime(),
        **get_cpu_temperature(),
        **get_disk_usage(),
        **get_memory_usage(),
        **get_cpu_load(),
        **get_pending_updates()
    }

def check_thresholds_and_log(status_data):
    """
    Sammenligner systemstatus mot grenseverdier i config_health.json.
    Logger advarsler hvis noen grenser overskrides.
    """
    try:
        config = load_config(paths.CONFIG_HEALTH_PATH)
        thresholds = config.get("thresholds", {})
        alerts = config.get("alerts", {})
        log_warn = alerts.get("log_warning", True)

        warnings = []

        if status_data["cpu_temp_c"] and status_data["cpu_temp_c"] > thresholds.get("cpu_temp_max", 80):
            warnings.append(f"CPU temp høy: {status_data['cpu_temp_c']}°C")

        if status_data["percent_used"] > thresholds.get("disk_usage_max_percent", 90):
            warnings.append(f"Diskbruk høy: {status_data['percent_used']}%")

        if status_data["free_gb"] < thresholds.get("min_free_disk_gb", 1.0):
            warnings.append(f"Lite ledig diskplass: {status_data['free_gb']} GB")

        if status_data["percent_used_mem"] > thresholds.get("memory_usage_max_percent", 85):
            warnings.append(f"Minnebruk høy: {status_data['percent_used_mem']}%")

        if status_data["free_mb"] < thresholds.get("min_free_memory_mb", 128):
            warnings.append(f"Lite ledig minne: {status_data['free_mb']} MB")

        if log_warn and warnings:
            for w in warnings:
                logger.log_warning("system_monitor", w)

        return warnings

    except Exception as e:
        logger.log_error("system_monitor", f"Feil ved terskelsjekk: {e}")
        return []
