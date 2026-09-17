import os
from PIL import Image
from typing import Literal

type PixelMatrix = list[list[tuple[int, int, int]]]
type GenericMatrix = list[list[float]]

def _calculate_brightness(red: int, green: int, blue: int, method: Literal["average", "min_max", "luminosity"] = "average") -> float:
    """Calculate the brightness for given RGB values"""
    if method == "average":
        return (red + green + blue) / 3
    elif method == "min_max":
        return ((max(red, green, blue) + min(red, green, blue)) / 2)
    elif method == "luminosity":
        return (0.21 * red + 0.72 * green + 0.07 * blue)

def _brightness_to_ascii(brightness: float, sequence: str = "`^\",:;Il!i~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$") -> str:
    """Returns an ASCII character for any brightness value"""
    # ASCII_CHARS = "`^\",:;Il!i~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
    # think: 0 brightness gets index 0, max brightness gets index 64.
    # which means 0 maps to 0, 255 maps to 64.
    # for max 100 brightness and 20 chars, I can do 50 / 100 * 20
    # following the above logic, 49 should map to 10 again. It gets 9.8. And 10.4 which
    # is 52 should also get the same thing? The range here is 9 = x . 0.2 and 11 = y . 0.2 viz 45 - 55. (0.2 is just 20/100)
    # for max 255 brightness and 64 chars can I do x / 255 * 64?
    # and for this case, what's the range here, i.e. in what range do you get the same brightness? In the above example it was 10, for ex. in strip 45-55 you would find the same brightness. 
    # lower = x . 1/255*64 and higher = y . 1/255*64. So it's 0.25098039215686274 times whatever. Here the midpoint would be 64/2 = 32.
    # But wait - I will never see the $ sign this way? As let's say the brightness for a pixel here would be 252 and I get 63.2 which I can round to 63 to get @ sign.
    # What if I take brightness of a pixel to be 254? I get 63.7 then which I can round to 64. So this does seem to work?
    # Let me try to apply this.
    brightness_number = round((brightness/255) * (len(sequence) - 1))
    return sequence[brightness_number]

def load_image(image_path: str, true_term: bool = True) -> Image.Image:
    """Load an image and optionally resize it to then default terminal cell dimensions (1 char per cell corresponding to 1px)"""
    image = Image.open(image_path)
    size = os.get_terminal_size()
    if true_term:
        term_cols, term_rows = size.columns, size.lines
        # effective_height = round(term_rows * 0.5) # aspect ratio correction is taken to be 0.5
        image = image.resize((term_cols, term_rows))
    print("Successfully loaded image!")
    print(f"Image size: {image.size}")
    return image

def generate_pixel_matrix(image: Image.Image) -> PixelMatrix:
    """Generate a pixel matrix for a given image, with a given width and height"""
    # pixel_matrix = [pixel for pixel in sample.get_flattened_data()]
    # get_flattened_data gives, well, flattened data, which I don't want for my 2D array.

    # coordinates are represented as 0,0 on the upper left
    # width is 700, height is 486 or whatever.
    # so this matrix should be of size 467, each array containing 700 pixel values.
    flat_data = image.get_flattened_data()
    pixel_matrix = []
    image_height = image.height
    image_width = image.width
    # I spent like 30 mins discovering this formula
    # but I had also discovered that flat_data was managing tuples in terms of y times width
    # it genuinely didn't cross my mind to just append that instead of going for the pixel-perfect tuple (literally)
    # for y in range(image_height):
    #     pixel_row = []
    #     for x in range(image_width):
    #         pixel_at_coordinate = flat_data[(y * image_width) + x]
    #         pixel_row.append(pixel_at_coordinate)
    #     pixel_matrix.append(pixel_row)
    for y in range(image_height):
        pixel_matrix.append(flat_data[(y * image_width) : ((y+1) * image_width)])
    return pixel_matrix

def generate_brightness_matrix(pixel_matrix: PixelMatrix, method: Literal["average", "min_max", "luminosity"] = "average") -> GenericMatrix:
    """Give each pixel a brightness value and generate a new matrix based on that"""
    brightness_matrix = []
    for pixel_row in pixel_matrix:
        brightness_row = []
        for pixel in pixel_row:
            red = pixel[0]
            green = pixel[1]
            blue = pixel[2]
            pixel_brightness = _calculate_brightness(red, green, blue, method=method)
            brightness_row.append(pixel_brightness)
        brightness_matrix.append(brightness_row)
    return brightness_matrix

# now I need to scale each brightness to an ASCII character.
# len(ASCII_CHARS) is 65. A brightness of 0 should pick the first character, that is the backtick ` at 0 and a brightness of 255 should pick the last character, i.e. the 64th and final character $.

def generate_ascii_matrix(brightness_matrix: GenericMatrix) -> GenericMatrix:
    """Generate the final ASCII matrix containing an ASCII character for each pixel/brightness value"""
    ascii_matrix = []
    for row in brightness_matrix:
        ascii_row = []
        for brightness_pixel in row:
            ascii_row.append(_brightness_to_ascii(brightness_pixel))
        ascii_matrix.append(ascii_row)
    return ascii_matrix

# 700 width 467 height or 700 height 467 width?

# four_six_seven_chars = []
# for _ in range(467):
#     four_six_seven_chars.append("a")
#
# for char in four_six_seven_chars:
#     print(char, end="")

# for my terminal stty size gives 35 173 at default settings. Which means 35 cells of height and 173 cells of width. One cell is configured to be 14pt in ghostty's font settings. 14pt is around 18.66 pixels.
# Fuck, let me do some trial and error and see on which dimensions my image is rendering perfectly on my screen. Let me look up resizing on pillow.
# on stty size 1036 948 the image renders perfectly.
# this is tough - if I resize an image before converting it to raw pixel data I would lose quality, by a lot.

# 0,1 is on 40, (0, 2) is on 80 and so on. 40 is the image width.
# (1,0) is on 1, (2, 0) is on 2. (2, 1) is on 42. (4,1) is on 44. (4,3) is on 124. (5,3) is on 125.
# (11, 3) is on 131. So again, 3 * 40 + 11 = 131.
# the formula seems to be flat_data[(width * y coordinate) + x coordinate]

def optimised_generation(image: Image.Image, method: Literal["average", "min_max", "luminosity"] = "average") -> GenericMatrix:
    """
    Optimised generation of the final ASCII characters' matrix.
    Uses a single iteration to accomplish everything.
    """
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
            pixel_brightness = _calculate_brightness(red, green, blue, method=method)
            character_row.append(_brightness_to_ascii(pixel_brightness))
        final_matrix.append(character_row)
    return final_matrix

if __name__ == "__main__":
    image = load_image("cosmog.jpg", true_term=True)
    final_mat = optimised_generation(image, method="luminosity")
    # pixel_mat = generate_pixel_matrix(image)
    # brightness_mat = generate_brightness_matrix(pixel_mat)
    # final_mat = generate_ascii_matrix(brightness_mat)
    for row in final_mat:
        for char in row:
            print(char, end="")
        print()
