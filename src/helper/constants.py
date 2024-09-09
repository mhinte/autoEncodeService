"""Module providing static variables."""

INPUT_FOLDER = "videos\\input\\"
OUTPUT_FOLDER = "videos\\output\\"
PROCESSED_FILES_PATH = "temp/processed_files.txt"
HANDBRAKE_CLI_PATH = "src/HandBrakeCLI.exe"
NETWORK_FOLDER_PATH = "PATH_TO_NETWORK_FOLDER"

SUBTITLE_CRITERIA = [
    {
        "name": "Fremdsprache",
        "priority": 1,
        "condition": lambda subtitle_info: subtitle_info["language"] == 'de'
                                           and subtitle_info["proportion"] < 0.1,
        "default": "Yes",
    },
    {
        "name": "Deutsch",
        "priority": 2,
        "condition": lambda subtitle_info: subtitle_info["language"] == 'de'
                                           and subtitle_info["proportion"] < 1,
        "default": "No",
    },
    {
        "name": "English",
        "priority": 3,
        "condition": lambda subtitle_info: subtitle_info["language"] == 'en'
                                           and subtitle_info["proportion"] < 1,
        "default": "No",
    }
]
