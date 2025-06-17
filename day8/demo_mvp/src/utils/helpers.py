# Utility functions 

import logging
import os # Keep os for other potential uses, though getenv is replaced
from .config import config # Import the AppConfig instance

def setup_logging():
    """Configures basic logging for the application using settings from config."""
    # load_dotenv() is now handled by config.py implicitly upon import

    log_level_str = config.log_level # Get LOG_LEVEL from AppConfig. Changed from .LOG_LEVEL to .log_level
    log_level = getattr(logging, log_level_str, logging.INFO)

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler()  # Outputs to console
            # You can add FileHandler here if you want to log to a file
            # logging.FileHandler("app.log")
        ]
    )
    # Removed unused logger instance: logger = logging.getLogger(__name__)
    # Modules should get their own loggers if they need to log specific messages.
    # The root logger configuration done by basicConfig applies to all.

if __name__ == '__main__':
    # Example of how to use it
    setup_logging()
    # Get a logger for this example usage
    example_logger = logging.getLogger(__name__) 
    example_logger.debug("This is a debug message from helpers.py.")
    example_logger.info("This is an info message from helpers.py.")
    example_logger.warning("This is a warning message from helpers.py.")
    example_logger.error("This is an error message from helpers.py.")
    example_logger.critical("This is a critical message from helpers.py.") 