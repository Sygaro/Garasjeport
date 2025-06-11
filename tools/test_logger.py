from utils.logging.unified_logger import get_logger

def main():
    logger = get_logger("GarageController", category="system", source="API")
    logger.info("Dette er en vanlig INFO-melding")
    logger.change("Dette er en custom CHANGE-melding (med farge)")
    logger.notice("Dette er en custom NOTICE-melding (med farge)")
    logger.timing("Dette er en custom NOTICE-melding (med farge)")


if __name__ == "__main__":
    main()
