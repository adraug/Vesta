import logging

handler = logging.StreamHandler()
formatter = logging.Formatter("[{asctime}] [{levelname:<8}] {name}: {message}", "%Y-%m-%d %H:%M:%S", style="{")
library, _, _ = __name__.partition(".")

logger = logging.getLogger(library)
handler.setFormatter(formatter)
logger.addHandler(handler)