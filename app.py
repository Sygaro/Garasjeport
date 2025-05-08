# Fil: app.py
# Flask hovedapplikasjon for garasjeprosjektet
# Inneholder ruter for adminpanel, portkontroll, kalibrering, backup og loggvisning

from flask import Flask, render_template, redirect, url_for, request, flash, session, send_from_directory
from garage_controller import GarageController
from logger import setup_logging
from datetime import datetime, timedelta
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
@app.before_request
def session_timeout_check():
    with open("config.json", "r") as f:
        conf = json.load(f)

    timeout_minutes = conf.get("session_timeout_minutes", 15)
    timeout_seconds = timeout_minutes * 60

    now = datetime.now().timestamp()
    last = session.get("last_activity", now)
    session["last_activity"] = now

    if session.get("logged_in") and (now - last > timeout_seconds):
        session.clear()
        flash("Du ble logget ut pga. inaktivitet.", "warning")
        return redirect("/login")

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

@app.template_filter("siden_tidspunkt")
@login_required_if_enabled
def siden_tidspunkt(iso_str):
    try:
        dt = datetime.fromisoformat(iso_str)
        nå = datetime.now()
        diff = nå - dt
        dager = diff.days
        sek = diff.seconds
        if dager > 0:
            return f"for {dager} dager siden"
        elif sek >= 3600:
            return f"for {sek // 3600} timer siden"
        elif sek >= 60:
            return f"for {sek // 60} minutter siden"
        else:
            return "nå nettopp"
    except:
        return ""


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
        flash(f"Feil ved lasting av config.json: {e}", "danger")
        config = {"relay_pins": {}, "sensor_pins": {}}

    # 📤 Håndter POST-skjemaer
    if request.method == "POST":
        setting = request.form.get("setting")

        # 🔐 Endre session-timeout
        if setting == "timeout":
            try:
                timeout_val = request.form.get("session_timeout")
                if not timeout_val:
                    raise ValueError("Session-timeout mangler.")
                val = int(timeout_val)

                config["session_timeout_minutes"] = val
                with open(config_path, "w") as fw:
                    json.dump(config, fw, indent=4)
                flash(f"Session-timeout oppdatert til {val} minutter", "success")
            except Exception as e:
                flash(f"Feil ved lagring av session-timeout: {e}", "danger")

        # 🔔 Flash-meldingers varighet
        elif setting == "flash_timeout":
            try:
                flash_data = {}
                for cat in ["success", "info", "warning", "danger"]:
                    val = int(request.form.get(f"flash_{cat}", 30))
                    if not (1 <= val <= 300):
                        raise ValueError(f"Verdi for {cat} må være mellom 1 og 300 sekunder.")
                    flash_data[cat] = val
                config["flash_timeout"] = flash_data
                with open(config_path, "w") as fw:
                    json.dump(config, fw, indent=4)
                flash("Visningstid for meldinger oppdatert.", "success")
            except Exception as e:
                flash(f"Feil ved lagring av flash-timeout: {e}", "danger")

        # 📦 Endre antall dager backup beholdes
        elif setting == "retention_days":
            try:
                days = int(request.form.get("retention_days"))
                if not (1 <= days <= 365):
                    raise ValueError("Velg mellom 1 og 365 dager.")
                config["backup_retention_days"] = days
                with open(config_path, "w") as fw:
                    json.dump(config, fw, indent=4)
                flash(f"Behold backupfiler i {days} dager", "success")
            except Exception as e:
                flash(f"Feil ved lagring av antall dager: {e}", "danger")

        # ⚙️ Oppdater porter (GPIO-konfig)
        elif request.form.get("port"):
            try:
                port = request.form["port"]
                new_relay = int(request.form["relay_bcm"])
                new_open = int(request.form["sensor_open_bcm"])
                new_closed = int(request.form["sensor_closed_bcm"])

                pin_values = [new_relay, new_open, new_closed]
                if len(set(pin_values)) != len(pin_values):
                    flash("Samme GPIO-pinne kan ikke brukes flere ganger for samme port.", "danger")
                else:
                    config["relay_pins"][port] = new_relay
                    if port not in config["sensor_pins"]:
                        config["sensor_pins"][port] = {}
                    config["sensor_pins"][port]["open"] = new_open
                    config["sensor_pins"][port]["closed"] = new_closed

                    with open(config_path, "w") as fw:
                        json.dump(config, fw, indent=4)
                    flash(f"GPIO-pinner oppdatert for {port}", "success")
            except Exception as e:
                flash(f"Feil under oppdatering av porter: {e}", "danger")

    # 🌐 Brukte pinner for å disable dem i dropdown
    used_pins = set(config.get("relay_pins", {}).values())
    for sensor in config.get("sensor_pins", {}).values():
        used_pins.add(sensor.get("open"))
        used_pins.add(sensor.get("closed"))

    # 📂 Hent nyeste og eldste backup for visning
    backup_dir = "backups"
    latest_backup = None
    eldste_dato = None
    neste_autoslett = None

    if os.path.exists(backup_dir):
        files = sorted(os.listdir(backup_dir))
        for f in files:
            try:
                if not f.endswith(".json"):
                    continue
                parts = f.replace(".json", "").split("_")
                if len(parts) < 3:
                    continue
                dt = datetime.strptime(parts[-2] + "_" + parts[-1], "%Y%m%d_%H%M%S")
                if not eldste_dato or dt < eldste_dato:
                    eldste_dato = dt
            except:
                continue
        if files:
            latest_backup = files[-1]
        if eldste_dato:
            retention = config.get("backup_retention_days", 30)
            neste_autoslett = eldste_dato + timedelta(days=retention)

    # 📤 Render admin-panelet
    return render_template(
        "admin.html",
        config=config,
        available_gpio=get_available_gpio(),
        used_pins=used_pins,
        latest_backup=latest_backup,
        eldste_dato=eldste_dato,
        neste_autoslett=neste_autoslett
    )




