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

### 15. Animation Frame Timing Mechanism
- **Decision**: Standardize on `time.sleep(frame_duration / 1000)` for GIF/animation frame pacing.
- **Reasoning**: Yields CPU time slice to the operating system scheduler and avoids pegging a core at 100% utilization, accepting OS wake latency variance over a spinlock.

### 15. Animation Frame Timing Mechanism (Updated)
- **Decision**: `time.sleep(frame_duration / 1000)`. Hybrid approach ruled out.
- **Evidence**: 30 consecutive `time.sleep(0.030)` samples showed max overshoot of 0.50ms (1.6% of frame budget). Scheduler precision is sufficient. Perceived jitter is likely variable per-frame render time, not scheduler wake latency.

### 16. NumPy Vectorization (Deferred)
- **Decision**: Deferred NumPy vectorization of pixel conversion loop.
- **Evidence**: Profiled per-frame: conversion=3.67s, stdout write=0.197s. Conversion is 18.6x the bottleneck.
- **Reasoning**: Other architectural work (base class, video support) takes priority. NumPy rewrite is a confirmed future milestone.

### 17. Class Hierarchy
- **Decision**: Introduced a base class with shared `__init__` and common methods (`_calculate_brightness`, `_brightness_to_ascii`, `_fit_image`, `_maxres_image`). `ImageToASCII` and `AnimationToASCII` inherit from it, each with genuinely distinct behavior. `AnimationToASCII` will gain animation-specific params (e.g. `loop`) in a future step.

### 18. CLI Zero-Argument Handling
- **Decision**: Check `len(sys.argv) == 1` in `main()` and print a descriptive usage hint instead of argparse's default error message.
- **Observed**: `sciagram` with no arguments prints guidance message and exits cleanly.

### 19. Animation Looping Support
- **Decision**: Added `loop: bool = True` to `AnimationToASCII`, caught `KeyboardInterrupt` in `display()`, and restored cursor with `\033[?25h`.
- **Implementation**: Added `--loop` flag to `cli.py` and auto-routed via `_is_animated()`.
- **Observed**: Looping verified; clean exit on `SIGINT` with restored cursor.

### 20. Video Frame Extraction via FFmpeg
- **Decision**: Stream raw video bytes via `ffmpeg -i <file> -f rawvideo -pix_fmt rgb24 -` directly into `subprocess.Popen(stdout=subprocess.PIPE)`.
- **Implementation**: Read chunks of `W * H * 3` bytes and reconstruct using `Image.frombytes("RGB", (W, H), raw_bytes)`.
- **Observed**: First frame extracted and rendered as ASCII in `non_lib/ffmpeg_test.py`.

### 21. Multi-Frame Video Stream Decoding
- **Decision**: Loop `process.stdout.read(frame_bytes)` until EOF to extract all video frames. Downscaling delegated to ffmpeg (`-s`).
- **Observed**: Tested in `non_lib/ffmpeg_test.py`. Continuous sequence of frames decoded and rendered without pipe hangs.

### 22. Video Metadata Extraction via FFprobe
- **Decision**: Query `ffprobe` with JSON output format (`-select_streams v:0 -show_entries stream=width,height,r_frame_rate`).
- **Observed**: Extracted `(width, height, frame_rate)` cleanly from video file without decoding frames.

### 23. VideoToASCII Stream Implementation
- **Decision**: Implemented `VideoToASCII(GenericConverter)` streaming raw RGB frames directly from `ffmpeg` downscaled via `-s`.
- **Flicker Fix**: Eliminated trailing `\n` on the final row (`"\n".join(lines)`), preventing 1-line viewport scroll stutter on bottom margin.
- **Observed**: Video plays in terminal without scrolling or frame tearing.
