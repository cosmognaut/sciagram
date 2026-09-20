import os
import sys
import time
import subprocess
from typing import Literal
from sciagram import ImageToASCII
from PIL import Image, ImageSequence

type CharacterMatrix = list[list[str]]

def _calculate_brightness(red: int, green: int, blue: int) -> float:
    """Calculate the brightness for given RGB values"""
    return (0.21 * red + 0.72 * green + 0.07 * blue)

def _brightness_to_ascii(brightness: float) -> str:
    """Returns an ASCII character for any brightness value"""
    sequence = "`^\",:;Il!i~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
    brightness_number = round((brightness/255) * (len(sequence) - 1))
    return sequence[brightness_number]

def convert(image: Image.Image, color: bool = True) -> CharacterMatrix:
    image = image.convert('RGB')
    flat_data = image.get_flattened_data()
    final_matrix = []
    image_height = image.height
    image_width = image.width
    for y in range(image_height):
        character_row = []
        for x in range(image_width):
            pixel = flat_data[(y * image_width) + x]
            assert type(pixel) is tuple
            red = pixel[0]
            green = pixel[1]
            blue = pixel[2]
            pixel_brightness = _calculate_brightness(red, green, blue)
            if not color:
                character_row.append(_brightness_to_ascii(pixel_brightness))
            else:
                character_row.append(f"\033[38;2;{red};{green};{blue}m{_brightness_to_ascii(pixel_brightness)}")
        final_matrix.append(character_row)
    return final_matrix

def print_to_term(image: Image.Image):
    ascii_matrix = convert(image)
    final_string = ""
    for row in ascii_matrix:
        for char in row:
            final_string += char
        final_string += "\n"
    sys.stdout.write(final_string)
    sys.stdout.write("\n")

URL = "/home/ishu/Downloads/cat.gif"
operating_system = os.name
with Image.open(URL) as im:
    # print(im.tile[0][0]) # should be "gif"
    frame_number = 0
    for frame in ImageSequence.Iterator(im):
        frame_duration = frame.info['duration']
        print_to_term(frame)
        time.sleep(frame_duration/1000) # milliseconds to seconds
        # now = time.time_ns()/10e5
        # timer = 0
        # while timer <= frame_duration:
        #     end = time.time_ns()/10e5
        #     timer = end - now
        # subprocess.run(["cls"] if operating_system == "nt" else ["clear"])
        sys.stdout.write("\033[H?25l")
        frame_number += 1
# print(f"Total frames: {frame_number}")
# i need to devise a way to print the image to the term and then clear the screen before the next image is rendered.