# 🔧 Kalibreringsrute – lagrer åpne-/lukketid i sekunder
@app.route("/admin/calibrate", methods=["POST"])
@login_required_if_enabled
def calibrate():
    port = request.form.get("port")
    action = request.form.get("action")  # NEW

    try:
        open_val = request.form.get("open_time")
        close_val = request.form.get("close_time")

        with open("config.json", "r") as f:
            config = json.load(f)

        if "calibration" not in config:
            config["calibration"] = {}
        if port not in config["calibration"]:
            config["calibration"][port] = {}

        now = datetime.now().isoformat(timespec="seconds")

        if action == "save_open":
            open_time = float(open_val)
            if not (0 <= open_time <= 60):
                raise ValueError("Åpnetid må være mellom 0 og 60 sek.")
            config["calibration"][port]["open_time"] = open_time
            config["calibration"][port]["source"] = "manuell"
            config["calibration"][port]["timestamp"] = now
            flash(f"Åpnetid lagret for {port}", "success")

        elif action == "save_close":
            close_time = float(close_val)
            if not (0 <= close_time <= 60):
                raise ValueError("Lukketid må være mellom 0 og 60 sek.")
            config["calibration"][port]["close_time"] = close_time
            config["calibration"][port]["source_close"] = "manuell"
            config["calibration"][port]["timestamp_close"] = now
            flash(f"Lukketid lagret for {port}", "success")

        with open("config.json", "w") as f:
            json.dump(config, f, indent=4)

    except Exception as e:
        flash(f"Feil under lagring: {e}", "danger")

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
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
        retention_days = config.get("backup_retention_days", 30)
    except:
        retention_days = 30

    now = datetime.now()
    deleted = 0
    for f in os.listdir(backup_dir):
        path = os.path.join(backup_dir, f)
        try:
            created = datetime.strptime(f.split('_')[-1].replace(".json", ""), "%Y%m%d_%H%M%S")
            if (now - created).days > retention_days:
                os.remove(path)
                deleted += 1
        except:
            continue

    if deleted:
        flash(f"{deleted} gamle backupfiler ble automatisk fjernet", "info")

    backups = sorted(os.listdir(backup_dir), reverse=True)
    return render_template("backup.html", backups=backups, retention_days=retention_days)


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

@app.route("/download-backup/<filename>")
@login_required_if_enabled
def download_backup(filename):
    return send_from_directory("backups", filename, as_attachment=True)

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

@app.route("/delete-backup/<filename>")
@login_required_if_enabled
def delete_backup(filename):
    path = os.path.join("backups", filename)
    try:
        if os.path.exists(path):
            os.remove(path)
            flash(f"Backupfil '{filename}' ble slettet", "success")
        else:
            flash("Filen finnes ikke", "warning")
    except Exception as e:
        flash(f"Feil ved sletting: {e}", "danger")
    return redirect(url_for("admin_backup"))

@app.route("/delete-multiple-backups", methods=["POST"])
@login_required_if_enabled
def delete_multiple_backups():
    files = request.form.getlist("selected_files")
    deleted = 0
    for f in files:
        path = os.path.join("backups", f)
        if os.path.exists(path):
            os.remove(path)
            deleted += 1
    flash(f"{deleted} backupfiler slettet", "success")
    return redirect(url_for("admin_backup"))

@app.route("/admin/backup/old")
@login_required_if_enabled
def show_old_backups():
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
        retention_days = config.get("backup_retention_days", 30)
    except:
        retention_days = 30

    old_files = []
    now = datetime.now()
    backup_dir = "backups"
    if os.path.exists(backup_dir):
        for f in os.listdir(backup_dir):
            try:
                if not f.endswith(".json"):
                    continue
                parts = f.replace(".json", "").split("_")
                if len(parts) < 3:
                    continue
                dt = datetime.strptime(parts[-2] + "_" + parts[-1], "%Y%m%d_%H%M%S")
                age_days = (now - dt).days
                if age_days > retention_days:
                    old_files.append({
                        "filename": f,
                        "created": dt.strftime("%d.%m.%Y %H:%M:%S"),
                        "age": age_days
                    })
            except:
                continue

    return render_template("confirm_delete_old.html", old_files=old_files, retention_days=retention_days)

@app.route("/admin/backup/delete-old", methods=["POST"])
@login_required_if_enabled
def delete_old_backups():
    deleted = 0
    backup_dir = "backups"

    try:
        with open("config.json", "r") as f:
            config = json.load(f)
        retention_days = config.get("backup_retention_days", 30)
    except:
        retention_days = 30

    now = datetime.now()

    for f in os.listdir(backup_dir):
        try:
            if not f.endswith(".json"):
                continue
            parts = f.replace(".json", "").split("_")
            if len(parts) < 3:
                continue
            dt = datetime.strptime(parts[-2] + "_" + parts[-1], "%Y%m%d_%H%M%S")
            if (now - dt).days > retention_days:
                os.remove(os.path.join(backup_dir, f))
                deleted += 1
        except:
            continue

    flash(f"{deleted} gamle backupfiler ble slettet.", "success")
    return redirect(url_for("admin_backup"))



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
    try:
        with open("config.json", "r") as f:
            config_data = json.load(f)
    except:
        config_data = {}
    return dict(config_data=config_data)
    return dict(config=app.config, config_data=config)



if __name__ == '__main__':    app.run(host='0.0.0.0', port=5000, debug=True)
