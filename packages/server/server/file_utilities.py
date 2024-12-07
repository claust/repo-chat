import hashlib
import os
import pathspec
from typing import List
from dataclasses import dataclass

ignored_extensions = [".bin", ".sqlite3"]


@dataclass
class FileProcessResult:
    files: List[str]
    log: str


@dataclass
class FileResult:
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

    for root, dirs, files in os.walk(base_folder):
        for name in files:
            file_path = os.path.join(root, name)
            relative_path = os.path.relpath(file_path, base_folder)
            if not spec.match_file(relative_path) and not is_binary_file(file_path):
                files_and_dirs.append(file_path)

    log = ""
    print("Found", len(files_and_dirs), "files")
    log += f"Found {len(files_and_dirs)} files\n\n"

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
    log += f"Found {len(files)} files (excluding ignored folders)\n\n"

    return FileProcessResult(files=files, log=log)


def generate_gitignore_spec(base_folder) -> pathspec.PathSpec:
    gitignore_path = os.path.join(base_folder, '.gitignore')
    ignored_patterns = []
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r') as gitignore_file:
            ignored_patterns = gitignore_file.read().splitlines()

    spec = pathspec.PathSpec.from_lines('gitwildmatch', ignored_patterns)
    return spec


def handle_file(base_folder: str, filepath: str) -> FileResult:
    """
    Reads the content of a file, if not binary, and returns a FileHandleResult containing the content and its MD5 hash.

    Args:
      filepath (str): The path to the file to be read.

    Returns:
      FileHandleResult: A dataclass with three attributes:
        - filepath: The path to the file.
        - content: The content of the file as a string.
        - id: The MD5 hash of the file content.
    """
    with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read()
        relative_filepath = os.path.relpath(
            filepath, os.path.dirname(base_folder))

        return FileResult(
            file_path=filepath,
            relative_file_path=relative_filepath,
            content=content,
            id=hashlib.md5((relative_filepath + content).encode()).hexdigest()
        )


def is_binary_file(filepath: str) -> bool:
    """
    Checks if a file is binary by reading the first 1024 bytes and looking for null bytes.

    Args:
        filepath (str): The path to the file to be checked.

    Returns:
        bool: True if the file is binary, False otherwise.
    """
    with open(filepath, 'rb') as file:
        return b'\0' in file.read(1024)
