import io
import subprocess
from sciagram import ImageToASCII
from subprocess import TimeoutExpired
from PIL import Image, ImageSequence

# ffmpeg -i video.mp4 -f rawvideo -pix_fmt rgb24 -s {width}x{height} -
VIDEO_URL = "/home/ishu/Downloads/demo.mp4" # size 852, 480
process = subprocess.Popen([
    "ffmpeg",
    "-i",
    VIDEO_URL,
    "-f",
    "rawvideo",
    "-pix_fmt",
    "rgb24",
    "-s",
    "852x480",
    "-",
], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

# width is set to be 100, height is 50.

# I want to read frame_bytes.
# let me read the final bytes first
raw_bytes = process.stdout.read(1226880) # 852 x 480 x 3 as in rg24 there are 3 bytes (24 bits; 8 for each R G and B)
# kill the process after reading the first frame's bytes
process.kill()
frame = Image.frombytes(mode="RGB", data=raw_bytes, size=(852,480))
frame.save("test.png")
artist = ImageToASCII(url="./test.png", color=True)
artist.display()


# why does conversion fail when I don't pass the read method? like what the fuck? broken pipe is what I get.
# print(type(process.stdout)) # buffered reader.
# raw_bytes = process.stdout
# read_data = io.BytesIO(raw_bytes)
# try:
#     sequence = Image.open(read_data)
#     DURATIONS = []
#     for frame in ImageSequence.Iterator(sequence):
#         frame_duration = frame.info['duration']
#         DURATIONS.append(frame_duration)
#     print(DURATIONS)
# except Exception as e:
#     print(f"Error: {e}")
