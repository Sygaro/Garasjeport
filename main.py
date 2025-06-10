#!/usr/bin/env python3

import sys
import signal
from utils.bootstrap_logger import get_bootstrap_logger

def main():
    # === 1. Kjør bootstrap FØRST ===
    from core import bootstrap
    bootstrap_logger = get_bootstrap_logger()
    try:
        status = bootstrap.run_bootstrap()
    except Exception as e:
        bootstrap_logger.error(f"Bootstrap feilet: {e}", exc_info=True)
        sys.exit(1)

    if not status.get("ok"):
        bootstrap_logger.error("Bootstrap feilet! Avslutter.")
        sys.exit(1)
    bootstrap_logger.info("Bootstrap OK – starter resten av systemet.")

    # === 2. Importer og start resten av systemet ===
    from core import system_init

    # === 3. Signalhåndtering for shutdown (CTRL+C, kill, systemstop) ===
    def handle_signal(signum, frame):
        from utils.logging.unified_logger import get_logger
        logger = get_logger("main", category="system")
        logger.info(f"Mottok signal {signum}. Kjører shutdown.")
        system_init.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    # === 4. System-initialisering ===
    try:
        system_init.init()
    except Exception as e:
        from utils.logging.unified_logger import get_logger
        logger = get_logger("main", category="system")
        logger.error(f"Feil under systeminitiering: {e}", exc_info=True)
        system_init.shutdown()
        sys.exit(1)

    # === 5. Start Flask-app (webserver) ===
    try:
        from app import app
        app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
    except (KeyboardInterrupt, SystemExit):
        # Normal avslutning
        system_init.shutdown()
    except Exception as e:
        from utils.logging.unified_logger import get_logger
        logger = get_logger("main", category="system")
        logger.error(f"Feil under Flask-app: {e}", exc_info=True)
        system_init.shutdown()
        sys.exit(1)

    # === 6. Sikkerhetsnett for shutdown (vanlig exit) ===
    system_init.shutdown()

if __name__ == "__main__":
    main()
