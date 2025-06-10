# main.py

import sys
from core.bootstrap import run_bootstrap

def main():
    # --- Kjør alltid bootstrap FØR noe annet! ---
    status = run_bootstrap()
    if not status["ok"]:
        print("[FATAL] Bootstrap feilet – systemet starter IKKE. Sjekk logg.")
        sys.exit(1)

    # --- Nå er det trygt å importere logger og systemmoduler ---
    from flask import Flask
    from utils.logging.unified_logger import get_logger
    from core import system_init
    from routes.api import api, port_routes, status_routes, config_routes, log_routes, system_routes, sensor_routes, bootstrap_routes
    from routes.web import web

    logger = get_logger("main", category="system")
    logger.info("=== System oppstart: starter Flask-app og kjører systeminitiering ===")

    try:
        system_init.init()
        logger.info("Systeminitiering OK.")
    except Exception as e:
        logger.error(f"Feil under systeminitiering: {e}", exc_info=True)
        sys.exit(2)

    app = Flask(__name__)
    app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True

    # Registrer API-blueprints
    for bp in [api, port_routes, status_routes, config_routes, log_routes, system_routes, sensor_routes, bootstrap_routes, web]:
        app.register_blueprint(bp)

    @app.route("/health")
    def health_check():
        return {"status": "ok", "version": "1.0"}

    logger.info("=== Starter Flask web-server ===")
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)

if __name__ == "__main__":
    main()
