import logging

def configure_logger(level=logging.INFO):
    logger = logging.getLogger('cwmaya')
    
    # Ensure the logger starts at INFO level
    logger.setLevel(logging.INFO)
    
    # Add a console handler if not already added
    if not logger.hasHandlers():
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger 