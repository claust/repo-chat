import hashlib
import os

ignored_extensions = [".bin", ".sqlite3"]


def get_files_to_process(base_folder: str) -> dict:
    """
    Recursively scans the given folder and returns a dictionary containing a list of files to process and a log.

    Args:
        base_folder (str): The path to the folder to scan.

    Returns:
        dict: A dictionary with two keys:
            - "files": A list of text file paths that do not include "node_modules" and do not start with ".git" or end with any of the ignored extensions.
            - "log": A string log of the scanning process, including the number of files found and the number of files after excluding ignored folders.
    """
    files_and_dirs = []
    for root, dirs, files in os.walk(base_folder):
        for name in files:
            file_path = os.path.join(root, name)
            if not is_binary_file(file_path):
                files_and_dirs.append(file_path)

    log = ""
    print("Found", len(files_and_dirs), "files")
    log += f"Found {len(files_and_dirs)} files\n\n"

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

    with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read()
        return {
            'filepath': filepath,
            'content': content,
            'id': hashlib.md5((filepath + content).encode()).hexdigest()
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
