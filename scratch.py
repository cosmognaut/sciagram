# import os
#
# size = os.get_terminal_size()
# print(size)
# print(size.columns, size.lines)
#
#
# for _ in range(10):
#     print('#' * 10)

# you don't even need mappings for this
red = 255
green = 165
blue = 0
text = "demo text"
print(f"\033[38;2;{red};{green};{blue}m{text}")
