import logging
logger = logging.getLogger(__name__)


import logging

# Initialize logger
logger = logging.getLogger(__name__)

def print_hello():
    try:
        print("Hello World")
        logger.info("Hello World")
    except Exception as e:
        # Log the exception
        logger.exception("An error occurred: %s", str(e))
