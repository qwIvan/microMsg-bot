import sys
import logging

logger = logging.getLogger('mm-bot')
stdout = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s\t%(message)s')
stdout.setFormatter(formatter)
logger.addHandler(stdout)
logger.setLevel('INFO')
