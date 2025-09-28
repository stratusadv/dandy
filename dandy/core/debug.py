import warnings
import traceback


def dandy_warning_handler(message, category, filename, lineno, file=None, line=None):
    print(f"Warning: {message}")
    print(f"File: {filename}:{lineno}")
    traceback.print_stack()


warnings.showwarning = dandy_warning_handler
