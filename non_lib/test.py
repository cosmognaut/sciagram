from sciagram.converter import ImageToASCII

magic = ImageToASCII(image_url="/home/ishu/Projects/sciagram/assets/samples/sample.jpg", brightness_method="luminosity", color=True, sizing="maxres")
magic.print_to_term()
