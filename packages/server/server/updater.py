import hashlib
import os

ignored_extensions = [".bin", ".sqlite3"]


def get_files_to_process(folder: str) -> dict:
    files_and_dirs = []
    for root, dirs, files in os.walk(folder):
        for name in files:
            files_and_dirs.append(os.path.join(root, name))

    log = ""
    print("Found", len(files_and_dirs), "folders/files")
    log += f"Found {len(files_and_dirs)} folders/files\n\n"

    files = [
        f for f in files_and_dirs
        if "node_modules" not in f and not f.startswith(".git") and not any(f.endswith(ext) for ext in ignored_extensions)
    ]
    log += f"Found {len(files)} files (excluding ignored folders)\n\n"

    return {"files": files, "log": log}


def handle_file(filepath: str) -> dict:
    """
    Reads the content of a file, if not binary, and returns a dictionary containing the content and its MD5 hash.

    Args:
      filepath (str): The path to the file to be read.

    Returns:
      dict: A dictionary with two keys:
        - 'filepath': The path to the file.
        - 'content': The content of the file as a string.
        - 'id': The MD5 hash of the file content.
    """
    if is_binary_file(filepath):
        return None

    # Read the file in text mode
    with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read()
        return {
            'filepath': filepath,
            'content': content,
            'id': hashlib.md5(content.encode()).hexdigest()
        }


def is_binary_file(filepath: str) -> bool:
    """
    Checks if a file is binary by reading the first 1024 bytes and looking for null bytes.

    Args:
        filepath (str): The path to the file to be checked.

    Returns:
        bool: True if the file is binary, False otherwise.
    """
    with open(filepath, 'rb') as file:
        if b'\0' in file.read(1024):
            return True
    return False


directory_path = './../'
dict = get_files_to_process(directory_path)

for file in dict['files']:
    file_result = handle_file(file)
    if file_result:
        print(file_result['id'], file_result['filepath'])
