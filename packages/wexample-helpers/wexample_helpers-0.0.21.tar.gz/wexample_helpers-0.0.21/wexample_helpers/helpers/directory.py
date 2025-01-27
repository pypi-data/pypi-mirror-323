import os
import shutil
from typing import Any, List

from wexample_helpers.const.types import AnyCallable
from wexample_helpers.helpers.file import file_read


def directory_remove_tree_if_exists(directory: str) -> None:
    if os.path.exists(directory):
        shutil.rmtree(directory)


def directory_execute_inside(target_dir: str, callback: AnyCallable) -> Any:
    original_dir = os.getcwd()
    os.chdir(target_dir)
    response = callback()
    os.chdir(original_dir)

    return response


def directory_get_base_name(path: str) -> str:
    return os.path.basename(os.path.normpath(path))


def directory_get_parent_path(path: str) -> str:
    return os.path.dirname(os.path.normpath(path)) + os.sep


def directory_empty_dir(dir_path: str) -> None:
    # Iterate over each item in the directory
    for item_name in os.listdir(dir_path):
        # Construct the full path to the item
        item_path = os.path.join(dir_path, item_name)
        if os.path.isfile(item_path) or os.path.islink(item_path):
            os.remove(item_path)  # Remove the file or link
        elif os.path.isdir(item_path):
            # Recursively remove the directory
            shutil.rmtree(item_path)


def directory_list_files(dir_path: str) -> List[str]:
    """List all files in directory and subdirectories, sorted alphabetically."""
    file_paths = []
    for root, dirs, files in os.walk(dir_path):
        files.sort()  # Sort files alphabetically
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.isfile(file_path):  # Ensure it's a file
                file_paths.append(file_path)
    return file_paths


def directory_aggregate_all_files_form_dir(dir_path: str) -> str:
    return directory_aggregate_all_files(directory_list_files(dir_path))


def directory_aggregate_all_files(file_paths: List[str]) -> str:
    """Aggregate contents of the given list of file paths."""
    aggregated_content = ""
    for file_path in file_paths:
        aggregated_content += file_read(file_path) + os.linesep
    return aggregated_content
