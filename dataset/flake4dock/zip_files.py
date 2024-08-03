import os
import zipfile
import argparse
from tqdm import tqdm

def zip_folders(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    # List all folders in the input directory
    all_folders = [f for f in os.listdir(input_dir) if os.path.isdir(os.path.join(input_dir, f))]

    # Iterate over the folders in chunks of 50
    for i in tqdm(range(0, len(all_folders), 50)):
        chunk = all_folders[i:i + 50]
        zip_filename = os.path.join(output_dir, f'folders_{i // 50 + 1}.zip')

        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for folder in chunk:
                folder_path = os.path.join(input_dir, folder)
                for root, dirs, files in os.walk(folder_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        zipf.write(file_path, os.path.relpath(file_path, input_dir))

    print("Zipping complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Zip folders in chunks of 50")
    parser.add_argument("-i", "--input", required=True, help="Input directory containing folders to zip")
    parser.add_argument("-o", "--output", required=True, help="Output directory to save zip files")

    args = parser.parse_args()
    zip_folders(args.input, args.output)
