import json
import subprocess

VIDEO_URL = "/home/ishu/Downloads/short.mp4"
# ffprobe -v error -select_streams v -of default=noprint_wrappers=1:nokey=1
#  -show_entries stream=width,height,r_frame_rate -of json
def get_video_data(video_url: str):
    """Get width, height, frame rate"""
    process = subprocess.Popen([
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        "-show_entries",
        "stream=width,height,r_frame_rate",
        "-of",
        "json",
        video_url,
    ], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

    get = process.stdout.read()
    json_output = json.loads(get)
    width = json_output['streams'][0]['width']
    height = json_output['streams'][0]['height']
    raw_frame_rate = json_output['streams'][0]['r_frame_rate']
    num, deno = (int(char) for char in raw_frame_rate.split('/'))
    frame_rate = round(num/deno)
    return (width, height, frame_rate)
