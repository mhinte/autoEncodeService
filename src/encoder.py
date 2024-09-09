"""Module providing the logic for handling the encoding of videos."""

import logging
import os
import shutil
import subprocess
from typing import List, Set

import pymediainfo

from src.helper.constants import (INPUT_FOLDER, OUTPUT_FOLDER,
                                  HANDBRAKE_CLI_PATH, PROCESSED_FILES_PATH, SUBTITLE_CRITERIA, NETWORK_FOLDER_PATH)

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
            logger.info("New file found at %s.",
                        os.path.splitext(input_file_path)[0])
            output_file_path = os.path.join(OUTPUT_FOLDER, os.path.splitext(file)[0] + ".mkv")
            encode_video(input_file_path, output_file_path)
            # copy_to_network(output_file_path)
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


def get_audio_indices(input_file: str, languages: List[str] = None, first_only: bool = True) -> str:
    """
    Returns indices of audio streams matching specified languages.

    Args:
        input_file (str): Path to the video file.
        languages (List[str], optional): Language codes to match. Defaults to ['de', 'en'].
        first_only (bool, optional): If True, returns only the first match per language.

    Returns:
        str: Comma-separated indices of matching audio streams or an empty string if none.
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

    if not audio_tracks:
        logger.warning('No audio tracks found in the media file: %s', input_file)
        return ""

    # Collect indices of audio tracks matching the specified languages
    indices = []

    # Process languages in the order they are specified in the input list
    for lang in languages:
        found = False
        for i, track in enumerate(audio_tracks):
            track_lang = getattr(track, 'language', None)
            if track_lang == lang:
                indices.append(str(i + 1))  # Append the 1-based index
                if first_only:
                    found = True
                    break  # Stop searching after the first match for this language
        if first_only and found:
            continue  # Move to the next language if first_only is True

    return ','.join(indices)


def get_subtitles(input_file):
    """
    Extracts and filters subtitle tracks from a media file based on predefined criteria.

    Parameters:
    - input_file (str): Path to the media file.

    Returns:
    - list of dict: Filtered subtitles with details like track number,
        language, size, proportion, default status, priority, and criterion name.

    Raises:
    - FileNotFoundError: Logs error if file is not found.
    """

    try:
        media_info = pymediainfo.MediaInfo.parse(input_file)
        text_tracks = media_info.text_tracks
    except FileNotFoundError:
        logger.error('Input file not found: %s', input_file)
        return ""

    subtitle_list = []
    criteria_status = {criterion["name"]: False for criterion in SUBTITLE_CRITERIA}

    for track in text_tracks:
        subtitle_info = {
            "track_nr": int(track.stream_identifier) + 1,
            "language": track.language,
            "stream_size": track.stream_size,
            "proportion": float(track.proportion_of_this_stream) * 1000,
            "default": track.default,
        }

        for criterion in SUBTITLE_CRITERIA:
            if criterion["condition"](subtitle_info) and not criteria_status[criterion["name"]]:
                subtitle_info["default"] = criterion["default"]
                subtitle_info['priority'] = criterion["priority"]
                subtitle_info['name'] = criterion["name"]
                subtitle_list.append(subtitle_info)
                criteria_status[criterion["name"]] = True
                break

    subtitle_list.sort(key=lambda x: x['priority'])
    logger.debug("Using these subtitles for encoding: %s", subtitle_list)

    return subtitle_list


def add_subtitle_command(command, subtitles):
    """
    Adds subtitle-related options to a HandBrake CLI command based on the provided subtitles.

    Parameters:
    - command (list): The initial list of command-line arguments for HandBrake.
    - subtitles (list of dict): A list of subtitle dictionaries where each dictionary
    contains information about a subtitle track.
      Each dictionary is expected to have the following keys:
      - 'track_nr' (int): The track number of the subtitle.
      - 'name' (str): The name of the subtitle.

    Returns:
    - list: The updated command list with added subtitle options.
    """

    logger.debug("Check for subtitle options to add.")
    if not subtitles:
        logger.debug("No subtitles found, skipping analyse.")
        return command

    # Initialize subtitle command list
    subtitle_command = [
        '--subtitle-burned=none',
    ]

    # Variables to collect subtitle information
    subtitle_tracks = []
    subtitle_names = []

    # Collect subtitle track info
    for subtitle in subtitles:
        # Append track id
        subtitle_tracks.append(str(subtitle['track_nr']))

        # Append subtitle name
        subtitle_names.append(subtitle['name'])

    # Add collected subtitle tracks to command
    subtitle_command.extend(['--subtitle', ','.join(subtitle_tracks)])

    # Add collected subtitle names to command
    subtitle_command.extend(['--subname', ','.join(subtitle_names)])

    # Always set the first subtitle as the default
    subtitle_command.extend(['--subtitle-default', str(subtitles[0]['track_nr'])])

    # Extend the original command with the generated subtitle options
    command.extend(subtitle_command)
    logger.debug("Added subtitle options: %s", subtitle_command)

    return command


def copy_to_network(src_file):
    """
    WIP: basic implementation for copying the final video to a network drive

    works, but is slow
    """
    logger.debug("Checking connection to %s", NETWORK_FOLDER_PATH)
    if os.path.exists(NETWORK_FOLDER_PATH):
        logger.info("Connection to %s successful, starting upload of %s", NETWORK_FOLDER_PATH, src_file)
        shutil.copy(src_file, NETWORK_FOLDER_PATH)
        logger.info("File %s copied to network folder %s successfully!", src_file, NETWORK_FOLDER_PATH)
    else:
        logger.info("Connection to %s failed; skipping upload :(", NETWORK_FOLDER_PATH)


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
        '--quality', '17.5',
        '--vfr',
        '--crop-mode', ' auto',
        '--auto-anamorphic',
        '--lapsharp=light',
        '--hqdn3d=light',
        '--auto-anamorphic',
        '--aencoder', 'copy',
        '--audio-copy-mask', 'ac3,aac,eac3,truehd,dts,dtshd,flac',
        '--audio-fallback', 'av_aac',
        '--audio', audio_command,
        '--aname', 'Deutsch,English',
        '--native-language', 'deu',
        '--markers',
        '--turbo',
        '--format', 'av_mkv',
    ]

    extended_command = add_subtitle_command(command, get_subtitles(input_file))
    try:
        logger.info("Starting encoding with command: %s", extended_command)
        subprocess.run(extended_command, check=True)
        write_processed_file(input_file)
        logger.info("Successfully encoded %s to %s", input_file, output_file)
    except subprocess.CalledProcessError as e:
        logger.error("An error occurred while encoding %s: %s", input_file, e)
    except FileNotFoundError as err:
        logger.error("File not found: %s", err)
