# ==========================================
# Filnavn: log_config.py
# Logger-konfig for fremtidig loggrotering/nivå
# ==========================================

LOG_ROTATION_DAYS = 7

DEFAULT_LOG_LEVEL = "INFO"

# Fremtidig støtte for roterende logger:
# from logging.handlers import TimedRotatingFileHandler
# handler = TimedRotatingFileHandler('logfile.log', when='midnight', interval=1, backupCount=7)
