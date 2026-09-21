"""Converters used to convert an image or an animation to ASCII art.

This module contains converters that one can use to convert an image or an animation to
ASCII art. The primary class used here is ImageToASCII for image to ASCII art conversions, and AnimationToASCII for
animation to ASCII art conversions.

Typical usage example:
    converter = ImageToASCII(image_url="/path/to/image.jpg", true_term=True, brightness_method="luminosity")
    converter.print_to_term() # prints the art to the terminal

For detailed information about the attributes, refer to the class docstring.
"""
import io
import os
import sys
import time
import shutil
import urllib.request
from typing import Literal
from PIL import Image, ImageSequence

type CharacterMatrix = list[list[str]]
type FrameData = list[tuple[Image.Image, float]]

# video support addition?
class GenericConverter:
    """This class models an generic media to ASCII art converter.

    Converts any media (via a provided URL) to ASCII art ready to be printed to the terminal.

    Attributes:
        url: string URL for the media to be converted
        true_term: boolean that dictates whether to resize the media according to current terminal size
        brightness_method: string method name (formula) used to calculate the brightness
        color: boolean indicating whether the final output should be colored or not
        sizing: string art sizing sequence to be followed
        sequence: the string sequence of ASCII characters to be used; defaults to a standard 65 characters ranked by brightness
        cell_ratio: ratio between a terminal cell's width to its height; defaults to 0.4
        debug: boolean to set debugging on or off; debugging enables print statements that tell you the size of your terminal, etc.
    """
    def __init__(self, url: str, true_term: bool = True, brightness_method: Literal["average", "min_max", "luminosity"] = "average", color: bool = False, sizing: Literal["fit", "maxres"] = "fit"):
        """
        Initialises a generic converter.

        Parameters/Options:
            url: a string URL for the media you want to convert.
            true_term: boolean for if you want to resize the media ccording to your current terminal size, defaults to True. Always use True if you want best representation catered to your terminal size.
            brightness_method: method to calculate brightness; choose "luminosity" for best quality art, as that's optimised for the human eye's receptors. Defaults to "average".
            color: boolean for if you want the final output to be colored or not. 24bit colors (8R, 8G, 8B) are used here ; please check if your terminal emulator supports this first. Defaults to False, i.e. black and white output.
            sizing: sizing option for the rendered art, choose "fit" if you want to fit it to the current terminal context, and "maxres" if you want maximum resolution at the cost of scrolling downwards. Defaults to "fit".
        """
        self.url = url
        self.true_term = true_term
        self.brightness_method = brightness_method
        self.color = color
        self.sizing = sizing
        self.sequence = "`^\",:;Il!i~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
        self.cell_ratio = 0.4
        self.debug = False

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

    def _load_url(self, url: str) -> Image.Image:
        """Loads an image (for now) from a specified URL"""
        request = urllib.request.Request(url)
        request.add_header('User-Agent', 'urllib-example/0.1 (Contact: . . .)')
        with urllib.request.urlopen(request) as file:
            raw_bytes = io.BytesIO(file.read())
            image = Image.open(raw_bytes)
        return image

    def _convert_image(self, image: Image.Image) -> CharacterMatrix:
        """
        Generic method or converting an image to return a two-dimensional matrix containing ASCII characters for each pixel in the provided image. 
        If the image is not in RGB mode, we manually convert it to RGB here.

        Parameters:
            image: the image to be converted

        Returns:
            a two-dimensional matrix containing ASCII characters for each pixel in the provided image
        """
        if image.mode != "RGB":
            image = image.convert('RGB')
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

