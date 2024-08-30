import logging
import os
import subprocess

import pymediainfo

from constants import INPUT_FOLDER, OUTPUT_FOLDER, HANDBRAKE_CLI_PATH, PROCESSED_FILES_PATH

logger = logging.getLogger(__name__)


def process_all_videos():
    already_processed = read_processed_files()
    files = os.listdir(INPUT_FOLDER)
    for file in files:
        input_file_path = os.path.join(INPUT_FOLDER, file)
        if os.path.isfile(input_file_path) and input_file_path not in already_processed:
            logger.info(f"New file found at {os.path.splitext(input_file_path)[0]}; start encoding now...")
            output_file_path = os.path.join(OUTPUT_FOLDER, os.path.splitext(file)[0] + ".mkv")
            encode_video(input_file_path, output_file_path)
        else:
            logger.info(f"Already processed file found in path: {os.path.splitext(input_file_path)[0]}")


def read_processed_files():
    if os.path.exists(PROCESSED_FILES_PATH):
        with open(PROCESSED_FILES_PATH, 'r') as f:
            return set(line.strip() for line in f)
    else:
        return set()


def write_processed_file(file):
    with open(PROCESSED_FILES_PATH, 'a') as f:
        f.write(f"{file}\n")


def get_audio_streams(input_file):
    media_info = pymediainfo.MediaInfo.parse(input_file)
    audio_tracks = []

    for track in media_info.tracks:
        if track.track_type == "Audio":
            audio_info = {
                "track_id": track.track_id,
                "format": track.format,
                "language": track.language,
            }
            audio_tracks.append(audio_info)

    return audio_tracks


def encode_video(input_file, output_file):
    """
    Encodes a video file using HandBrakeCLI.

    Args:
        input_file (str): Path to the input video file.
        output_file (str): Path to save the encoded output video file.
    """

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Create indexes for selecting wanted audio streams
    audio_streams = get_audio_streams(input_file)
    indexEn = next((i for i, item in enumerate(audio_streams) if item['language'] == 'en'), -1)
    indexDe = next((i for i, item in enumerate(audio_streams) if item['language'] == 'de'), -1)

    # HandBrake settings for a pal dvd
    command = [
        HANDBRAKE_CLI_PATH,
        '--input', input_file,
        '--output', output_file,
        '--encoder', 'x265',
        '--encoder-preset', 'medium',
        '--encoder-profile', 'main10',
        '--quality', '17',
        '--vfr',
        '--unsharp-tune', 'fine',
        '--hqdn3d', 'light',
        '--width', '720',
        '--height', '576',
        '--auto-anamorphic',
        '--aencoder', 'av_aac',
        '--audio', f'{str(indexDe + 1)},{str(indexEn + 1)}',
        '--aname', 'Deutsch,English',
        '--mixdown', 'dpl1',
        '--subtitle-lang-list', 'deu,eng',
        '--first-subtitle',
        '--subname', 'Deutsch,English',
        '--aq', '5',
        '--markers',
        '--multi-pass',
        '--turbo',
        '--format', 'av_mkv'
    ]

    try:
        subprocess.run(command, check=True)
        write_processed_file(input_file)
        logger.info(f"Successfully encoded {input_file} to {output_file}")
    except subprocess.CalledProcessError as e:
        logger.error(f"An error occurred while encoding {input_file}: {e}")
    except FileNotFoundError:
        logger.warning("HandBrakeCLI is not installed or not found in the system path.")
