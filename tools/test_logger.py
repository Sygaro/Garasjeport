from utils.logging.unified_logger import get_logger

def main():
    logger1 = get_logger("GarageController", category="port_activity")
    logger2 = get_logger("system_init", category="system")
    logger3 = get_logger("env_manager", category="environment")

    logger1.debug("Port debug-melding (port_activity).")
    logger1.info("Port åpnet (port_activity).")
    logger2.info("Systeminit startet.")
    logger2.error("Noe gikk galt i systeminit.")
    logger3.info("Sensorer lastet.")
    logger3.warning("Miljøsensor viser lav verdi.")

if __name__ == "__main__":
    main()
