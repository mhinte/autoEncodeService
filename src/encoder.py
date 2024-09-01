"""Module providing the logic for handling the encoding of videos."""

import logging
import os
import subprocess
from typing import List, Set

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


def get_audio_indices(input_file: str, languages: List[str] = None) -> str:
    """
    Retrieves indices of audio streams in the specified languages from a media file.

    Args:
        input_file (str): Path to the input video file.
        languages (List[str], optional): List of ISO 639-2 language codes to search for in the
        audio streams. Defaults to ['de', 'en'] if not provided.

    Returns:
        str: A comma-separated string of indices of the specified language audio streams,
            ordered by their appearance.
            Returns an empty string if no audio streams are found or an error occurs.

    Raises:
        FileNotFoundError: If the input file does not exist.
        ValueError: If there is an issue with retrieving or converting track information.

    Example:
        >>> get_audio_indices('path/to/video.mkv', ['de', 'en'])
        '1,2'
    """
    if languages is None:
        languages = ['de', 'en']

    try:
        media_info = pymediainfo.MediaInfo.parse(input_file)
        audio_tracks = media_info.audio_tracks
    except FileNotFoundError:
        logger.error('Input file not found: %s', input_file)
        return ""
    except ValueError as e:
        logger.error('Value error: %s', e)
        return ""

    # Collect indices of audio tracks matching the specified languages
    indices = [
        str(i + 1) for lang in languages
        for i, track in enumerate(audio_tracks)
        if getattr(track, 'language', None) == lang
    ]

    return ','.join(indices)


def encode_video(input_file: str, output_file: str) -> None:
    """
    Encodes a video file using HandBrakeCLI.

    Args:
        input_file (str): Path to the input video file.
        output_file (str): Path to save the encoded output video file.
    """

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    audio_command = get_audio_indices(input_file)

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
        '--aq', '4',
        '--native-language', 'deu',
        '--native-dub',
        '--subtitle-lang-list', 'deu,eng',
        '--first-subtitle',
        '--subname', 'Deutsch,English',
        '--subtitle-burned=none',
        '--subtitle-default=none',
        '--subtitle-forced',
        '--subtitle', 'scan',
        '--markers',
        '--multi-pass',
        '--turbo',
        '--format', 'av_mkv'
    ]

    try:
        subprocess.run(command, check=True)
        write_processed_file(input_file)
        logger.info("Successfully encoded %s to %s", input_file, output_file)
    except subprocess.CalledProcessError as e:
        logger.error("An error occurred while encoding %s: %s", input_file, e)
    except FileNotFoundError as err:
        logger.error("File not found: %s", err)
