import os
import conf
import logging
import datetime
from logging.handlers import RotatingFileHandler
from os import path

if not path.exists(conf.LOGDIR):
    os.mkdir(conf.LOGDIR)

log_formatter = logging.Formatter('%(asctime)s %(levelname)s (%(lineno)d) %(message)s')
# log_formatter = logging.Formatter('%(asctime)s %(funcName)s(%(lineno)d) %(message)s')

rolling_handler = RotatingFileHandler(os.path.join(conf.LOGDIR, datetime.datetime.now().strftime("%Y-%m-%d.log")))
rolling_handler.setFormatter(log_formatter)
rolling_handler.setLevel(logging.INFO)

logger = logging.getLogger('root')
logger.setLevel(logging.INFO)
logger.addHandler(rolling_handler)





