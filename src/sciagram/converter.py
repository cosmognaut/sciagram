"""Converters used to convert an image to ASCII art.

This module contains converts that one can use to convert an image (for now) to
ASCII art. The primary class used here is ImageToASCII for image to ASCII art conversions.

Typical usage example:
    converter = ImageToASCII(image_url="/path/to/image.jpg", true_term=True, brightness_method="luminosity")
    converter.print_to_term() # prints the art to the terminal

For detailed information about the attributes, refer to the class docstring.
"""

import shutil
from PIL import Image
from typing import Literal

# type PixelMatrix = list[list[tuple[int, int, int]]]
type CharacterMatrix = list[list[str]]

class ImageToASCII:
    """This class models an image to ASCII art converter.

    Converts any image (via a provided URL) to ASCII art ready to be printed to the terminal.

    Attributes:
        image_url: string URL for the image to be converted
        true_term: boolean that dictates whether to resize the image according to current terminal size
        brightness_method: string method name used to calculate the brightness
        sequence: the string sequence of ASCII characters to be used

    For defaults, refer to the initialisation docstring.
    """

    def __init__(self, image_url: str, true_term: bool = True, brightness_method: Literal["average", "min_max", "luminosity"] = "average", sequence: str = "`^\",:;Il!i~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"):
        """
        Initialises the image to ASCII art converter.

        Parameters/Options:
            image_url: a string URL for the image you want to convert.
            true_term: boolean for if you want to resize the image according to your current terminal size, defaults to True. Always use True if you want best representation catered to your terminal size.
            brightness_method: method to calculate brightness; choose "luminosity" for best quality art, as that's optimised for the human eye's receptors. Defaults to "average".
            sequence: sequence for ASCII characters to be used, defaults to a standard 65 character sequence ranked by brightness.
        """
        self.image_url = image_url
        self.true_term = true_term
        self.brightness_method = brightness_method
        self.sequence = sequence

    def _calculate_brightness(self, red: int, green: int, blue: int) -> float:
        """Calculate the brightness for given RGB values"""
        if self.brightness_method == "average":
            return (red + green + blue) / 3
        elif self.brightness_method == "min_max":
            return ((max(red, green, blue) + min(red, green, blue)) / 2)
        # elif self.brightness_method == "luminosity":
        else:
            return (0.21 * red + 0.72 * green + 0.07 * blue)

    def _brightness_to_ascii(self, brightness: float) -> str:
        """Returns an ASCII character for any brightness value"""
        brightness_number = round((brightness/255) * (len(self.sequence) - 1))
        return self.sequence[brightness_number]

    def _load_image(self) -> Image.Image:
        """Load an image and optionally resize it to then default terminal cell dimensions (1 char per cell corresponding to 1px)"""
        image = Image.open(self.image_url)
        size = shutil.get_terminal_size(fallback=(80, 24)) # 80, 24 is the default fallback, I am just making it explicit here.
        # size = os.get_terminal_size()
        if self.true_term:
            term_cols, term_rows = size.columns, size.lines
            # effective_height = round(term_rows * 0.5) # aspect ratio correction is taken to be 0.5
            image = image.resize((term_cols, term_rows))
        # print("Successfully loaded image!")
        # print(f"Image size: {image.size}")
        return image

    def convert(self) -> CharacterMatrix:
        """
        Primary method for converting an image to an ASCII art representation.
        
        Parameters:
            none

        Returns:
            a two dimensional matrix containing ASCII characters for every pixel of the image.
        """
        image = self._load_image()
        flat_data = image.get_flattened_data()
        final_matrix = []
        image_height = image.height
        image_width = image.width
        for y in range(image_height):
            character_row = []
            for x in range(image_width):
                pixel = flat_data[(y * image_width) + x]
                assert type(pixel) is tuple # for linter errors
                red = pixel[0]
                green = pixel[1]
                blue = pixel[2]
                pixel_brightness = self._calculate_brightness(red, green, blue)
                character_row.append(self._brightness_to_ascii(pixel_brightness))
            final_matrix.append(character_row)
        return final_matrix

    def print_to_term(self):
        """
        Method for printing the generated ASCII art to terminal. Internally uses the convert() method.

        Parameters:
            none

        Returns:
            nothing, just prints the generated ASCII art to your terminal screen.
        """
        ascii_matrix = self.convert()
        for row in ascii_matrix:
            for char in row:
                print(char, end="")
            print()

if __name__ == "__main__":
    converter = ImageToASCII(image_url="/home/ishu/Projects/sciagram/src/sciagram/cosmog.jpg", true_term=True, brightness_method="luminosity")
    # final_mat = converter.convert()
    converter.print_to_term()
