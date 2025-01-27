import logging
import json
import socket
from datetime import datetime
from pathlib import Path
from logging.handlers import TimedRotatingFileHandler
import os
import threading
import time
from logging.handlers import SocketHandler
from distutils.util import strtobool

class LogstashHandler(SocketHandler):
    """Custom handler for sending logs to Logstash with retry mechanism."""
    def __init__(self, host, port, max_retries=5, retry_delay=5):
        super().__init__(host, port)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.connect_with_retry()

    def connect_with_retry(self):
        """Attempt to connect to Logstash with retries."""
        for attempt in range(self.max_retries):
            try:
                self.createSocket()
                return
            except (socket.error, socket.gaierror) as e:
                if attempt < self.max_retries - 1:
                    print(f"Failed to connect to Logstash (attempt {attempt + 1}/{self.max_retries}), "
                          f"retrying in {self.retry_delay} seconds... Error: {str(e)}")
                    time.sleep(self.retry_delay)
                else:
                    print(f"Could not connect to Logstash after {self.max_retries} attempts: {str(e)}")

    def emit(self, record):
        """Send a log record to Logstash, reconnecting if necessary."""
        try:
            s = self.format(record) + '\n'
            if not self.sock:
                self.connect_with_retry()
            if self.sock:
                self.sock.sendall(s.encode())
        except Exception as e:
            self.handleError(record)
            # Try to reconnect for next time
            self.sock = None

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "container_id": socket.gethostname(),
            "app_name": os.getenv("APP_NAME", "unknown"),
            "file": f"{Path(record.pathname).as_posix()}:{record.lineno}",
            "level": record.levelname.lower(),
            "msg": record.getMessage(),
            "time": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

        # Add transaction_id if available in thread-local storage
        transaction_id = getattr(record, 'transaction_id', None)
        if transaction_id:
            log_entry["transaction_id"] = transaction_id

        return json.dumps(log_entry)

_thread_local = threading.local()

def set_transaction_id(transaction_id):
    """Sets the transaction ID for the current thread."""
    _thread_local.transaction_id = transaction_id

def get_transaction_id():
    """Gets the transaction ID for the current thread."""
    return getattr(_thread_local, "transaction_id", None)

class ContextFilter(logging.Filter):
    """Logging filter to inject the transaction_id into log records."""
    def filter(self, record):
        record.transaction_id = get_transaction_id()
        return True

def get_logger(
    name="custom_logger",
    level=logging.INFO,
    log_dir="logs",
    file_name="app.log",
    console_logging=True,
    file_logging=True,
    backup_count=7,
):
    """
    Get a pre-configured logger with optional Logstash support.

    :param name: Name of the logger.
    :param level: Logging level.
    :param log_dir: Directory to store log files.
    :param file_name: Name of the log file.
    :param console_logging: Whether to log to console.
    :param file_logging: Whether to log to a file.
    :param backup_count: Number of rotated log files to retain.
    :return: Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent duplicate handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    # Add the context filter to include transaction ID
    logger.addFilter(ContextFilter())

    # Create logs directory if it doesn't exist
    if file_logging:
        log_dir_path = Path(log_dir)
        log_dir_path.mkdir(exist_ok=True)

    # Console Handler
    if console_logging:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(JsonFormatter())
        logger.addHandler(console_handler)

    # File Handler with daily rotation
    if file_logging:
        file_handler = TimedRotatingFileHandler(
            filename=log_dir_path / file_name,
            when="midnight",
            interval=1,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(JsonFormatter())

        # Set log files to compress after rotation
        file_handler.namer = lambda name: name + ".zip"
        file_handler.rotator = lambda source, dest: os.rename(source, dest)

        logger.addHandler(file_handler)

    # Logstash Handler (if enabled)
    logstash_enable = strtobool(os.getenv("LOGSTASH_ENABLE", "false"))
    if logstash_enable:
        logstash_host = os.getenv("LOGSTASH_HOST", "logstash")
        logstash_port = int(os.getenv("LOGSTASH_PORT", "8900"))
        
        logstash_handler = LogstashHandler(
            host=logstash_host,
            port=logstash_port,
            max_retries=5,
            retry_delay=5
        )
        logstash_handler.setLevel(level)
        logstash_handler.setFormatter(JsonFormatter())
        logger.addHandler(logstash_handler)

    return logger
