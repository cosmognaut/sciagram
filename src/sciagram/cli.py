import argparse
from typing import Literal
from sciagram import ImageToASCII

type brightness_options = Literal["average", "minmax", "luminosity"]

def main():
    parser = argparse.ArgumentParser(prog="sciagram", description="sciagram CLI for swift ASCII art generation", epilog="thank you, and have fun :)")

    parser.add_argument("filename", type=str, help="image URL (local for now) you want to convert to ASCII art")
    parser.add_argument("-c", "--color", action="store_true", help="use this if you want the art to be colored")
    parser.add_argument("-m", "--method", type=str, choices=["average", "min_max", "luminosity"], default="average", help="method used to calculate the brightness of each pixel")
    parser.add_argument("-s", "--size", type=str, choices=["fit", "maxres"], default="fit", help="final art size; choose maxres for maximum qualtiy, and fit for fitting to current terminal dimensions")
    parser.add_argument("-d", "--debug", action="store_true", help="enable debugging")

    args = parser.parse_args()
    if not args.color:
        converter = ImageToASCII(image_url=args.filename, brightness_method=args.method, sizing=args.size)
    else:
        converter = ImageToASCII(image_url=args.filename, color=True, brightness_method=args.method, sizing=args.size)

    if args.debug:
        converter.debug = True
    converter.print_to_term()

if __name__ == "__main__":
    main()
