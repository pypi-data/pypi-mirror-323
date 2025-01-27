import logging
import sys
import os

class DockerSafeLogger:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._configure_logger()

    def _configure_logger(self):
        # Set default log level from environment or use INFO
        log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        self.logger.setLevel(log_level)

        # Use a simple format that works well with container logs
        formatter = logging.Formatter(
            '%(asctime)s | %(process)d | %(levelname)-8s | %(module)s | %(message)s'
        )

        # Console handler using stdout (properly flushed)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(log_level)
        handler.setFormatter(formatter)

        # Add handler only if none exist
        if not self.logger.handlers:
            self.logger.addHandler(handler)

        # Prevent propagation to root logger
        self.logger.propagate = False

    def __getattr__(self, name):
        """Delegate logger methods"""
        return getattr(self.logger, name)