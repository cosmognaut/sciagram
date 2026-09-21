"""CLI implementation for `sciagram`

This module contains the `sciagram` command-line interface's implementation. `sciagram` internally
uses the `argparse` module for interacting with the command-line. It's a media-extension agnostic tool
which can convert any media to ASCII art.

Typical usage example:
    `sciagram /path/to/media.ext --color --size=fit --method=luminosity`
"""
import io
import os
import sys
import argparse
from PIL import Image
import urllib.request
from sciagram.errors import UnreadbleFormatError
from sciagram import ImageToASCII, AnimationToASCII, VideoToASCII

Image.init()
READBLE_FORMATS = [ext for ext, format in Image.EXTENSION.items() if format in Image.OPEN] 
VIDEO_FORMATS = [".mp4", ".webm"] # update this later

def _load_url(url: str) -> Image.Image:
    """Loads an image (for now) from a specified URL"""
    request = urllib.request.Request(url)
    request.add_header('User-Agent', 'urllib-example/0.1 (Contact: . . .)')
    with urllib.request.urlopen(request) as file:
        raw_bytes = io.BytesIO(file.read())
        image = Image.open(raw_bytes)
    return image

def _is_animated(filename: str) -> bool:
    """Returns a boolean indicating whether the file is animated or not"""
    # no support for animated GIF url fetching yet...
    if "http://" in filename or "https://" in filename:
        image = _load_url(filename)
    else:
        image = Image.open(filename)
    # if is_animated flag is present, it's animated
    if getattr(image, "is_animated", False):
        return True
    # is_animated flag is not present, but the number of frames is greater than one
    if getattr(image, "n_frames", 1) > 1:
        return True
    return False

def _get_extension(filename: str) -> str:
    """Returns the filename extension from a filename"""
    _, ext = os.path.splitext(filename)
    return ext.lower()

def main():
    if len(sys.argv) == 1:
        # means no arguments have been provided
        print("sciagram: You must specify an input file (or URL) as argument. \nTry 'sciagram --help' for more information.")
        return
    # means some arguments are provided
    parser = argparse.ArgumentParser(prog="sciagram", description="sciagram CLI for swift ASCII art generation", epilog="thank you, and have fun :)")
    parser.add_argument("filename", type=str, help="media URL you want to convert to ASCII art")
    parser.add_argument("-c", "--color", action="store_true", help="use this if you want the art to be colored")
    parser.add_argument("-m", "--method", type=str, choices=["average", "min_max", "luminosity"], default="average", help="method used to calculate the brightness of each pixel")
    parser.add_argument("-s", "--size", type=str, choices=["fit", "maxres"], default="fit", help="final art size; choose maxres for maximum qualtiy, and fit for fitting to current terminal dimensions")
    parser.add_argument("-l", "--loop", action="store_true", default=False, help="enable infinite looping in case of animations; this flag is NOT supported for images and videos")
    parser.add_argument("-d", "--debug", action="store_true", help="enable experimental debugging")

    args = parser.parse_args()
    ext = _get_extension(args.filename)
    if ext in VIDEO_FORMATS:
        if args.loop:
            print("sciagram: You cannot use the --loop flag with videos. \nTry 'sciagram --help' for more information.")
            return
        converter = VideoToASCII(url=args.filename, true_term=True, brightness_method=args.method, color=args.color, sizing=args.size)
    else:
        if ext not in READBLE_FORMATS:
            raise UnreadbleFormatError("The file format specified is not readble by Pillow.") 
        animated = _is_animated(args.filename)
        if animated:
            converter = AnimationToASCII(url=args.filename, true_term=True, brightness_method=args.method, color=args.color, sizing=args.size, loop=args.loop)
        else:
            if args.loop:
                print("sciagram: You cannot use the --loop flag with images. \nTry 'sciagram --help' for more information.")
                return
            converter = ImageToASCII(url=args.filename, true_term=True, brightness_method=args.method, color=args.color, sizing=args.size)
    converter.debug = args.debug
    converter.display()

if __name__ == "__main__":
    main()
