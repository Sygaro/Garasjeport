from flask import Blueprint, render_template, request, redirect, flash, url_for
from core.config_manager import ConfigManager
from utils.gpio_utils import get_gpio_info  # egen fil, se neste punkt
import datetime

port_routes = Blueprint("port_routes", __name__)
config_manager = ConfigManager()

@port_routes.route("/admin/ports", methods=["GET"])
def show_ports():
    gpio_config = config_manager.get_module("gpio")
    calibration_config = config_manager.get_module("system").get("calibration", {})

    gpio_data = get_gpio_info(gpio_config)
    merged_config = {
        "relay_pins": gpio_config["relay_pins"],
        "sensor_pins": gpio_config["sensor_pins"],
        "calibration": calibration_config
    }

    return render_template(
        "admin_ports.html",
        config=merged_config,
        available_gpio=gpio_data["available"],
        used_pins=gpio_data["used"]
    )

@port_routes.route("/admin/ports", methods=["POST"])
def update_port_gpio():
    port = request.form.get("port")
    relay = int(request.form.get("relay_bcm"))
    sensor_open = int(request.form.get("sensor_open_bcm"))
    sensor_closed = int(request.form.get("sensor_closed_bcm"))

    gpio = config_manager.get_module("gpio")
    gpio["relay_pins"][port] = relay
    gpio["sensor_pins"][port] = {
        "open": sensor_open,
        "closed": sensor_closed
    }
    config_manager.update_module("gpio", gpio, user="web", source="port config")
    flash(f"GPIO-konfig for {port} er oppdatert.", "success")
    return redirect(url_for("port_routes.show_ports"))

@port_routes.route("/admin/calibrate", methods=["POST"])
def save_manual_calibration():
    port = request.form.get("port")
    open_time = float(request.form.get("open_time"))
    close_time = float(request.form.get("close_time"))

    system = config_manager.get_module("system")
    if "calibration" not in system:
        system["calibration"] = {}

    system["calibration"][port] = {
        "open_time": open_time,
        "close_time": close_time,
        "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        "source": "web"
    }

    config_manager.update_module("system", system, user="web", source="calibration")
    flash(f"Kalibreringsdata for {port} er lagret.", "success")
    return redirect(url_for("port_routes.show_ports"))
