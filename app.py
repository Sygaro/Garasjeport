# Filnavn: app.py

from flask import Flask, render_template, request, redirect, url_for, session
import os
import json
import shutil
from datetime import datetime
from logger import log_event

app = Flask(__name__)
app.secret_key = 'supersecretkey'

CONFIG_PATH = "config.json"
BACKUP_DIR = "backups"

# Last inn konfigurasjon
def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return {}

# Lagre konfigurasjon
def save_config(data):
    with open(CONFIG_PATH, "w") as f:
        json.dump(data, f, indent=4)

# Forside
@app.route("/")
def index():
    config = load_config()
    statuses = {port: "Åpen" for port in config.get("ports", [])}
    return render_template("index.html", statuses=statuses)

# Adminpanel
@app.route("/admin", methods=["GET", "POST"])
def admin():
    config = load_config()

    if request.method == "POST":
        port_names = request.form.getlist("port_name")
        log_event(f"Mottatte portnavn fra skjema: {port_names}")
        try:
            config["ports"] = port_names
            config["relay_pins"] = {}
            config["sensor_pins"] = {}

            for idx, port in enumerate(port_names):
                relay = request.form.get(f"relay_{port}", "").strip()
                if relay:
                    config["relay_pins"][port] = int(relay)

                sensor_open = request.form.get(f"sensor_open_{port}", "").strip()
                sensor_closed = request.form.get(f"sensor_closed_{port}", "").strip()

                if sensor_open and sensor_closed:
                    config["sensor_pins"][port] = {
                        "open": int(sensor_open),
                        "closed": int(sensor_closed)
                    }

            save_config(config)
            log_event("Konfigurasjon oppdatert via adminpanel")
            return redirect(url_for("admin"))
        except Exception as e:
            log_event("Feil i adminpanel", level="error")
            print(e)

    return render_template("admin.html", config=config)

# Backup-side
@app.route("/admin/backup")
def admin_backup():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    backups = os.listdir(BACKUP_DIR)
    return render_template("backup.html", backups=backups)

# Lag backup
@app.route("/admin/backup/create")
def create_backup():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"config_backup_{timestamp}.json"
    shutil.copy(CONFIG_PATH, os.path.join(BACKUP_DIR, backup_name))
    log_event(f"Backup laget: {backup_name}")
    return redirect(url_for("admin_backup"))

# Gjenopprett backup
@app.route("/admin/backup/restore/<filename>")
def restore_backup(filename):
    try:
        backup_path = os.path.join(BACKUP_DIR, filename)
        shutil.copy(backup_path, CONFIG_PATH)
        log_event(f"Gjenopprettet backup: {filename}")
    except Exception as e:
        log_event(f"Feil ved gjenoppretting: {str(e)}", level="error")
    return redirect(url_for("admin_backup"))

# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
