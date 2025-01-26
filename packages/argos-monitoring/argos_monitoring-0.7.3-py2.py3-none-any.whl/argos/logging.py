import logging


logging.getLogger("passlib").setLevel(logging.ERROR)


LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

# Print level before message
logging.basicConfig(format="%(levelname)-9s %(message)s")

# XXX We probably want different loggers for client and server.
logger = logging.getLogger(__name__)


# XXX Does not work ?
def set_log_level(log_level):
    level = getattr(logging, log_level.upper(), None)
    if not isinstance(level, int):
        raise ValueError(f"Invalid log level: {log_level}")
    logger.setLevel(level=level)
    logger.info("Log level set to %s", log_level)
