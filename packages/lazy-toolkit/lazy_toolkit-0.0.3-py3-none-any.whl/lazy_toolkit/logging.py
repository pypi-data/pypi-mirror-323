import logging
import os
import sys
import time
from logging import Formatter, Logger, handlers
from types import TracebackType

# Logger configs
LOGGING_WHEN: str = 'MIDNIGHT'
LOGGING_RETENTION_PERIOD: int = 28
LOG_FILE_PATTERN = "%Y.%m.%d.log"
LOGGING_LEVEL: int = logging.DEBUG
LOGGING_FORMATTER: str = "[%(name)s][%(levelname)s]|%(asctime)s|process:%(process)d|%(module)s|%(filename)s|@%(lineno)d|%(message)s"


class DefaultLogger:

    @staticmethod
    def get_logger(name: str,
                   log_path: str,
                   log_filename: str = 'default.log',
                   to_console: bool = True) -> Logger:
        """Get logger

        Args:
            name (str): Logger name
            log_file (str): Log file name
        """
        if not os.path.exists(log_path):
            os.makedirs(log_path, exist_ok=True)

        logger: Logger = logging.getLogger(name)
        logger.setLevel(LOGGING_LEVEL)
        formatter: Formatter = Formatter(LOGGING_FORMATTER)

        # Logging file config
        file_handler = handlers.TimedRotatingFileHandler(
            filename=os.path.join(log_path, log_filename),
            when=LOGGING_WHEN,
            backupCount=LOGGING_RETENTION_PERIOD)
        file_handler.suffix = LOG_FILE_PATTERN
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Logging to stdout config
        if to_console:
            stream_handler = logging.StreamHandler(sys.stderr)
            stream_handler.setFormatter(formatter)
            logger.addHandler(stream_handler)

        return logger


class Stopwatch:
    """A simple stopwatch to measure the elapsed time with logging
    """

    def __init__(self, logger: Logger, msg_on_finish: str | None = None, msg_on_failure: str | None = None):
        """
        Args:
            msg_on_finish (str | None): The message to log when the stopwatch finishes
            msg_on_failure (str | None): The message to log when failure occurs within the stopwatch context manager
        """
        self.start_time: float | None = None
        self.logger: Logger = logger
        self.normal_msg: str | None = msg_on_finish
        self.failure_msg: str | None = msg_on_failure

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self,
                 exc_type: type[BaseException] | None,
                 exc_val: BaseException | None,
                 exc_tb: TracebackType | None):
        if self.logger and self.start_time:
            seconds: float = time.time() - self.start_time

            if exc_type:
                # If there is an exception, log the failure message when failure message is provided
                if self.failure_msg:
                    self.logger.error(f'{self.failure_msg} | Exception: {exc_type.__name__}[{exc_val}] | {seconds:.2f}s')
            else:
                if self.normal_msg:
                    self.logger.info(f'{self.normal_msg} | {seconds:.2f}s')
                else:
                    self.logger.info(f'Elapsed time: {seconds:.2f}s')
                    self.logger.info(f'Elapsed time: {seconds:.2f}s')
