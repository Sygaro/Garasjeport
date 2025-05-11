
import logging

def apply_log_level(level_str):
    level = getattr(logging, level_str.upper(), logging.INFO)
    logging.basicConfig(level=level)
    logging.getLogger('werkzeug').setLevel(level)
    return level

def setup_rotating_logger(log_file, level=logging.INFO, when='W0', interval=1, backupCount=4):
    from logging.handlers import TimedRotatingFileHandler

    logger = logging.getLogger()
    logger.setLevel(level)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    handler = TimedRotatingFileHandler(log_file, when=when, interval=interval, backupCount=backupCount)
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger
