"""Converters used to convert an image to ASCII art.

This module contains converts that one can use to convert an image (for now) to
ASCII art. The primary class used here is ImageToASCII for image to ASCII art conversions.

Typical usage example:
    converter = ImageToASCII(image_url="/path/to/image.jpg", true_term=True, brightness_method="luminosity")
    converter.print_to_term() # prints the art to the terminal

For detailed information about the attributes, refer to the class docstring.
"""

import os
import shutil
from PIL import Image
from typing import Literal

type CharacterMatrix = list[list[str]]

class ImageToASCII:
    """This class models an image to ASCII art converter.

    Converts any image (via a provided URL) to ASCII art ready to be printed to the terminal.

    Attributes:
        image_url: string URL for the image to be converted
        true_term: boolean that dictates whether to resize the image according to current terminal size
        brightness_method: string method name (formula) used to calculate the brightness
        color: boolean indicating whether the final output should be colored or not
        sizing: string art sizing sequence to be followed
        sequence: the string sequence of ASCII characters to be used; defaults to a standard 65 characters ranked by brightness
        cell_ratio: ratio between a terminal cell's width to its height; defaults to 0.4

    For defaults on instance creation, refer to the initialisation docstring.
    """

    def __init__(self, image_url: str, true_term: bool = True, brightness_method: Literal["average", "min_max", "luminosity"] = "average", color: bool = False, sizing: Literal["fit", "maxres"] = "fit"):
        """
        Initialises the image to ASCII art converter.

        Parameters/Options:
            image_url: a string URL for the image you want to convert.
            true_term: boolean for if you want to resize the image according to your current terminal size, defaults to True. Always use True if you want best representation catered to your terminal size.
            brightness_method: method to calculate brightness; choose "luminosity" for best quality art, as that's optimised for the human eye's receptors. Defaults to "average".
            color: boolean for if you want the final output to be colored or not. 24bit colors (8R, 8G, 8B) are used here ; please check if your terminal emulator supports this first. Defaults to False, i.e. black and white output.
            sizing: sizing option for the rendered art, choose "fit" if you want to fit it to the current terminal context, and "maxres" if you want maximum resolution at the cost of scrolling downwards. Defaults to "fit".
        """
        self.image_url = image_url
        self.true_term = true_term
        self.brightness_method = brightness_method
        self.color = color
        self.sizing = sizing
        self.sequence = "`^\",:;Il!i~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
        self.cell_ratio = 0.4

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

    def _fit_image(self, image_width: float, image_height: float, terminal_width: int, terminal_height: int) -> tuple[int, int]:
        """Returns a scale-preserved (width, height) tuple that preserves the original image's aspect ratio"""
        scaling_factor = min((terminal_height/(image_height * self.cell_ratio)), (terminal_width/image_width))
        target_width = round(image_width * scaling_factor)
        target_height = round(image_height * scaling_factor * self.cell_ratio)
        return (target_width, target_height)

    def _maxres_image(self, image_width: float, image_height: float, terminal_width: int, terminal_height: int) -> tuple[int, int]:
        """Returns a maximum resolution (width, height) tuple according to width or height maximisations"""
        if terminal_width > terminal_height:
            target_width = terminal_width 
            target_height = round((image_height/image_width) * terminal_width * self.cell_ratio)
        else:
            target_height = terminal_height
            target_width = round((image_width/(image_height * self.cell_ratio)) * terminal_height)
        return (target_width, target_height)

    def _load_image(self) -> Image.Image:
        """Load an image and optionally resize it to then default terminal cell dimensions (1 char per cell corresponding to 1px)"""
        image = Image.open(self.image_url)
        # size = shutil.get_terminal_size(fallback=(80, 24)) # 80, 24 is the default fallback, I am just making it explicit here.
        size = os.get_terminal_size(0) # 0 because pipe could be triggered too
        # print(f"Input aspect ratio: {image.width/image.height}")
        if self.true_term:
            term_cols, term_rows = size.columns, size.lines
            # print(f"Terminal width: {term_cols}, terminal height: {term_rows}")
            if self.sizing == "fit":
                image = image.resize(self._fit_image(image.width, image.height, term_cols, term_rows))
            elif self.sizing == "maxres":
                image = image.resize(self._maxres_image(image.width, image.height, term_cols, term_rows))

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
                if not self.color:
                    # if color is not enabled, simply append the ascii character itself
                    character_row.append(self._brightness_to_ascii(pixel_brightness))
                else:
                    # if color is enabled, append the ascii character along with 24-bit color sequence
                    character_row.append(f"\033[38;2;{red};{green};{blue}m{self._brightness_to_ascii(pixel_brightness)}")
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
    converter = ImageToASCII(image_url="/home/ishu/Downloads/example.gif", true_term=True, brightness_method="luminosity", color=True, sizing="maxres")
    # final_mat = converter.convert()
    converter.print_to_term()
