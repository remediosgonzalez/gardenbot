import logging


def setup():
    # Basic config for all the files
    logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(name)s |  %(levelname)s: %(message)s')
