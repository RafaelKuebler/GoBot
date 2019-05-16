import gobot.telegram as gobot
import logging
import sys
import datetime
import os
from key import token

__author__ = "Rafael Kübler da Silva <rafael_kuebler@yahoo.es>"
__version__ = "0.1"


if not os.path.exists('logs'):
    os.makedirs('logs')
log_filename = datetime.date.today()

logging.basicConfig(filename=f'logs/{log_filename}.log',
                    level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(message)s')
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

logging.info("Starting telegram bot...")
gobot.start_bot(token)
