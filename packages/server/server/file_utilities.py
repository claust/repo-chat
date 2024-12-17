import hashlib
import os
import pathspec
from typing import List
from typing import TypedDict

ignored_extensions = [".bin", ".sqlite3"]


class FileProcessResult(TypedDict):
    files: List[str]


class FileResult(TypedDict):
    file_path: str
    relative_file_path: str
    content: str
    id: str


def get_files_to_process(base_folder: str) -> FileProcessResult:
    """
    Recursively scans the given folder and returns a dictionary containing a list of files to process and a log.

    Args:
        base_folder (str): The path to the folder to scan.

    Returns:
        FileProcessResult: A dataclass with two attributes:
            - files: A list of text file paths that do not include "node_modules" and do not start with ".git" or end with any of the ignored extensions.
            - log: A string log of the scanning process, including the number of files found and the number of files after excluding ignored folders.
    """
    spec = generate_gitignore_spec(base_folder)
    files_and_dirs = []
    print(f"Scanning files and directories in {base_folder} ({
          os.path.abspath(base_folder)})")
    for root, dirs, files in os.walk(base_folder):
        for name in files:
            file_path = os.path.join(root, name)
            relative_path = os.path.relpath(file_path, base_folder)
            if not spec.match_file(relative_path) and not is_binary_file(file_path):
                files_and_dirs.append(file_path)

    all_files = len(files_and_dirs)
    print("Found", all_files, "files and dirs")

    def is_ignored(path) -> bool:
        relative_path = os.path.relpath(path, base_folder)
        if spec.match_file(relative_path):
            return True
        if ".git" in path.split(os.sep):
            return True
        if any(path.endswith(ext) for ext in ignored_extensions):
            return True
        return False

    files = [f for f in files_and_dirs if not is_ignored(f)]
    files_to_index = len(files)
    print(f"Found {files_to_index} files to index (ignoring {
          all_files - files_to_index})\n\n")

    return FileProcessResult(files=files)


def generate_gitignore_spec(base_folder) -> pathspec.PathSpec:
    gitignore_path = os.path.join(base_folder, '.gitignore')
    ignored_patterns = []
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r') as gitignore_file:
            ignored_patterns = gitignore_file.read().splitlines()

    spec = pathspec.PathSpec.from_lines('gitwildmatch', ignored_patterns)
    return spec


max_file_size = 20000


def read_file_content(base_folder: str, filepath: str, skip_content: bool = False) -> FileResult:
    """
    Reads the content of a file, if not binary, and returns a FileResult containing the content and its MD5 hash.

    Args:
        base_folder (str): The path to the base folder.
        filepath (str): The path to the file to be read.

    Returns:
      FileHandleResult: A dataclass with three attributes:
        - filepath: The path to the file.
        - content: The content of the file as a string.
        - id: The MD5 hash of the file content.
    """
    with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read()
        # Only take the first max_file_size characters, but log the full length if truncated
        if len(content) > max_file_size:
            print(
                f"File {filepath} has {len(content)} characters, truncating to {max_file_size}")
            content = content[:max_file_size]
        relative_filepath = os.path.relpath(
            filepath, os.path.dirname(base_folder))

        return FileResult(
            file_path=filepath,
            relative_file_path=relative_filepath,
            content="" if skip_content else content,
            id=hashlib.md5((relative_filepath + content).encode()).hexdigest()
        )


def is_binary_file(filepath: str) -> bool:
    """
    Check if a file is binary by attempting to read and decode a portion of the file using UTF-8 encoding.

    Args:
        filepath (str): The path to the file to be checked.

    Returns:
        bool: True if the file is binary, False if it is a text file.
    """
    try:
        with open(filepath, 'rb') as file:
            # Read a portion of the file
            chunk = file.read(1024)
            # Try to decode the chunk using UTF-8
            chunk.decode('utf-8')
    except UnicodeDecodeError:
        # If a UnicodeDecodeError is raised, the file is binary
        return True
    return False
