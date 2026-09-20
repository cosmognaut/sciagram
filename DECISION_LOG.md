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

### 5. Image Sizing Strategy
- **Decision**: Implement `fit` (contain) mode as default sizing behavior.
- **Reasoning**: Ensures the rendered ASCII art fits completely within `(term_cols, term_rows)` without terminal scrollback distortion, accounting for monospace character cell aspect ratio (~0.5).

### 6. Aspect Ratio Preserving Fit
- **Decision**: Implemented `_fit_image` using uniform scaling factor `min(H_term / (H_img * cell_ratio), W_term / W_img)`.
- **Observed**: Tested in `converter.py`. Output constrained within terminal bounds without distortion.

### 7. Maxres Sizing Strategy
- **Decision**: Added `sizing="maxres"` mode to maximize character resolution.
- **Implementation**: Stretches across the major terminal dimension and scales the other via aspect and cell ratio.
- **Observed**: Tested in `converter.py`.

### 8. Piped Terminal Size Detection
- **Decision**: Query fd 0 (`os.get_terminal_size(0)`) to determine terminal dimensions.
- **Reasoning**: Allows piping stdout to pagers like `less -r` while still preserving the actual terminal window width from stdin.
- **Observed**: Tested via `uv run -m src.sciagram.converter | less -r`. Output rendered at full terminal width.

### 9. Package Release 0.0.2
- **Decision**: Bump version to 0.0.2, export `ImageToASCII` from root package.
- **Observed**: Wheel verified with `zipfile -l`. Contains `converter.py` and `__init__.py`.

### 10. PyPI Deployment
- **Decision**: Published release 0.0.2 to PyPI.
- **Observed**: PyPI metadata API confirms version `0.0.2` active and downloadable.

### 11. Font Cell Ratio Configuration
- **Decision**: Expose `cell_ratio: float` directly as an explicit configuration parameter rather than implementing an automated TTF binary parser.
- **Reasoning**: Keeps the codebase minimal, maintains Pillow as the sole dependency, and avoids the failure modes of parsing diverse OpenType/TrueType binary table variants.

### 12. CLI Entry-Point
- **Decision**: Added `cli.py` with `argparse` and registered `[project.scripts] sciagram = "sciagram.cli:main"`.
- **Observed**: Executable via `uv run sciagram`.

### 13. Global CLI Tool Installation
- **Decision**: Install via `uv tool install . --reinstall` into `~/.local/bin`.
- **Observed**: Binary resolved in `$PATH` at `~/.local/bin/sciagram`.

### 14. In-Memory Remote URL Fetching
- **Decision**: Added `_load_url` using `urllib.request` with custom `User-Agent` and wrapped response in `io.BytesIO`.
- **Reasoning**: Avoids filesystem disk writes/cleanup overhead.
- **Observed**: Tested via `sciagram $TEST_URL --color --method=luminosity`. Output rendered directly to stdout.
