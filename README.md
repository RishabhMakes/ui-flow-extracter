# Video Frame Deduplication Tool

A Python CLI tool for hash-based video frame deduplication that extracts frames from video files and removes duplicates using perceptual hashing.

## Features

- **Hash-Based Deduplication**: Uses perceptual hashing to identify and remove duplicate or nearly identical frames
- **Flexible Frame Extraction**: Extract all frames or frames at specified intervals
- **Configurable Similarity Threshold**: Adjust how strict the duplicate detection should be
- **Multiple Video Formats**: Supports common video formats (MP4, AVI, MOV, MKV, WMV, FLV, WebM, M4V)
- **Progress Tracking**: Real-time progress updates during processing
- **Detailed Statistics**: Shows reduction percentages and frame counts

## Installation

1. Clone or download this repository
2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

Extract all frames and deduplicate:
```bash
python video_dedup.py video.mp4
```

### Advanced Usage

Extract frames at intervals (faster processing):
```bash
python video_dedup.py video.mp4 --interval 30
```

Custom similarity threshold and output directory:
```bash
python video_dedup.py video.mp4 --threshold 3 --output-dir ./my_frames
```

Enable verbose logging:
```bash
python video_dedup.py video.mp4 --verbose
```

### Command Line Options

- `video_path`: Path to the input video file (required)
- `--interval`, `-i`: Extract frames at intervals (e.g., every 30 frames). If not specified, extracts all frames
- `--threshold`, `-t`: Similarity threshold for duplicate detection (0-64, lower = more strict). Default: 5
- `--output-dir`, `-o`: Output directory for unique frames. Default: unique_frames
- `--verbose`, `-v`: Enable verbose logging

### Examples

```bash
# Basic deduplication
python video_dedup.py presentation.mp4

# Extract every 24th frame (roughly 1 frame per second for 24fps video)
python video_dedup.py presentation.mp4 --interval 24 --output-dir frames

# Strict duplicate detection
python video_dedup.py video.mp4 --threshold 2

# Lenient duplicate detection
python video_dedup.py video.mp4 --threshold 10
```

## How It Works

1. **Frame Extraction**: Extracts frames from the video using OpenCV
2. **Perceptual Hashing**: Generates perceptual hashes for each frame using the `imagehash` library
3. **Duplicate Detection**: Compares hashes using Hamming distance to find similar frames
4. **Deduplication**: Removes duplicate frames based on the similarity threshold
5. **Output**: Saves unique frames to the specified output directory

## Similarity Threshold Guide

The similarity threshold determines how strict the duplicate detection is:

- **0-2**: Very strict - only removes nearly identical frames
- **3-5**: Moderate (default) - good balance for most use cases
- **6-10**: Lenient - removes more variations but may remove legitimate differences
- **11+**: Very lenient - may remove frames that are noticeably different

## Performance Tips

- Use `--interval` for faster processing on long videos
- For screen recordings or presentations, intervals of 24-30 work well
- Higher thresholds process faster but may be less accurate
- Use `--verbose` to monitor progress on large files

## Output

The tool creates a directory containing:
- Unique frames saved as JPG files
- Frames are named with their original frame numbers
- Console output shows statistics including reduction percentage

## Dependencies

- `opencv-python`: Video processing and frame extraction
- `Pillow`: Image processing
- `imagehash`: Perceptual hashing for duplicate detection

## Supported Video Formats

- MP4 (.mp4)
- AVI (.avi)
- MOV (.mov)
- MKV (.mkv)
- WMV (.wmv)
- FLV (.flv)
- WebM (.webm)
- M4V (.m4v)

## License

This project is open source and available under the MIT License.