import os
from pathlib import Path
from typing import List, Optional, Tuple, Union

from wexample_helpers.const.types import FileStringOrPath


def file_change_mode(path: str, mode: int) -> None:
    try:
        if not os.path.islink(path):
            os.chmod(path, mode)
    except FileNotFoundError:
        pass


def file_change_mode_recursive(
    path: str, mode: int, follow_symlinks: bool = True
) -> None:
    file_change_mode(path=path, mode=mode)

    # If the path is a directory (and not a symlink if follow_symlinks is False),
    # loop through its contents and call the function recursively
    if os.path.isdir(path) and (follow_symlinks or not os.path.islink(path)):
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            file_change_mode_recursive(item_path, mode, follow_symlinks)


def file_list_subdirectories(path: str) -> List[str]:
    subdirectories = []
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isdir(item_path) and not item.startswith("."):
            subdirectories.append(os.path.basename(item_path))

    subdirectories.sort()

    return subdirectories


def file_mode_num_to_octal(num: int) -> str:
    return str(oct(num)[-3:])


def file_mode_octal_to_num(mode: Union[str, int]) -> int:
    return int(mode, 8)


def file_path_get_octal_mode(path: Path) -> str:
    return file_mode_num_to_octal(path.stat().st_mode)


def file_path_get_mode_num(path: Path) -> int:
    return path.stat().st_mode & 0o777


def file_read(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def file_read_or_default(file_path: str, default: str = "") -> str:
    try:
        return file_read(file_path=file_path)
    except Exception as e:
        return default


def file_remove_file_if_exists(file: str) -> None:
    if os.path.isfile(file) or os.path.islink(file):
        os.remove(file)


def file_resolve_path(path: FileStringOrPath) -> Path:
    return path if path is Path else Path(path)


def file_touch(path: str, times: Optional[Tuple[int, int]] = None) -> None:
    with open(path, "a"):
        os.utime(path, times)


def file_validate_mode_octal(mode: Union[str, int]) -> bool:
    if len(mode) != 3:
        return False
    for char in mode:
        if char not in "01234567":
            return False
    return True


def file_validate_mode_octal_or_fail(mode: Union[str, int]) -> bool:
    if not file_validate_mode_octal(mode):
        raise Exception(f"Bad mode format {mode}")
    return True


def file_write(file_path: str, content: str) -> None:
    with open(file_path, "w") as f:
        f.write(content)


def file_get_directories(path: str, recursive: bool = False) -> List[str]:
    directories = []

    if not recursive:
        for entry in os.listdir(path):
            full_path = os.path.join(path, entry)
            if os.path.isdir(full_path):
                directories.append(full_path)

    else:
        for root, dirs, files in os.walk(path):
            for directory in dirs:
                dir_path = os.path.join(root, directory)
                directories.append(dir_path)

    return directories