class ImageToASCII(GenericConverter):
    """This class models an image to ASCII art converter.

    Converts any image (via a provided URL) to ASCII art ready to be printed to the terminal.

    Attributes:
        url: string URL for the image to be converted
        true_term: boolean that dictates whether to resize the image according to current terminal size
        brightness_method: string method name (formula) used to calculate the brightness
        color: boolean indicating whether the final output should be colored or not
        sizing: string art sizing sequence to be followed
        sequence: the string sequence of ASCII characters to be used; defaults to a standard 65 characters ranked by brightness
        cell_ratio: ratio between a terminal cell's width to its height; defaults to 0.4
        debug: boolean to set debugging on or off; debugging enables print statements that tell you the size of your terminal, etc.

    For defaults on instance creation, refer to the initialisation docstring.
    """

    def __init__(self, url: str, true_term: bool = True, brightness_method: Literal["average", "min_max", "luminosity"] = "average", color: bool = False, sizing: Literal["fit", "maxres"] = "fit"):
        """
        Initialises the image to ASCII art converter.

        Parameters/Options:
            url: a string URL for the image you want to convert.
            true_term: boolean for if you want to resize the image according to your current terminal size, defaults to True. Always use True if you want best representation catered to your terminal size.
            brightness_method: method to calculate brightness; choose "luminosity" for best quality art, as that's optimised for the human eye's receptors. Defaults to "average".
            color: boolean for if you want the final output to be colored or not. 24bit colors (8R, 8G, 8B) are used here ; please check if your terminal emulator supports this first. Defaults to False, i.e. black and white output.
            sizing: sizing option for the rendered art, choose "fit" if you want to fit it to the current terminal context, and "maxres" if you want maximum resolution at the cost of scrolling downwards. Defaults to "fit".
        """
        super().__init__(url=url, true_term=true_term, brightness_method=brightness_method, color=color, sizing=sizing)

    def _load_image(self) -> Image.Image:
        """Load an image and optionally resize it to the default terminal cell dimensions (1 char per cell corresponding to 1px)"""
        # if https is there, it means it's a web url.
        # this WILL misfire on local images with http in their name
        if "http://" in self.url or "https://" in self.url:
            image = self._load_url(self.url)
        else:
            image = Image.open(self.url)
        if self.debug:
            print(f"Successfully loaded image of size {image.width}x{image.height}")
        # size = shutil.get_terminal_size(fallback=(80, 24)) # 80, 24 is the default fallback, I am just making it explicit here.
        size = os.get_terminal_size(0) # 0 because pipe could be triggered too
        # print(f"Input aspect ratio: {image.width/image.height}")
        if self.true_term:
            term_cols, term_rows = size.columns, size.lines
            if self.debug:
                print(f"Terminal width: {term_cols}, terminal height: {term_rows}")
            if self.sizing == "fit":
                image = image.resize(self._fit_image(image.width, image.height, term_cols, term_rows))
            elif self.sizing == "maxres":
                image = image.resize(self._maxres_image(image.width, image.height, term_cols, term_rows))
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
        final_matrix = self._convert_image(image)
        return final_matrix

    def display(self):
        """
        Method for displaying the generated ASCII art to terminal. Internally uses the convert() method.

        Parameters:
            none

        Returns:
            nothing, just displays the generated ASCII art to your terminal screen.
        """
        ascii_matrix = self.convert()
        for row in ascii_matrix:
            for char in row:
                print(char, end="")
            print()

