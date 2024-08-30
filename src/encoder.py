"""Module providing the logic for handling the encoding of videos."""

import logging
import os
import subprocess
from typing import List, Dict, Set

import pymediainfo

from src.helper.constants import (INPUT_FOLDER, OUTPUT_FOLDER,
                                  HANDBRAKE_CLI_PATH, PROCESSED_FILES_PATH)

logger = logging.getLogger(__name__)


def process_all_videos() -> None:
    """
    Process all found videos in the input folder with the given handbrake settings.
    """
    already_processed = read_processed_files()
    files = os.listdir(INPUT_FOLDER)
    for file in files:
        input_file_path = os.path.join(INPUT_FOLDER, file)
        if os.path.isfile(input_file_path) and file not in already_processed:
            logger.info("New file found at %s; start encoding now...",
                        os.path.splitext(input_file_path)[0])
            output_file_path = os.path.join(OUTPUT_FOLDER, os.path.splitext(file)[0] + ".mkv")
            encode_video(input_file_path, output_file_path)
        else:
            logger.info("Already processed file %s in path: %s",
                        file, os.path.splitext(input_file_path)[0])


def read_processed_files() -> Set[str]:
    """
    Returns a list of all processed files found in the text file.
    """
    processed_files = set()
    if os.path.exists(PROCESSED_FILES_PATH):
        with open(PROCESSED_FILES_PATH, 'r', encoding="utf-8") as f:
            processed_files = {line.strip() for line in f}
    return processed_files


def write_processed_file(file_path: str) -> None:
    """
    Updates the processed files file.
    """
    with open(PROCESSED_FILES_PATH, 'a', encoding="utf-8") as f:
        f.write(f"{os.path.basename(file_path)}\n")


def get_audio_streams(input_file: str) -> List[Dict[str, str]]:
    """
    Returns a list of all audio streams.
    """
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


def encode_video(input_file: str, output_file: str) -> None:
    """
    Encodes a video file using HandBrakeCLI.

    Args:
        input_file (str): Path to the input video file.
        output_file (str): Path to save the encoded output video file.
    """

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    audio_streams = get_audio_streams(input_file)

    indices = []
    index_de = next((i for i, item in enumerate(audio_streams) if item['language'] == 'de'), -1)
    if index_de != -1:
        indices.append(str(index_de + 1))

    index_en = next((i for i, item in enumerate(audio_streams) if item['language'] == 'en'), -1)
    if index_en != -1:
        indices.append(str(index_en + 1))

    audio_command = ','.join(indices)

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
        '--audio', audio_command,
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

    # Remove empty parameters
    command = [param for param in command if param]

    try:
        subprocess.run(command, check=True)
        write_processed_file(input_file)
        logger.info("Successfully encoded %s to %s", input_file, output_file)
    except subprocess.CalledProcessError as e:
        logger.error("An error occurred while encoding %s: %s", input_file, e)
    except FileNotFoundError as err:
        logger.error("File not found: %s", err)
