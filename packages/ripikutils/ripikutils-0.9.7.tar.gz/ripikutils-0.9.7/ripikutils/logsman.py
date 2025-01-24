import logging
from logging.handlers import RotatingFileHandler
import os
import sys
from datetime import datetime
from pytz import timezone
from typing import Union


def setup_logger(name: str = None, log_filename: str = None, 
                 prefix: str = '', postfix: str = '', 
                 log_dir: str = 'logs', timezone_name: str = 'Asia/Kolkata',
                 max_log_size: int = 100, backup_count: int = 5,
                 logging_level: Union[int, str] = logging.INFO):
    
    """ Sets up a logging configuration

    Args:
        name (str, optional): name of the logger. Defaults to None.
        log_filename (str, optional): filename of the file where the logs will be written. Defaults to None.
        prefix (str, optional): Any prefix that we want to add in logfile. Defaults to blank string.
        postfix (str, optional): Any postfix that we want to add in logfile. Defaults to blank string.
        log_dir (str, optional): directory path where the log files will be saved. Defaults to `'logs'`.
        timezone_name (str, optional): timezone that will used in the log filename if log_filename is None. Defaults to `'Asia/Kolkata'`.
        max_log_size (int, optional): Maximum size (in MB) of the log file before rotation. Defaults to 100 MB.
        backup_count (int, optional): Number of rotated log files to keep. Defaults to 5.
        logging_level (Union[int, str], optional): The logging level to set for the logger. Defaults to `logging.INFO`.

    Returns:
        logger object: configured logger
    """
    
    # Create logs directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)

    # Generate a unique log filename with timestamp
    timestamp = datetime.now(timezone(timezone_name)).strftime("%Y-%m-%d_%H-%M-%S")
    if log_filename is None:
        log_filename = f'log_{timestamp}.log'
    log_filename = prefix + os.path.splitext(log_filename)[0] + postfix + os.path.splitext(log_filename)[1]
    log_filename = os.path.join(log_dir, log_filename)

    # Configure the root logger
    logging.basicConfig(
        level=logging_level,  # Set the overall logging level
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            RotatingFileHandler(
                log_filename, maxBytes=int(max_log_size * 1024 * 1024), backupCount=backup_count
            ),
            logging.StreamHandler(sys.__stdout__)
        ]
    )

    # Get and return the logger (default to the root logger if name is None)
    logger = logging.getLogger(name or None)
    
    return logger


class LoggerWriter:
    """
    Custom writer to redirect stdout/stderr to logging.
    """
    def __init__(self, logger, level):
        self.logger = logger
        self.level = level
        self.linebuf = ''

    def write(self, message):
        if message.strip():  # Ignore empty lines
            self.logger.log(self.level, message.strip())

    def flush(self):
        pass  # For compatibility with file-like objects
    
    
class NoRecursiveFilter(logging.Filter):
    def filter(self, record):
        # Avoid re-logging messages
        return not record.msg.startswith("INFO:") and not record.msg.startswith("ERROR:")