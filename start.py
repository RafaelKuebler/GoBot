import logging
import sys
import datetime
import os

from gobot.telegram_interface import TelegramInterface

__author__ = "Rafael Kübler da Silva <rafael_kuebler@yahoo.es>"
__version__ = "0.1"


if not os.path.exists('logs'):
    os.makedirs('logs')

log_filename = datetime.date.today()
logging.basicConfig(filename=f'logs/{log_filename}.log',
                    filemode='w',
                    level=logging.INFO,
                    format='%(asctime)s [%(levelname)s] %(message)s')
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

if "TOKEN" not in os.environ:
    logging.error("No TOKEN specified!")
    exit(1)

bot = TelegramInterface()
bot.start_bot(os.environ.get('TOKEN'))
