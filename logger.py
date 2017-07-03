import sys
import logging

logger = logging.getLogger('mm-bot')
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel('INFO')
