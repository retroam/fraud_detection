import logging

def setup_logger():
    """Set up a logger for the fraud detection package."""
    logger = logging.getLogger('fraud_detection')
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger