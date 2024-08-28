from encoder import process_all_videos

if __name__ == '__main__':
    try:
        process_all_videos()
    except Exception as e:
        # log error
        print(e)
