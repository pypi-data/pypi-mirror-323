import logging

def get_nao_logger(
    name: str = 'default_nao_logger',
    formatter: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    log_file_name: str = 'log.log',
    console_handler_level=logging.DEBUG,
    file_handler_level=logging.DEBUG
):
    # Create or get a logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Prevent duplicate handlers if the logger is already configured
    if not logger.handlers:
        # Set up formatter
        log_formatter = logging.Formatter(formatter)

        # Create console handler and set level
        console_handler = logging.StreamHandler()
        console_handler.setLevel(console_handler_level)
        console_handler.setFormatter(log_formatter)  # Set the formatter

        # Create file handler and set level
        file_handler = logging.FileHandler(log_file_name)
        file_handler.setLevel(file_handler_level)
        file_handler.setFormatter(log_formatter)  # Set the formatter

        # Add handlers to the logger
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger