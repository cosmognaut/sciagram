import os
import sys
# works for standard non piped case.
# file = sys.stdout.fileno()
# print(f"File: {file}")
# print(os.isatty(file))
# size = os.get_terminal_size(file)
# print(size)
# print(size.columns, size.lines)
# observation - when I pipe into less, file equals 1.
# thus file 0 must mean that we're in non-piped case where the pipe was triggered from
# works for all cases?
print(os.isatty(0))
size = os.get_terminal_size(0)
print(size)
print(size.columns, size.lines)
#
#
# for _ in range(10):
#     print('#' * 10)

# you don't even need mappings for this
# red = 255
# green = 165
# blue = 0
# text = "demo text"
# print(f"\033[38;2;{red};{green};{blue}m{text}")
