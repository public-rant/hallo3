"""
Extract videos and captions from Hugging Face datasets for hallo3 processing.
"""
import argparse
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional

from datasets import load_dataset
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def detect_video_field(sample: Dict[str, Any]) -> Optional[str]:
    """
    Detect which field contains video data in the dataset sample.

    Args:
        sample: A single sample from the dataset

    Returns:
        The field name containing video data, or None if not found
    """
    # Common video field names
    video_fields = ['video', 'video_file', 'video_path', 'mp4', 'movie', 'clip']

    for field in video_fields:
        if field in sample:
            return field

    # Check for fields that might contain video data
    for key, value in sample.items():
        if isinstance(value, str) and any(ext in value.lower() for ext in ['.mp4', '.avi', '.mov', '.mkv']):
            return key
        elif hasattr(value, 'path') and any(ext in str(value.path).lower() for ext in ['.mp4', '.avi', '.mov', '.mkv']):
            return key

    return None


def detect_caption_field(sample: Dict[str, Any]) -> Optional[str]:
    """
    Detect which field contains caption/text data in the dataset sample.

    Args:
        sample: A single sample from the dataset

    Returns:
        The field name containing caption data, or None if not found
    """
    # Common caption field names
    caption_fields = ['caption', 'text', 'description', 'prompt', 'title', 'label']

    for field in caption_fields:
        if field in sample:
            return field

    return None


def extract_video_file(video_data: Any, output_path: Path) -> bool:
    """
    Extract video file from various possible formats.

    Args:
        video_data: Video data from the dataset (could be path, bytes, or file object)
        output_path: Where to save the video file

    Returns:
        True if successful, False otherwise
    """
    try:
        if isinstance(video_data, str):
            # It's a file path
            if os.path.exists(video_data):
                import shutil
                shutil.copy2(video_data, output_path)
                return True
        elif hasattr(video_data, 'path'):
            # It's a file object with path attribute
            import shutil
            shutil.copy2(video_data.path, output_path)
            return True
        elif hasattr(video_data, 'read'):
            # It's a file-like object
            with open(output_path, 'wb') as f:
                f.write(video_data.read())
            return True
        elif isinstance(video_data, bytes):
            # It's raw bytes
            with open(output_path, 'wb') as f:
                f.write(video_data)
            return True
        else:
            logging.warning(f"Unknown video data type: {type(video_data)}")
            return False
    except Exception as e:
        logging.error(f"Failed to extract video: {e}")
        return False


def extract_from_hf_dataset(
    dataset_name: str,
    output_videos: Path,
    output_captions: Path,
    split: str = "train",
    max_samples: Optional[int] = None
) -> None:
    """
    Extract videos and captions from a Hugging Face dataset.

    Args:
        dataset_name: Name of the Hugging Face dataset
        output_videos: Directory to save extracted videos
        output_captions: Directory to save caption files
        split: Dataset split to use
        max_samples: Maximum number of samples to process
    """
    logging.info(f"Loading dataset: {dataset_name}")

    try:
        dataset = load_dataset(dataset_name, split=split)
    except Exception as e:
        logging.error(f"Failed to load dataset {dataset_name}: {e}")
        return

    # Detect field names from first sample
    if len(dataset) == 0:
        logging.error("Dataset is empty!")
        return

    first_sample = dataset[0]
    video_field = detect_video_field(first_sample)
    caption_field = detect_caption_field(first_sample)

    if video_field is None:
        logging.error(f"Could not detect video field in dataset. Available fields: {list(first_sample.keys())}")
        return

    logging.info(f"Detected video field: {video_field}")
    if caption_field:
        logging.info(f"Detected caption field: {caption_field}")
    else:
        logging.warning("No caption field detected - will create empty caption files")

    # Process samples
    samples_to_process = min(len(dataset), max_samples) if max_samples else len(dataset)
    successful_extractions = 0

    for idx in tqdm(range(samples_to_process), desc="Extracting videos"):
        sample = dataset[idx]

        # Generate output filename
        video_filename = f"video_{idx:06d}.mp4"
        video_output_path = output_videos / video_filename
        caption_output_path = output_captions / f"video_{idx:06d}.txt"

        # Extract video
        if extract_video_file(sample[video_field], video_output_path):
            successful_extractions += 1

            # Extract caption
            if caption_field and caption_field in sample:
                caption_text = str(sample[caption_field])
                with open(caption_output_path, 'w', encoding='utf-8') as f:
                    f.write(caption_text)
            else:
                # Create empty caption file
                with open(caption_output_path, 'w', encoding='utf-8') as f:
                    f.write("")
        else:
            logging.warning(f"Failed to extract video for sample {idx}")

    logging.info(f"Successfully extracted {successful_extractions} videos out of {samples_to_process} samples")


def main():
    parser = argparse.ArgumentParser(description="Extract videos and captions from Hugging Face datasets")
    parser.add_argument("--dataset_name", required=True, help="Name of the Hugging Face dataset")
    parser.add_argument("--output_videos", type=Path, required=True, help="Directory to save extracted videos")
    parser.add_argument("--output_captions", type=Path, required=True, help="Directory to save caption files")
    parser.add_argument("--split", default="train", help="Dataset split to use")
    parser.add_argument("--max_samples", type=int, help="Maximum number of samples to process")

    args = parser.parse_args()

    # Create output directories
    args.output_videos.mkdir(parents=True, exist_ok=True)
    args.output_captions.mkdir(parents=True, exist_ok=True)

    extract_from_hf_dataset(
        args.dataset_name,
        args.output_videos,
        args.output_captions,
        args.split,
        args.max_samples
    )


if __name__ == "__main__":
    main()
