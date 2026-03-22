"""Package that rovides utility modules and functions to support the main application.

These utilities include functions for downloading, file management, URL handling,
progress tracking, and more.

Modules:
    - config: Constants and settings used across the project.
    - download_utils: Functions for handling downloads.
    - file_utils: Utilities for managing file operations.
    - general_utils: Miscellaneous utility functions.
    - gofile_utils: Functions for checking Bunkr status and URL validation.

This package is designed to be reusable and modular, allowing its components to be
easily imported and used across different parts of the application.
"""

# src/__init__.py

from .version import __author__, __title__, __version__, version_info

__all__ = [
    "__author__",
    "__title__",
    "__version__",
    "config",
    "download_utils",
    "file_utils",
    "general_utils",
    "gofile_utils",
    "version_info",
]
