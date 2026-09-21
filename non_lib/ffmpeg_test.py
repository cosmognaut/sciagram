import io
import subprocess
from PIL import Image
from video import get_video_data
from sciagram import ImageToASCII

# ffmpeg -i video.mp4 -f rawvideo -pix_fmt rgb24 -s {width}x{height} -
VIDEO_URL = "/home/ishu/Downloads/demo.mp4" # size 852, 480
VIDEO_URL = "/home/ishu/Downloads/short.mp4"

width, height, frame_rate = get_video_data(VIDEO_URL)

process = subprocess.Popen([
    "ffmpeg",
    "-i",
    VIDEO_URL,
    "-f",
    "rawvideo",
    "-pix_fmt",
    "rgb24",
    "-s",
    f"{width}x{height}",
    "-",
], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

# if frames per second is 30, 1 second = 30 frames; then one frame = (1/30) seconds.

while True:
    try:
        raw_bytes = process.stdout.read(width * height * 3) # 852 x 480 x 3 as in rg24 there are 3 bytes (24 bits; 8 for each R G and B)
        frame = Image.frombytes(mode="RGB", data=raw_bytes, size=(width, height))
        frame.save("test.png")
        artist = ImageToASCII(url="./test.png", color=True)
        artist.display()
    except Exception:
        # not enough image data
        break
