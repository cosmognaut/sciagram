# Decision Log

## Architecture Decisions

### 1. Library Output Model
- **Decision**: The conversion interface yields/returns string representations of the ASCII art instead of writing side effects directly to `sys.stdout`.
- **User Reasoning**: Allows consumers of the library to capture, store, pipe, or render output flexibly rather than being coupled to interactive terminal stdout.

### 2. Terminal Sizing Fallback
- **Decision**: Use `shutil.get_terminal_size(fallback=(80, 24))` instead of `os.get_terminal_size()`.
- **Reasoning**: Prevents `ENOTTY` (`Inappropriate ioctl for device`) crashes when stdout is redirected to pipes or files.

### 3. Color Encoding Standard
- **Decision**: Use 24-bit TrueColor ANSI escape codes (`\033[38;2;R;G;Bm`) for color rendering.
- **Observed**: Execution of `f"\033[38;2;{red};{green};{blue}m{text}"` verified in terminal.

### 4. Color Configuration Option
- **Decision**: Added `color: bool = False` flag to `ImageToASCII`.
- **Implementation**: When `True`, wraps each character with `\033[38;2;R;G;Bm`.
- **Observed**: Output verified via `uv run python -m src.sciagram.converter`.
