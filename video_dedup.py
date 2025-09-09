#!/usr/bin/env python3
"""
Hash-Based Video Frame Deduplication Tool
Extracts frames from video files and removes duplicates using perceptual hashing.
"""

import argparse
import cv2
import os
import sys
from pathlib import Path
import imagehash
from PIL import Image
import tempfile
import shutil
from typing import List, Tuple, Dict
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class VideoDeduplicator:
    def __init__(self, video_path: str, similarity_threshold: int = 5):
        self.video_path = Path(video_path)
        self.similarity_threshold = similarity_threshold
        self.supported_formats = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v'}
        
        if not self.video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        if self.video_path.suffix.lower() not in self.supported_formats:
            logger.warning(f"Format {self.video_path.suffix} may not be supported")

    def extract_frames(self, interval: int = None) -> List[Tuple[int, str]]:
        """Extract frames from video. If interval is None, extract all frames."""
        cap = cv2.VideoCapture(str(self.video_path))
        
        if not cap.isOpened():
            raise ValueError(f"Cannot open video file: {self.video_path}")
        
        temp_dir = tempfile.mkdtemp()
        frames = []
        frame_count = 0
        extracted_count = 0
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        logger.info(f"Video info: {total_frames} frames, {fps:.2f} FPS")
        
        if interval:
            logger.info(f"Extracting frames at {interval} frame intervals")
        else:
            logger.info("Extracting all frames")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            should_extract = interval is None or frame_count % interval == 0
            
            if should_extract:
                frame_path = os.path.join(temp_dir, f"frame_{frame_count:06d}.jpg")
                cv2.imwrite(frame_path, frame)
                frames.append((frame_count, frame_path))
                extracted_count += 1
                
                if extracted_count % 100 == 0:
                    logger.info(f"Extracted {extracted_count} frames...")
            
            frame_count += 1
        
        cap.release()
        logger.info(f"Extracted {extracted_count} frames total")
        return frames

    def generate_hashes(self, frames: List[Tuple[int, str]]) -> Dict[int, str]:
        """Generate perceptual hashes for frames."""
        hashes = {}
        
        logger.info("Generating perceptual hashes...")
        
        for i, (frame_num, frame_path) in enumerate(frames):
            try:
                with Image.open(frame_path) as img:
                    phash = str(imagehash.phash(img))
                    hashes[frame_num] = phash
                
                if (i + 1) % 100 == 0:
                    logger.info(f"Processed {i + 1}/{len(frames)} frames")
            
            except Exception as e:
                logger.warning(f"Failed to process frame {frame_num}: {e}")
        
        logger.info(f"Generated {len(hashes)} hashes")
        return hashes

    def find_duplicates(self, hashes: Dict[int, str]) -> List[int]:
        """Find duplicate frames based on hash similarity."""
        duplicates = []
        processed_hashes = set()
        hash_to_frame = {}
        
        logger.info(f"Finding duplicates with threshold {self.similarity_threshold}...")
        
        for frame_num, hash_str in hashes.items():
            hash_obj = imagehash.hex_to_hash(hash_str)
            is_duplicate = False
            
            for processed_hash_str in processed_hashes:
                processed_hash_obj = imagehash.hex_to_hash(processed_hash_str)
                difference = hash_obj - processed_hash_obj
                
                if difference <= self.similarity_threshold:
                    duplicates.append(frame_num)
                    is_duplicate = True
                    logger.debug(f"Frame {frame_num} is duplicate of frame {hash_to_frame[processed_hash_str]} (diff: {difference})")
                    break
            
            if not is_duplicate:
                processed_hashes.add(hash_str)
                hash_to_frame[hash_str] = frame_num
        
        logger.info(f"Found {len(duplicates)} duplicate frames")
        return duplicates

    def save_unique_frames(self, frames: List[Tuple[int, str]], duplicates: List[int], output_dir: str):
        """Save unique frames to output directory."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        duplicate_set = set(duplicates)
        saved_count = 0
        
        logger.info(f"Saving unique frames to {output_dir}...")
        
        for frame_num, frame_path in frames:
            if frame_num not in duplicate_set:
                output_file = output_path / f"unique_frame_{frame_num:06d}.jpg"
                shutil.copy2(frame_path, output_file)
                saved_count += 1
        
        logger.info(f"Saved {saved_count} unique frames")
        
        # Cleanup temp files
        temp_dir = Path(frames[0][1]).parent
        shutil.rmtree(temp_dir)

    def deduplicate(self, interval: int = None, output_dir: str = "unique_frames"):
        """Main deduplication process."""
        logger.info(f"Starting deduplication of {self.video_path}")
        
        # Extract frames
        frames = self.extract_frames(interval)
        
        # Generate hashes
        hashes = self.generate_hashes(frames)
        
        # Find duplicates
        duplicates = self.find_duplicates(hashes)
        
        # Save unique frames
        self.save_unique_frames(frames, duplicates, output_dir)
        
        total_frames = len(frames)
        unique_frames = total_frames - len(duplicates)
        reduction_percent = (len(duplicates) / total_frames * 100) if total_frames > 0 else 0
        
        logger.info(f"Deduplication complete!")
        logger.info(f"Original frames: {total_frames}")
        logger.info(f"Duplicate frames: {len(duplicates)}")
        logger.info(f"Unique frames: {unique_frames}")
        logger.info(f"Reduction: {reduction_percent:.1f}%")


def main():
    parser = argparse.ArgumentParser(
        description="Hash-based video frame deduplication tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python video_dedup.py video.mp4
  python video_dedup.py video.mp4 --interval 30 --threshold 3
  python video_dedup.py video.mp4 --output-dir ./frames --threshold 8
        """
    )
    
    parser.add_argument('video_path', help='Path to the video file')
    
    parser.add_argument(
        '--interval', '-i',
        type=int,
        help='Extract frames at intervals (e.g., every 30 frames). If not specified, extracts all frames.'
    )
    
    parser.add_argument(
        '--threshold', '-t',
        type=int,
        default=5,
        help='Similarity threshold for duplicate detection (0-64, lower = more strict). Default: 5'
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        type=str,
        default='unique_frames',
        help='Output directory for unique frames. Default: unique_frames'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if args.threshold < 0 or args.threshold > 64:
        parser.error("Threshold must be between 0 and 64")
    
    try:
        deduplicator = VideoDeduplicator(args.video_path, args.threshold)
        deduplicator.deduplicate(args.interval, args.output_dir)
        
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()