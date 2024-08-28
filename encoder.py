import os
import subprocess

from constants import INPUT_FOLDER, OUTPUT_FOLDER, HANDBRAKE_CLI_PATH

def process_all_videos():
    files = os.listdir(INPUT_FOLDER)
    for file in files:
        input_file_path = os.path.join(INPUT_FOLDER, file)
        output_file_path = os.path.join(OUTPUT_FOLDER, os.path.splitext(file)[0] + ".mkv")
        encode_video(input_file_path, output_file_path)

def encode_video(input_file, output_file):
    """
    Encodes a video file using HandBrakeCLI.

    Args:
        input_file (str): Path to the input video file.
        output_file (str): Path to save the encoded output video file.
    """

    # Ensure the output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

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
        '--audio-lang-list', 'deu,eng',
        '--aname', 'Deutsch,English',
        '--first-audio',
        '--aencoder', 'av_aac',
        '--audio-copy-mask','aac,ac3',
        '--audio-fallback', 'av_aac',
        '--mixdown', 'dpl1',
        '--subtitle-lang-list', 'deu,eng',
        '--subname', 'Deutsch,English',
        '--first-subtitle',
        '--aq', '5',
        '--multi-pass',
        '--turbo',
        '--format', 'av_mkv'
    ]

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while encoding {input_file}: {e}")
    except FileNotFoundError:
        print("HandBrakeCLI is not installed or not found in the system path.")
    finally:
        print(f"Successfully encoded {input_file} to {output_file}")