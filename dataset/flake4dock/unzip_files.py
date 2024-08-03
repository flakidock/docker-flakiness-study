import os
import zipfile
import argparse
import shutil
from tqdm import tqdm

def extract_folders(zip_dir, output_dirs):
    # List all zip files in the zip directory
    zip_files = [f for f in os.listdir(zip_dir) if f.endswith('.zip')]

    for zip_file in tqdm(zip_files):
        zip_path = os.path.join(zip_dir, zip_file)
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            for output_dir in output_dirs:
                # Create the output directory if it doesn't exist
                os.makedirs(output_dir, exist_ok=True)
                # Extract the zip file to the output directory
                zipf.extractall(output_dir)
                
                print(f"Extracted {zip_file} to {output_dir}")

    print("Extraction complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract zip files to multiple directories")
    parser.add_argument("-i", "--input", required=True, help="Directory containing zip files")
    parser.add_argument("-o", "--output", required=True, nargs='+', help="List of output directories for extraction")

    args = parser.parse_args()
    extract_folders(args.input, args.output)
