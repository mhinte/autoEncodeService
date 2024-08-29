import logging

from encoder import process_all_videos

logger = logging.getLogger(__name__)
MONITORING = False


def monitor_folder():
    logger.info("Started monitoring folder...")
    while True:
        process_all_videos()


if __name__ == '__main__':
    FORMAT = '%(asctime)s - %(levelname)s : %(message)s'
    logging.basicConfig(filename='logs/encoder.log', level=logging.INFO, format=FORMAT)
    try:
        if MONITORING:
            monitor_folder()
        else:
            process_all_videos()
    except Exception as e:
        # log error
        print(e)
