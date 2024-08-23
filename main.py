import os
import time

#WATCH_FOLDER = "PATCH_TO_WATCH_FOLDER"
WATCH_FOLDER = "/home/marc/Videos"

def monitor_folder():
    while True:
        time.sleep(60 * 60)
        files = os.listdir(WATCH_FOLDER)
        for file in files:
            print(file)


if __name__ == '__main__':
    try:
        monitor_folder()
    except Exception as e:
        # log error
        print(e)