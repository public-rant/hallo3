#!/usr/bin/env python3
"""
Convenience wrapper script for processing Hugging Face datasets with hallo3.
This script provides a simple interface to the entire pipeline.
"""
import argparse
import logging
import os
import subprocess
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def run_command(cmd, cwd=None):
    """Run a shell command and return success status."""
    try:
        logging.info(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed: {' '.join(cmd)}")
        logging.error(f"Error: {e.stderr}")
        return False


def check_dependencies():
    """Check if required dependencies are available."""
    try:
        import datasets
        import torch
        import cv2
        import tqdm
        logging.info("✓ All required dependencies found")
        return True
    except ImportError as e:
        logging.error(f"✗ Missing dependency: {e}")
        logging.error("Please install required packages:")
        logging.error("pip install datasets torch opencv-python tqdm")
        return False


def analyze_dataset(dataset_name, split="train"):
    """Analyze dataset structure before processing."""
    logging.info(f"Analyzing dataset: {dataset_name}")

    script_path = Path(__file__).parent / "test_dataset_structure.py"
    cmd = [sys.executable, str(script_path), "--dataset_name", dataset_name, "--split", split]

    return run_command(cmd)


def process_dataset(dataset_name, parallelism=1, rank=0, output_name=None, temp_dir=None, analyze_first=True):
    """Process a Hugging Face dataset through the entire hallo3 pipeline."""

    # Check dependencies
    if not check_dependencies():
        return False

    # Set default output name
    if output_name is None:
        output_name = dataset_name.replace("/", "_").replace("-", "_")

    # Set default temp directory
    if temp_dir is None:
        temp_dir = f"/tmp/hallo3_processing_{output_name}"

    # Analyze dataset first if requested
    if analyze_first:
        logging.info("Analyzing dataset structure first...")
        if not analyze_dataset(dataset_name):
            logging.warning("Dataset analysis failed, but continuing with processing...")

    # Run the processing pipeline
    logging.info("Starting processing pipeline...")

    script_path = Path(__file__).parent / "scripts" / "data_preprocess_hf.sh"
    cmd = [
        str(script_path),
        dataset_name,
        str(parallelism),
        str(rank),
        output_name,
        temp_dir
    ]

    success = run_command(cmd)

    if success:
        logging.info("Processing completed successfully!")
        logging.info(f"Results saved to: ./data/{output_name}.json")
        logging.info(f"Temporary files in: {temp_dir}")

        # Ask if user wants to keep temp files
        try:
            keep_temp = input("Keep temporary files? (y/N): ").lower().strip()
            if keep_temp != 'y':
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
                logging.info("Temporary files cleaned up")
        except KeyboardInterrupt:
            logging.info("\nTemporary files kept")
    else:
        logging.error("Processing failed!")
        logging.error(f"Check temporary files in: {temp_dir}")

    return success


def main():
    parser = argparse.ArgumentParser(
        description="Process Hugging Face datasets with hallo3 pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze dataset structure only
  python process_hf_dataset.py --analyze-only "username/dataset-name"

  # Process dataset with default settings
  python process_hf_dataset.py "username/dataset-name"

  # Process with custom parallelism and output name
  python process_hf_dataset.py "username/dataset-name" --parallelism 4 --output-name "my_dataset"

  # Process without initial analysis
  python process_hf_dataset.py "username/dataset-name" --no-analyze
        """
    )

    parser.add_argument(
        "dataset_name",
        help="Name of the Hugging Face dataset (e.g., 'username/dataset-name')"
    )

    parser.add_argument(
        "--parallelism", "-p",
        type=int,
        default=1,
        help="Level of parallelism for processing (default: 1)"
    )

    parser.add_argument(
        "--rank", "-r",
        type=int,
        default=0,
        help="Rank for distributed processing (default: 0)"
    )

    parser.add_argument(
        "--output-name", "-o",
        help="Name for output files (default: sanitized dataset name)"
    )

    parser.add_argument(
        "--temp-dir", "-t",
        help="Temporary directory for processing (default: /tmp/hallo3_processing_<name>)"
    )

    parser.add_argument(
        "--analyze-only",
        action="store_true",
        help="Only analyze dataset structure, don't process"
    )

    parser.add_argument(
        "--no-analyze",
        action="store_true",
        help="Skip dataset analysis and go straight to processing"
    )

    args = parser.parse_args()

    # Handle analyze-only mode
    if args.analyze_only:
        analyze_dataset(args.dataset_name)
        return

    # Process the dataset
    success = process_dataset(
        dataset_name=args.dataset_name,
        parallelism=args.parallelism,
        rank=args.rank,
        output_name=args.output_name,
        temp_dir=args.temp_dir,
        analyze_first=not args.no_analyze
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
