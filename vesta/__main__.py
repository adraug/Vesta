import os
import logging

from vesta import TOKEN, vesta_client, engine
from vesta import commands
from vesta.tables import Base
from vesta.log import logger

logger.setLevel(int(os.getenv('LOGGING_LEVEL', logging.DEBUG)))

Base.metadata.create_all(engine, checkfirst=True)

vesta_client.run(TOKEN)
