import subprocess
from .exceptions import FFMPEGNotInstalled

def _extract_attribute_data(msg, attributes):
    attribute_data = msg
    # Skip the first attribute since it is the topic name
    for attr in attributes[1:]:
        attribute_data = getattr(attribute_data, attr)
    return attribute_data


def convert_to_webm(video_name):
    """Convert a video to webm format using ffmpeg and save it under same name with .webm extension"""

    # Fail fast if ffmpeg is not installed
    try:
        subprocess.run(["ffmpeg", "-version"], check=True)
    except FileNotFoundError:
        raise FFMPEGNotInstalled(
            "ffmpeg is not installed. Please install ffmpeg to convert videos to webm format."
        )

    ffmpeg = [
        "ffmpeg",
        "-i",
        video_name,
        "-c:v",
        "libvpx-vp9",
        "-crf",
        "30",
        "-b:v",
        "0",
        "-y",
        video_name.split(".")[0] + ".webm",
    ]
    subprocess.run(ffmpeg)

