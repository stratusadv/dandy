from pathlib import Path


from dandy.core.path.tools import get_file_path_or_exception


def append_to_file(file_path: Path | str, content: str):
    if file_exists(file_path):
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(content)

    else:
        write_to_file(file_path, content)


def file_exists(file_path: Path | str) -> bool:
    return Path(file_path).exists()


def make_directory(directory_path: Path | str):
    Path(directory_path).mkdir(parents=True, exist_ok=True)


def read_from_file(file_path: Path | str) -> str:
    get_file_path_or_exception(file_path=file_path)

    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def remove_directory(directory_path: Path | str):
    Path(directory_path).rmdir()


def remove_file(file_path: Path | str):
    Path(file_path).unlink(missing_ok=True)


def write_to_file(file_path: Path | str, content: str):
    file_path = Path(file_path)

    make_directory(file_path.parent)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


