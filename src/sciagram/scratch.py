import os

size = os.get_terminal_size()
print(size)
print(size.columns, size.lines)


for _ in range(10):
    print('#' * 10)