class AnimationToASCII(GenericConverter):
    """This class models an animated sequence to ASCII art converter.

    Converts any animation (via a provided URL) to ASCII art ready to be printed to the terminal.

    Attributes:
        url: string URL for the sequence to be converted
        true_term: boolean that dictates whether to resize the image according to current terminal size
        brightness_method: string method name (formula) used to calculate the brightness
        color: boolean indicating whether the final output should be colored or not
        sizing: string art sizing sequence to be followed
        sequence: the string sequence of ASCII characters to be used; defaults to a standard 65 characters ranked by brightness
        cell_ratio: ratio between a terminal cell's width to its height; defaults to 0.4
        debug: boolean to set debugging on or off; debugging enables print statements that tell you the size of your terminal, etc.
        loop: boolean to set infinite looping to be enabled or not

    For defaults on instance creation, refer to the initialisation docstring.
    """

    def __init__(self, url: str, true_term: bool = True, brightness_method: Literal["average", "min_max", "luminosity"] = "average", color: bool = False, sizing: Literal["fit", "maxres"] = "fit", loop: bool = False):
        """
        Initialises the animation to ASCII art converter.

        Parameters/Options:
            url: a string URL for the sequence you want to convert.
            true_term: boolean for if you want to resize the image according to your current terminal size, defaults to True. Always use True if you want best representation catered to your terminal size.
            brightness_method: method to calculate brightness; choose "luminosity" for best quality art, as that's optimised for the human eye's receptors. Defaults to "average".
            color: boolean for if you want the final output to be colored or not. 24bit colors (8R, 8G, 8B) are used here ; please check if your terminal emulator supports this first. Defaults to False, i.e. black and white output.
            sizing: sizing option for the rendered art, choose "fit" if you want to fit it to the current terminal context, and "maxres" if you want maximum resolution at the cost of scrolling downwards. Defaults to "fit".
            loop: boolean for if you want the animation to loop endlessly.
        """
        # add loop boolean here later.
        super().__init__(url=url, true_term=true_term, brightness_method=brightness_method, color=color, sizing=sizing)
        self.loop = loop

    def _load_sequence(self) -> FrameData:
        """Load a sequence of frames and optionally resize them to the default terminal cell dimensions (1 char per cell corresponding to 1px)"""
        frame_data = []
        size = os.get_terminal_size(0)
        term_cols, term_rows = size.columns, size.lines

        if self.debug:
            print(f"Terminal width: {term_cols}, terminal height: {term_rows}")

        if "http://" in self.url or "https://" in self.url:
            animation = self._load_url(self.url)
        else:
            animation = Image.open(self.url)

        for frame in ImageSequence.Iterator(animation):
            frame_duration = frame.info['duration']
            if self.true_term:
                if self.sizing == "fit":
                    frame = frame.resize(self._fit_image(frame.width, frame.height, term_cols, term_rows))
                elif self.sizing == "maxres":
                    frame = frame.resize(self._maxres_image(frame.width, frame.height, term_cols, term_rows))
            frame_data.append((frame, frame_duration))
        return frame_data

    def convert(self) -> tuple[list[CharacterMatrix], list[float]]:
        """
        Primary method for converting a squence to an ASCII art representation.
        
        Parameters:
            none

        Returns:
            a list two dimensional matrices containing ASCII characters for every pixel of every frame in the sequence.
        """
        frame_data = self._load_sequence()
        character_matrices = []
        frame_durations = []
        for frame, duration in frame_data:
            character_matrices.append(self._convert_image(frame))
            frame_durations.append(duration)
        return (character_matrices, frame_durations)

    def _print_to_term(self, frame_matrices: list[CharacterMatrix], frame_durations: list[float]):
        """Internal method used to handle printing ASCII characters to the terminal screen; considers both looped and non-looped scenarios"""
        for ascii_matrix, duration in zip(frame_matrices, frame_durations):
            final_string = ""
            for row in ascii_matrix:
                for char in row:
                    final_string += char
                final_string += "\n"
            if not self.loop:
                try:
                    sys.stdout.write(final_string)
                    sys.stdout.write("\n")
                    time.sleep(duration/1000) # milliseconds
                    sys.stdout.write("\033[H\033[?25l") # move cursor back to home, invisibly
                except KeyboardInterrupt:
                    break
                sys.stdout.write("\033[?25h") # restore/un-hide the cursor
            else:
                # if loop is enabled, we should break only when there's an explicit KeyboardInterrupt for the entire animation
                # this is handled by display()
                sys.stdout.write(final_string)
                sys.stdout.write("\n")
                time.sleep(duration/1000) # milliseconds
                sys.stdout.write("\033[H\033[?25l") # move cursor back to home, invisibly

    def display(self):
        """
        Method for displaying the generated ASCII art to terminal. Internally uses the convert() method.

        Parameters:
            none

        Returns:
            nothing, just displays the generated ASCII art to your terminal screen.
        """
        frame_matrices, frame_durations  = self.convert()
        if self.loop:
            try:
                while True:
                    self._print_to_term(frame_matrices, frame_durations)
            except KeyboardInterrupt:
                sys.stdout.write("\033[?25h")
        else:
            self._print_to_term(frame_matrices, frame_durations)

if __name__ == "__main__":
    converter = ImageToASCII(url="https://upload.wikimedia.org/wikipedia/commons/2/2d/John_Carmack_2025.jpg", true_term=True, brightness_method="luminosity", color=True, sizing="maxres")
    # converter = AnimationToASCII(url="https://www.icegif.com/wp-content/uploads/2023/06/icegif-389.gif", true_term=True, brightness_method="luminosity", color=True, sizing="fit", loop=True)
    converter = AnimationToASCII(url="/home/ishu/Downloads/cat.gif", true_term=True, brightness_method="luminosity", color=True, sizing="fit", loop=True)
    # final_mat = converter.convert()
    converter.display()
