from encoder import process_all_videos

MONITORING = False

def monitor_folder():
    while True:
        process_all_videos()

if __name__ == '__main__':
    try:
        if MONITORING:
            monitor_folder()
        else:
            process_all_videos()
    except Exception as e:
        # log error
        print(e)
