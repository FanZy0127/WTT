import os
import json
import tarfile
import time
import yaml
from tqdm import tqdm

# File paths
DATA_TAR_GZ_PATH = 'data/202212-datalogger.tar.gz'
EXTRACTED_DATA_PATH = 'data/extracted'
FILE_PATHS = [
    'data/extracted/datalogger/db.json',
    'data/202212_api_requirements.json',
    'data/202212_openapi_spec_v1.json'
]

# Function to extract files
def extract_files(tar_gz_path, extract_path):
    if not os.path.exists(extract_path):
        os.makedirs(extract_path)
    with tarfile.open(tar_gz_path, 'r:gz') as tar:
        tar.extractall(path=extract_path)
    print(f"Files extracted to {extract_path}")

# Function to load and validate JSON or YAML data with progress bar and elapsed time
def validate_json_or_yaml(file_paths):
    chunk_size = 8192  # Read the file in chunks of 8 KB
    for file_path in file_paths:
        start_time = time.time()
        try:
            file_size = os.path.getsize(file_path)
            with open(file_path, 'r') as file:
                progress_bar = tqdm(total=file_size, unit='iB', unit_scale=True, desc=os.path.basename(file_path))
                data = ''
                while True:
                    chunk = file.read(chunk_size)
                    if not chunk:
                        break
                    data += chunk
                    progress_bar.update(len(chunk))
                    elapsed_time = time.time() - start_time
                    progress_bar.set_postfix({'Elapsed Time (s)': f'{elapsed_time:.2f}'})
                progress_bar.close()
                # Try loading as JSON
                try:
                    json_data = json.loads(data)
                    elapsed_time = time.time() - start_time
                    print(f"{os.path.basename(file_path)} : Data OK")
                    print(f"Elapsed Time : {elapsed_time:.2f} seconds")
                    continue  # Move to the next file
                except json.JSONDecodeError:
                    # If JSON loading fails, try loading as YAML
                    try:
                        yaml_data = yaml.safe_load(data)
                        elapsed_time = time.time() - start_time
                        print(f"{os.path.basename(file_path)} : Data OK")
                        print(f"Elapsed Time : {elapsed_time:.2f} seconds")
                    except yaml.YAMLError as e:
                        elapsed_time = time.time() - start_time
                        print(f"{os.path.basename(file_path)} : Data Error => {e}")
                        print(f"Elapsed Time : {elapsed_time:.2f} seconds")
                        display_error_context(data, e)
        except FileNotFoundError as e:
            elapsed_time = time.time() - start_time
            print(f"{os.path.basename(file_path)} : Data Error => {e}")
            print(f"Elapsed Time : {elapsed_time:.2f} seconds")

# Function to display the context around the error
def display_error_context(data, error):
    error_pos = error.pos if hasattr(error, 'pos') else None
    if error_pos is not None:
        start = max(0, error_pos - 20)
        end = min(len(data), error_pos + 20)
        context = data[start:end]
        print(f"Context around the error: '{context}'")
    else:
        print("Could not determine the exact position of the error.")

# Main function for standalone execution
def main():
    # Extract files
    extract_files(DATA_TAR_GZ_PATH, EXTRACTED_DATA_PATH)

    # Validate data from all file paths
    validate_json_or_yaml(FILE_PATHS)

if __name__ == "__main__":
    main()
