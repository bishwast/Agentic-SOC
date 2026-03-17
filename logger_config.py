import logging
import sys

def setup_logger():
    logger = logging.getLogger("AgenticSOC")
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        c_handler = logging.StreamHandler(sys.stdout)
        f_handler = logging.FileHandler('agentic_sic_api.log')
        c_handler.setLevel(logging.INFO)
        f_handler.setLevel(logging.INFO)
        format_style = logging.Formatter('%(asctime)s - [%(levelname)s] - %(name)s - %(message)s')
        c_handler.setFormatter(format_style)
        f_handler.setFormatter(format_style)
        logger.addHandler(c_handler)
        logger.addHandler(f_handler)
    return logger

logger = setup_logger()