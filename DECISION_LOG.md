# Decision Log

## Architecture Decisions

### 1. Library Output Model
- **Decision**: The conversion interface yields/returns string representations of the ASCII art instead of writing side effects directly to `sys.stdout`.
- **User Reasoning**: Allows consumers of the library to capture, store, pipe, or render output flexibly rather than being coupled to interactive terminal stdout.

### 2. Terminal Sizing Fallback
- **Decision**: Use `shutil.get_terminal_size(fallback=(80, 24))` instead of `os.get_terminal_size()`.
- **Reasoning**: Prevents `ENOTTY` (`Inappropriate ioctl for device`) crashes when stdout is redirected to pipes or files.
