# Fil: app.py
# Flask hovedapplikasjon, ruter og oppstartspunkt

from flask import Flask, render_template, redirect, url_for, request, flash
from garage_controller import GarageController
import json
import os
import logging
from logger import setup_logging
import atexit

# Initialiser logger
setup_logging()

# Last inn config
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

# Start Flask-app
app = Flask(__name__)
app.secret_key = "supersecretkey"
garage = GarageController(config)

# Sørg for at GPIO ryddes ved exit
atexit.register(garage.cleanup)

@app.route("/")
def index():
    statuses = {}
    for port in config.get("ports", []):
        statuses[port] = {
            "status": garage.get_status(port)
        }
    return render_template("index.html", statuses=statuses)

@app.route("/open/<port>")
def open_port(port):
    if garage.open_port(port):
        flash(f"Porten {port} ble aktivert", "success")
    else:
        flash(f"Feil: kunne ikke åpne {port}", "danger")
    return redirect(url_for("index"))

# Rute: /admin – konfigurasjon av porter og GPIO



@app.route("/admin", methods=["GET", "POST"])
def admin():
    """
    Adminpanel – lar brukeren konfigurere rele og sensor-pinner for porter.
    Vis tilgjengelige GPIO-pinner (sortert etter fysisk pin).
    Hindre duplikatbruk internt og globalt.
    """

    config_path = "config.json"

    def get_available_gpio():
        gpio_map = [
            {"bcm": 2, "pin": 3}, {"bcm": 3, "pin": 5}, {"bcm": 4, "pin": 7}, {"bcm": 17, "pin": 11},
            {"bcm": 27, "pin": 13}, {"bcm": 22, "pin": 15}, {"bcm": 10, "pin": 19}, {"bcm": 9, "pin": 21},
            {"bcm": 11, "pin": 23}, {"bcm": 0, "pin": 27}, {"bcm": 5, "pin": 29}, {"bcm": 6, "pin": 31},
            {"bcm": 13, "pin": 33}, {"bcm": 19, "pin": 35}, {"bcm": 26, "pin": 37}, {"bcm": 14, "pin": 8},
            {"bcm": 15, "pin": 10}, {"bcm": 18, "pin": 12}, {"bcm": 23, "pin": 16}, {"bcm": 24, "pin": 18},
            {"bcm": 25, "pin": 22}, {"bcm": 8, "pin": 24}, {"bcm": 7, "pin": 26}, {"bcm": 1, "pin": 28},
            {"bcm": 12, "pin": 32}, {"bcm": 16, "pin": 36}, {"bcm": 20, "pin": 38}, {"bcm": 21, "pin": 40}
        ]
        return sorted(gpio_map, key=lambda g: g["pin"])

    try:
        with open(config_path, "r") as f:
            config = json.load(f)
    except Exception as e:
        flash(f"Feil ved lesing av config.json: {e}", "danger")
        config = {"relay_pins": {}, "sensor_pins": {}}

    if request.method == "POST":
        try:
            port = request.form["port"]
            new_relay = int(request.form["relay_bcm"])
            new_open = int(request.form["sensor_open_bcm"])
            new_closed = int(request.form["sensor_closed_bcm"])

            # Intern validering – sjekk for duplikatbruk i samme port
            pin_values = [new_relay, new_open, new_closed]
            if len(set(pin_values)) != len(pin_values):
                flash("Samme GPIO-pinne kan ikke brukes flere ganger for samme port.", "danger")
            else:
                config["relay_pins"][port] = new_relay
                config["sensor_pins"][port]["open"] = new_open
                config["sensor_pins"][port]["closed"] = new_closed
                with open(config_path, "w") as fw:
                    json.dump(config, fw, indent=4)
                flash(f"GPIO-pinner oppdatert for {port}", "success")
        except Exception as e:
            flash(f"Feil under oppdatering: {e}", "danger")

    # Globale brukte pinner for å disable i dropdowns
    used_pins = set(config.get("relay_pins", {}).values())
    for sensor in config.get("sensor_pins", {}).values():
        used_pins.add(sensor.get("open"))
        used_pins.add(sensor.get("closed"))

    return render_template("admin.html", config=config, available_gpio=get_available_gpio(), used_pins=used_pins)
@app.route("/logout")
def logout():
    session.clear()
    flash("Du er logget ut", "info")
    return redirect(url_for("login"))

@app.route("/logs")
def logs():
    try:
        with open("logs/garage.log", "r") as f:
            log_content = f.readlines()
    except FileNotFoundError:
        log_content = ["Loggfil ikke funnet."]
    return render_template("logs.html", log_content=log_content)

@app.route("/stats")
def stats():
    dummy_stats = {"Port 1": 10, "Port 2": 7}
    return render_template("stats.html", stats=dummy_stats)

@app.route("/admin/backup")
def admin_backup():
    backup_dir = "backups"
    os.makedirs(backup_dir, exist_ok=True)
    backups = sorted(os.listdir(backup_dir), reverse=True)
    return render_template("backup.html", backups=backups)


# 🚀 Lager ny backup av konfigurasjonsfilen


# 📄 Viser innholdet i en backup
@app.route("/admin/backup/view/<filename>")
def view_backup(filename):
    path = os.path.join("backups", filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        return render_template("backup_view.html", filename=filename, content=content)
    else:
        flash("Filen finnes ikke")
        return redirect(url_for("admin_backup"))

# 🔁 Gjenoppretter backup etter bekreftelse

@app.route("/backup")
def view_backups():
    import os
    backup_dir = "backups"
    backups = sorted(os.listdir(backup_dir), reverse=True) if os.path.exists(backup_dir) else []
    return render_template("backup.html", backups=backups)

@app.route("/create-backup")
def create_backup():
    from datetime import datetime
    import shutil
    import os
    os.makedirs("backups", exist_ok=True)
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy("config.json", f"backups/config_{now}.json")
    flash("Backup opprettet", "success")
    return redirect("/backup")

@app.route("/restore/<filename>")
def restore_backup(filename):
    import shutil
    try:
        shutil.copy(f"backups/{filename}", "config.json")
        flash("Konfigurasjon gjenopprettet fra backup", "success")
    except Exception as e:
        flash(f"Feil under gjenoppretting: {e}", "danger")
    return redirect("/admin")


if __name__ == '__main__':    app.run(host='0.0.0.0', port=5000, debug=True)
