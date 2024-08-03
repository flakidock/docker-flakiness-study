import os
import json
import shutil
import fnmatch

def list_subfolders(folder_path):
    subfolders = []
    for root, dirs, files in os.walk(folder_path):
        for directory in dirs:
            subfolder_path = os.path.join(root, directory)
            subfolders.append(subfolder_path)
        break # only get top level subfolders
    subfolders = sorted(subfolders)
    return subfolders


def read_file(filename, encoding='utf8'):
    try:
        with open(filename, 'r', encoding=encoding, errors='ignore') as file:
            contents = file.read()
        return contents
    except FileNotFoundError:
        print(f"File not found: {filename}")
        return None


def list_files(folder_path):
    files = []
    for root, dirs, filenames in os.walk(folder_path):
        for filename in filenames:
            if not filename.endswith('.DS_Store'):
                file_path = os.path.join(root, filename)
                files.append(file_path)
    files = sorted(files)
    return files


def list_files_with_extension(folder_path, extension, not_extension=None, check_depth=True):
    files = []
    for root, dirs, filenames in os.walk(folder_path):
        for filename in filenames:
            if filename.endswith(extension) or (extension in filename):
                if (not_extension is None) or (not_extension not in filename):
                    file_path = os.path.join(root, filename)
                    files.append(file_path)
        if not check_depth:
            break
    files = sorted(files)
    return files


def list_folder(folder_path, check_depth=True):
    folders = []
    for root, dirs, filenames in os.walk(folder_path):
        for dir in dirs:
            if not dir.endswith('.DS_Store'):
                dir_path = os.path.join(root, dir)
                folders.append(dir_path)
        if not check_depth:
            break
            

    folders = sorted(folders)
    return folders

def list_log_files(directory):
    log_files = [file for file in os.listdir(directory) if fnmatch.fnmatch(file, '*.log')]
    return log_files

def create_json(dict_object: dict):
    json_data = []
    keys = list(dict_object.keys())
    values = list(zip(*dict_object.values()))

    for entry in values:
        json_entry = {}
        for key, value in zip(keys, entry):
            json_entry[key] = value
        json_data.append(json_entry)

    return json.dumps(json_data, indent=4)


def serialize_json(error_json: dict):
    json_str = json.dumps(error_json, indent=2)
    return json_str


def create_json_file(output_file_name, dictionary):
    json_data = []
    keys = list(dictionary.keys())
    values = list(zip(*dictionary.values()))

    for entry in values:
        json_entry = {}
        for key, value in zip(keys, entry):
            json_entry[key] = value
        json_data.append(json_entry)

    with open(output_file_name, 'w') as file:
        json.dump(json_data, file, indent=4)

def remove_and_generate_new_dir(folder_path: str):
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)

    shutil.os.mkdir(folder_path)

def create_or_empty_folder(folder_path):
    # Check if the folder exists
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        # Get a list of items (files and directories) in the folder
        items = os.listdir(folder_path)

        # Check if there are any items in the folder
        if items:
            # Remove all items in the folder
            for item in items:
                item_path = os.path.join(folder_path, item)
                
                if os.path.isfile(item_path):
                    os.remove(item_path)
                    
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                    
    else:
        os.makedirs(folder_path)
        
def save_list_to_file(data, filename):
    with open (filename, 'w') as f:
        for item in data:
            f.write("%s\n" % item)
            
def read_list_from_file(filename):
    # each line in the file is an item in the list
    with open(filename, 'r') as f:
        data = f.readlines()
    
    return [item.strip() for item in data]
     