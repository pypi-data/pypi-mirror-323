import logging
import os
import sys


class Logger:
    """
    Handles the creation, setup, and management of logging functionalities.

    This class facilitates logging by creating and managing a logger instance with
    customizable logging directory, name, and file. It ensures logs from a script
    are stored in a well-defined directory and file, and provides various logging
    methods for different log levels. The logger automatically formats and handles
    log messages. Additionally, this class provides a class method to initialize a
    logger with default behaviors.

    :ivar log_dir: Path to the directory where log files are stored.
    :type log_dir: str
    :ivar logger_name: Name of the logger instance.
    :type logger_name: str
    :ivar log_file: Base name of the log file.
    :type log_file: str
    :ivar logger: The initialized logger instance used for logging messages.
    :type logger: logging.Logger
    """
    def __init__(self, log_dir, logger_name, log_file):
        self.log_dir = log_dir
        self.logger_name = logger_name
        self.log_file = log_file
        self.logger = None

        self._setup()

    def _setup(self):
        # Ensure the log directory exists
        os.makedirs(self.log_dir, exist_ok=True)

        # Get the name of the calling script
        calling_script = os.path.splitext(os.path.basename(sys.argv[0]))[0]

        # Create a log file path
        log_file_path = os.path.join(self.log_dir, f"{self.log_file}_{calling_script}.log")

        # Delete the existing log file if it exists
        if os.path.exists(log_file_path):
            os.remove(log_file_path)

        # Create a logger
        self.logger = logging.getLogger(self.logger_name)
        self.logger.setLevel(logging.DEBUG)  # Log all levels DEBUG and above

        # Create a file handler
        handler = logging.FileHandler(log_file_path)

        # Create a formatter and add it to the handler
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        # Add the handler to the logger
        self.logger.addHandler(handler)

    @classmethod
    def default_logger(cls, log_dir='./logs/', logger_name=None, log_file=None):
        """
        Class-level method to create a default logger with generic parameters.
        :param log_dir: Directory where logs are stored.
        :param logger_name: Name of the logger (defaults to __name__).
        :param log_file: Name of the log file (defaults to logger_name).
        :return: Instance of Logger.
        """
        logger_name = logger_name or __name__
        log_file = log_file or logger_name
        return cls(log_dir=log_dir, logger_name=logger_name, log_file=log_file)

    def set_level(self, level):
        self.logger.setLevel(level)

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def critical(self, msg):
        self.logger.critical(msg)
