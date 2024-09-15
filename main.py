"""Module providing the main function for starting the handbrake automation."""

import logging
import os

from src.encoder import process_all_videos

LOG_FOLDER = "temp/logs"
LOG_FILE = os.path.join(LOG_FOLDER, "encoder.log")


def init_logger() -> None:
    """
    Initializes the logger, ensuring that the log directory exists.
    """
    os.makedirs(LOG_FOLDER, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler()
        ]
    )


init_logger()
logger = logging.getLogger(__name__)
MONITORING = False


def monitor_folder():
    """
    Function to start watching a given folder.
    """
    logger.info("Started monitoring folder...")
    while True:
        process_all_videos()


if __name__ == '__main__':
    if MONITORING:
        monitor_folder()
    else:
        process_all_videos()
