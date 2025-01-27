import logging

class NaoLogger:
    
    def __init__(self, name:str='default_nao_logger', formatter:str='%(asctime)s - %(name)s - %(levelname)s - %(message)s', log_file_name:str='log.log', console_handler_level=logging.DEBUG, file_handler_level=logging.DEBUG):

        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter(formatter)

        # Create console handler and set level
        console_handler = logging.StreamHandler()
        console_handler.setLevel(console_handler_level)

        # Create file handler and set level
        file_handler = logging.FileHandler(log_file_name)
        file_handler.setLevel(file_handler_level)

        # Create file handler and set level
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
