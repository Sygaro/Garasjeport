# Fil: app.py
# Flask hovedapplikasjon for garasjeprosjektet
# Inneholder ruter for adminpanel, portkontroll, kalibrering, backup og loggvisning

from flask import Flask, render_template, redirect, url_for, request, flash, session
from garage_controller import GarageController
from logger import setup_logging
from datetime import datetime
from event_log import log_event
import json
import os
import logging
import atexit
from flask import Flask, render_template


# 🚀 Initier logger og last konfig
setup_logging()
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

# 🌐 Start Flask
app = Flask(__name__)
app.secret_key = "supersecretkey"
garage = GarageController(config)

# 🔚 Rydd opp GPIO ved avslutning
atexit.register(garage.cleanup)

from functools import wraps

def login_required_if_enabled(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        with open("config.json", "r") as fconf:
            conf = json.load(fconf)
        if conf.get("require_login") and not session.get("logged_in"):
            flash("Du må logge inn for å få tilgang.", "warning")
            return redirect("/login")
        return f(*args, **kwargs)
    return wrapper


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("logged_in"):
            flash("Logg inn for å få tilgang", "warning")
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated


@app.route("/")
@login_required_if_enabled
def index():
    statuses = {}
    for port in config.get("ports", []):
        statuses[port] = {
            "status": garage.get_status(port)
        }
    return render_template("index.html", statuses=statuses)

@app.template_filter("format_norsk_dato")
@login_required_if_enabled
def format_norsk_dato(value):
    try:
        dt = datetime.fromisoformat(value)
        return dt.strftime("%d.%m.%Y %H:%M:%S")
    except Exception:
        return value  # fallback hvis parsing feiler

@app.route("/open/<port>")
@login_required_if_enabled
def open_port(port):
    if garage.open_port(port):
        flash(f"Porten {port} ble aktivert", "success")
    else:
        flash(f"Feil: kunne ikke åpne {port}", "danger")
    return redirect(url_for("index"))

# Rute: /admin – konfigurasjon av porter og GPIO



@app.route("/admin", methods=["GET", "POST"])
@login_required_if_enabled
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



# 🔧 Kalibreringsrute – lagrer åpne-/lukketid i sekunder
@app.route("/admin/calibrate", methods=["POST"])
@login_required_if_enabled
def calibrate():
    port = request.form.get("port")
    open_val = request.form.get("open_time")
    close_val = request.form.get("close_time")

    try:
        open_time = float(open_val)
        close_time = float(close_val)

        if not (0 <= open_time <= 60) or not (0 <= close_time <= 60):
            raise ValueError("Tiden må være mellom 0 og 60 sekunder.")

        with open("config.json", "r") as f:
            config = json.load(f)

        if "calibration" not in config:
            config["calibration"] = {}

        config["calibration"][port] = {
            "open_time": open_time,
            "close_time": close_time
        }

        with open("config.json", "w") as f:
            json.dump(config, f, indent=4)

        flash(f"Kalibrering lagret for {port}: Åpne: {open_time}s, Lukke: {close_time}s", "success")
    except Exception as e:
        flash(f"Feil under lagring av kalibrering: {e}", "danger")

    return redirect("/admin")



# Flask-rute for automatisk kalibrering via GPIO-måling

@app.route("/admin/calibrate/auto/<port>")
@login_required_if_enabled
def auto_calibrate(port):
    from datetime import datetime
    varighet = garage.maal_aapnetid(port)

    if varighet is None:
        flash(f"❌ Kalibrering feilet for {port}", "danger")
        return redirect("/admin")

    try:
        with open("config.json", "r") as f:
            config = json.load(f)

        if "calibration" not in config:
            config["calibration"] = {}

        if port not in config["calibration"]:
            config["calibration"][port] = {}

        # ✅ Oppdater bare åpne-feltene
        config["calibration"][port]["open_time"] = varighet
        config["calibration"][port]["source"] = "auto"
        config["calibration"][port]["timestamp"] = datetime.now().isoformat(timespec="seconds")

        with open("config.json", "w") as f:
            json.dump(config, f, indent=4)

        log_event("calibration", "Automatisk kalibrering lagret", port=port, data={"sekunder": varighet})
        flash(f"✅ Automatisk kalibrering for {port}: {varighet} sek", "success")

    except Exception as e:
        log_event("error", "Kunne ikke lagre kalibrering", port=port, data={"feil": str(e)})
        flash(f"Feil ved lagring: {e}", "danger")

    return redirect("/admin")


@app.route("/admin/calibrate/close/<port>")
@login_required_if_enabled
def auto_calibrate_close(port):
    from datetime import datetime
    varighet = garage.maal_lukketid(port)

    if varighet is None:
        flash(f"❌ Kalibrering av lukketid feilet for {port}", "danger")
        return redirect("/admin")

    try:
        with open("config.json", "r") as f:
            config = json.load(f)

        if "calibration" not in config:
            config["calibration"] = {}

        if port not in config["calibration"]:
            config["calibration"][port] = {}

        config["calibration"][port]["close_time"] = varighet
        config["calibration"][port]["source_close"] = "auto"
        config["calibration"][port]["timestamp_close"] = datetime.now().isoformat(timespec="seconds")

        with open("config.json", "w") as f:
            json.dump(config, f, indent=4)

        log_event("calibration", "Automatisk lukketid lagret", port=port, data={"sekunder": varighet})
        flash(f"✅ Lukketid målt for {port}: {varighet} sek", "success")

    except Exception as e:
        log_event("error", "Feil ved lagring av lukketid", port=port, data={"feil": str(e)})
        flash(f"Feil ved lagring: {e}", "danger")

    return redirect("/admin")


@app.route("/login", methods=["GET", "POST"])
def login():
    with open("config.json", "r") as f:
        config = json.load(f)
    auth = config.get("auth", {})
    correct_user = auth.get("username")
    correct_pass = auth.get("password")

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == correct_user and password == correct_pass:
            session["logged_in"] = True
            flash("Innlogging vellykket ✅", "success")
            return redirect("/")
        else:
            flash("Feil brukernavn eller passord ❌", "danger")

    return render_template("login.html")



@app.route("/logout")
@login_required_if_enabled
def logout():
    session.clear()
    flash("Du er logget ut", "info")
    return redirect(url_for("login"))

@app.route("/logs")
@login_required_if_enabled
def logs():
    try:
        with open("logs/garage.log", "r") as f:
            log_content = f.readlines()
    except FileNotFoundError:
        log_content = ["Loggfil ikke funnet."]
    return render_template("logs.html", log_content=log_content)

# 📜 Vis systemhendelser fra logs/events.log
@app.route("/admin/log")
@login_required_if_enabled
def vis_eventlogg():
    loggfil = "logs/events.log"
    hendelser = []

    if os.path.exists(loggfil):
        with open(loggfil, "r", encoding="utf-8") as f:
            for linje in f:
                try:
                    hendelser.append(json.loads(linje.strip()))
                except json.JSONDecodeError:
                    continue

    hendelser.reverse()  # Vis nyeste først
    return render_template("log.html", events=hendelser)


@app.route("/stats")
@login_required_if_enabled
def stats():
    return render_template("stats.html")

@app.route("/admin/backup")
@login_required_if_enabled
def admin_backup():
    backup_dir = "backups"
    os.makedirs(backup_dir, exist_ok=True)
    backups = sorted(os.listdir(backup_dir), reverse=True)
    return render_template("backup.html", backups=backups)


# 🚀 Lager ny backup av konfigurasjonsfilen


# 📄 Viser innholdet i en backup
@app.route("/admin/backup/view/<filename>")
@login_required_if_enabled
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
@login_required_if_enabled
def view_backups():
    import os
    backup_dir = "backups"
    backups = sorted(os.listdir(backup_dir), reverse=True) if os.path.exists(backup_dir) else []
    return render_template("backup.html", backups=backups)

@app.route("/create-backup")
@login_required_if_enabled
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
@login_required_if_enabled
def restore_backup(filename):
    import shutil
    try:
        shutil.copy(f"backups/{filename}", "config.json")
        flash("Konfigurasjon gjenopprettet fra backup", "success")
    except Exception as e:
        flash(f"Feil under gjenoppretting: {e}", "danger")
    return redirect("/admin")

@app.context_processor
def inject_config():
    return dict(config=app.config, config_data=config)



if __name__ == '__main__':    app.run(host='0.0.0.0', port=5000, debug=True)
