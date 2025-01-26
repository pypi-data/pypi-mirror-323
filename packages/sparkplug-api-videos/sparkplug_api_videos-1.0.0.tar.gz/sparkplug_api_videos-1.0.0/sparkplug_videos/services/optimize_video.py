# python
import subprocess


def optimize_video(
    source: str,
    filename: str,
) -> str:
    filepath = f"/tmp/{filename}.mp4"  # noqa: S108

    # Each argument must be it's own list item.
    # https://stackoverflow.com/a/23681211/2407209
    parts = [
        "ffmpeg",
        "-i",
        source,
        "-y",
        "-vcodec",
        "h264",
        "-acodec",
        "aac",
        "-crf",
        "28",
        "-strict",
        "-2",
        "-vf",
        "fps=fps=30,scale=-2:720",
        filepath,
    ]

    subprocess.Popen(parts).wait()  # noqa: S603
    return filepath
