import logging


CHUNK_SIZE = 4096
LOG_LEVEL = logging.INFO
logger = logging.getLogger()
logger.setLevel(LOG_LEVEL)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(module)s:%(funcName)s - %(message)s")
console_handler = logging.StreamHandler()
console_handler.setLevel(LOG_LEVEL)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)