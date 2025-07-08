#!/bin/bash

# Enhanced script to process Hugging Face datasets
dataset_name="$1"
p="$2"
r="$3"
name="$4"
temp_root="${5:-/tmp/hallo3_processing}"

echo "Processing Hugging Face dataset: $dataset_name"
echo "Parallelism: $p, Rank: $r, Dataset name: $name"

# Create temporary directory structure
mkdir -p "$temp_root/videos"
mkdir -p "$temp_root/caption"

# Extract videos and captions from Hugging Face dataset
echo "Extracting videos from Hugging Face dataset..."
python hallo3/extract_from_hf_dataset.py \
    --dataset_name "$dataset_name" \
    --output_videos "$temp_root/videos" \
    --output_captions "$temp_root/caption"

# Run the existing preprocessing pipeline
echo "Running video preprocessing..."
python hallo3/data_preprocess.py -i "$temp_root/videos" -o "$temp_root" -p "$p" -r "$r"

# Extract meta information
echo "Extracting meta information..."
python hallo3/extract_meta_info.py -r "$temp_root" -n "$name"

echo "Processing complete! Results saved to ./data/$name.json"
echo "Temporary files in: $temp_root"
