"""
Test script to inspect Hugging Face dataset structure before processing.
This helps identify the correct field names for videos and captions.
"""
import argparse
import logging
from datasets import load_dataset
from typing import Dict, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def analyze_dataset_structure(dataset_name: str, split: str = "train", max_samples: int = 3):
    """
    Analyze the structure of a Hugging Face dataset to understand its format.

    Args:
        dataset_name: Name of the Hugging Face dataset
        split: Dataset split to analyze
        max_samples: Number of samples to examine
    """
    print(f"\n{'='*60}")
    print(f"ANALYZING DATASET: {dataset_name}")
    print(f"{'='*60}")

    try:
        # Load dataset
        print(f"Loading dataset split: {split}")
        dataset = load_dataset(dataset_name, split=split)

        print(f"Dataset size: {len(dataset)}")
        print(f"Dataset features: {dataset.features}")

        # Analyze first few samples
        samples_to_check = min(len(dataset), max_samples)
        print(f"\nAnalyzing first {samples_to_check} samples:")

        for i in range(samples_to_check):
            sample = dataset[i]
            print(f"\n--- Sample {i+1} ---")
            print(f"Keys: {list(sample.keys())}")

            # Check each field
            for key, value in sample.items():
                value_type = type(value).__name__

                if isinstance(value, str):
                    preview = value[:100] + "..." if len(value) > 100 else value
                    print(f"  {key}: {value_type} - '{preview}'")
                elif hasattr(value, 'path'):
                    print(f"  {key}: {value_type} - path: {value.path}")
                elif hasattr(value, 'shape'):
                    print(f"  {key}: {value_type} - shape: {value.shape}")
                else:
                    print(f"  {key}: {value_type} - {str(value)[:100]}...")

        # Try to identify potential video and caption fields
        print(f"\n{'='*60}")
        print("FIELD ANALYSIS:")
        print(f"{'='*60}")

        first_sample = dataset[0]

        # Potential video fields
        video_candidates = []
        for key, value in first_sample.items():
            if any(keyword in key.lower() for keyword in ['video', 'mp4', 'movie', 'clip']):
                video_candidates.append(key)
            elif isinstance(value, str) and any(ext in value.lower() for ext in ['.mp4', '.avi', '.mov', '.mkv']):
                video_candidates.append(key)
            elif hasattr(value, 'path') and any(ext in str(value.path).lower() for ext in ['.mp4', '.avi', '.mov', '.mkv']):
                video_candidates.append(key)

        # Potential caption fields
        caption_candidates = []
        for key, value in first_sample.items():
            if any(keyword in key.lower() for keyword in ['caption', 'text', 'description', 'prompt', 'title', 'label']):
                caption_candidates.append(key)

        print(f"Potential video fields: {video_candidates}")
        print(f"Potential caption fields: {caption_candidates}")

        # Recommendations
        print(f"\n{'='*60}")
        print("RECOMMENDATIONS:")
        print(f"{'='*60}")

        if video_candidates:
            print(f"✓ Recommended video field: '{video_candidates[0]}'")
        else:
            print("✗ No obvious video field found. Manual inspection needed.")
            print("  Available fields:", list(first_sample.keys()))

        if caption_candidates:
            print(f"✓ Recommended caption field: '{caption_candidates[0]}'")
        else:
            print("✓ No caption field found - will create empty caption files")

        # Show command to run
        print(f"\n{'='*60}")
        print("SUGGESTED COMMAND:")
        print(f"{'='*60}")
        print(f"./hallo3/scripts/data_preprocess_hf.sh \"{dataset_name}\" 4 0 \"my_dataset\"")

    except Exception as e:
        logging.error(f"Failed to analyze dataset {dataset_name}: {e}")
        print(f"Error details: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description="Analyze Hugging Face dataset structure")
    parser.add_argument("--dataset_name", required=True, help="Name of the Hugging Face dataset")
    parser.add_argument("--split", default="train", help="Dataset split to analyze")
    parser.add_argument("--max_samples", type=int, default=3, help="Number of samples to examine")

    args = parser.parse_args()

    analyze_dataset_structure(args.dataset_name, args.split, args.max_samples)


if __name__ == "__main__":
    main()
