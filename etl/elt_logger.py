import logging

# Use Airflow's built-in logging (no need to create /opt/airflow/logs)
# Logging is managed by Astronomer/Airflow scheduler
logger = logging.getLogger(__name__)

# Configure format for clear, readable logs
formatter = logging.Formatter(
    '%(asctime)s - [%(levelname)s] - %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Get or create logger
_logger = logging.getLogger('infrapulse_etl')
_logger.setLevel(logging.INFO)

def log_info(msg):
    """Log informational message"""
    _logger.info(msg)

def log_error(msg):
    """Log error message"""
    _logger.error(msg)

def log_warning(msg):
    """Log warning message"""
    _logger.warning(msg)

def log_debug(msg):
    """Log debug message (detailed tracing)"""
    _logger.debug(msg)
