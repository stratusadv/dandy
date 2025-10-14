import warnings
import traceback
from typing import TextIO

def dandy_warning_handler(
    message: Warning | str,
    category: type[Warning],
    filename: str,
    lineno: int,
    file: TextIO | None = None,
    line: str | None = None,
):
    print(f"Warning: {message}")
    print(f"Category: {category.__name__}")
    print(f"File: {filename}:{lineno}")

    if file:
        print(f"File IO: {file.name}:{lineno}")

    if line:
        print(f"Source: {line.strip()}")
    print("\nStack trace:")

    traceback.print_stack(limit=-2)

warnings.showwarning = dandy_warning_handler
