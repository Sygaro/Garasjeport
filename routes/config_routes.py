# ==========================================
# Filnavn: config_routes.py
# API-endepunkter koblet til ConfigManager
# ==========================================

from flask import Blueprint, jsonify, request, send_file
import os, shutil, json
from core.config_manager import ConfigManager
from datetime import datetime
import zipfile
import io

config_routes = Blueprint("config_routes", __name__)
manager = ConfigManager()

BACKUP_DIR = "backups"

@config_routes.route("/api/config", methods=["GET"])
def get_all_config():
    return jsonify(manager.get_all())

@config_routes.route("/api/config/<module>", methods=["GET"])
def get_gpio():
    try:
        data = manager.get_module("gpio")
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@config_routes.route("/api/config/gpio", methods=["PUT"])
def update_gpio():
    try:
        new_data = request.get_json()
        manager.update_module("gpio", new_data, user="admin", source="web")
        return jsonify({"status": "OK"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_config_module(module):
    try:
        data = manager.get_module(module)
        return jsonify(data)
    except:
        print(f"Henter modul: {module}")
        return jsonify({"error": f"Modul '{module}' ikke funnet"}), 404

@config_routes.route("/api/config/<module>", methods=["PUT"])
def update_config_module(module):
    try:
        new_data = request.get_json()
        manager.update_module(module, new_data, user="admin", source="web")
        return jsonify({"status": "OK", "message": f"{module} oppdatert"}), 200
    except Exception as e:
        print(f"Oppdaterer modul: {module}")
        print(request.get_json())
        return jsonify({"status": "Feil", "message": str(e)}), 400

@config_routes.route("/api/config/backups/<module>", methods=["GET"])
def list_backups(module):
    files = sorted([
        f for f in os.listdir(BACKUP_DIR)
        if f.startswith(f"{module}_") and f.endswith(".json")
    ], reverse=True)
    return jsonify({"backups": files})

@config_routes.route("/api/config/backup/<filename>", methods=["GET"])
def download_backup(filename):
    path = os.path.join(BACKUP_DIR, filename)
    if not os.path.exists(path):
        return jsonify({"error": "Filen finnes ikke"}), 404
    return send_file(path, as_attachment=True)

@config_routes.route("/api/config/restore/<module>", methods=["POST"])
def restore_backup(module):
    data = request.get_json()
    filename = data.get("filename")
    path = os.path.join(BACKUP_DIR, filename)

    if not os.path.exists(path):
        return jsonify({"error": "Filen finnes ikke"}), 404

    with open(path) as f:
        content = f.read()
        manager.update_module(module, json.loads(content), user="admin", source="restore")

    return jsonify({"message": f"{module} gjenopprettet fra {filename}"}), 200

@config_routes.route("/api/config/export", methods=["GET"])
def export_full_config():
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Legg til config/
        for root, _, files in os.walk("config"):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, ".")
                zf.write(full_path, arcname=rel_path)

        # Legg til logs/
        for root, _, files in os.walk("logs"):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, ".")
                zf.write(full_path, arcname=rel_path)

    memory_file.seek(0)
    return send_file(
        memory_file,
        mimetype="application/zip",
        as_attachment=True,
        download_name=f"garasje_export_{datetime.now().strftime('%Y-%m-%d')}.zip"
    )

    