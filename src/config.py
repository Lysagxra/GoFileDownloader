"""Centralized configuration module for managing constants used across the project.

These configurations aim to improve modularity and readability by consolidating settings
into a single location.
"""

# ============================
# Paths and Files
# ============================
from argparse import ArgumentParser, Namespace
from collections import deque
from dataclasses import dataclass, field

DOWNLOAD_FOLDER = "Downloads"  # The folder where downloaded files will be stored.
URLS_FILE = "URLs.txt"         # The file containing the list of URLs to process.
SESSION_LOG = "session.log"    # The file used to log session errors.

# ============================
# API Endpoints
# ============================
GOFILE_API = "https://api.gofile.io"            # The base URL for the GoFile API.
GOFILE_API_ACCOUNTS = f"{GOFILE_API}/accounts"  # The endpoint for GoFile account
                                                # related operations.

# ============================
# Command Usage Instructions
# ============================
DEFAULT_USAGE = "python3 downloader.py <album_url>"
PASSWORD_USAGE = "python3 downloader.py <album_url> <password>"  # noqa: S105

# ============================
# UI & Table Settings
# ============================
BUFFER_SIZE = 5                   # Maximum number of items showed in buffers.
PROGRESS_COLUMNS_SEPARATOR = "•"  # Visual separator used between progress bar columns.

# Colors used for the progress manager UI elements
PROGRESS_MANAGER_COLORS = {
    "title_color": "light_cyan3",           # Title color for progress panels.
    "overall_border_color": "bright_blue",  # Border color for overall progress panel.
    "task_border_color": "medium_purple",   # Border color for task progress panel.
}

# Setting used for the log manager UI elements
LOG_MANAGER_CONFIG = {
    "colors": {
        "title_color": "light_cyan3",  # Title color for log panel.
        "border_color": "cyan",        # Border color for log panel.
    },
    "min_column_widths": {
        "Timestamp": 10,
        "Event": 15,
        "Details": 30,
    },
    "column_styles": {
        "Timestamp": "pale_turquoise4",
        "Event": "pale_turquoise1",
        "Details": "pale_turquoise4",
    },
}

# ============================
# Download Settings
# ============================
MAX_WORKERS = 3  # The maximum number of threads for concurrent downloads.

# Constants for file sizes, expressed in bytes.
KB = 1024
MB = 1024 * KB

# Thresholds for file sizes and corresponding chunk sizes used during download.
THRESHOLDS = [
    (1 * MB, 8 * KB),      # Less than 1 MB
    (10 * MB, 16 * KB),    # 1 MB to 10 MB
    (50 * MB, 64 * KB),    # 10 MB to 50 MB
    (100 * MB, 128 * KB),  # 50 MB to 100 MB
    (250 * MB, 256 * KB),  # 100 MB to 250 MB
]

# Default chunk size for files larger than the largest threshold.
LARGE_FILE_CHUNK_SIZE = 512 * KB

# ============================
# HTTP / Network
# ============================
# HTTP status codes
HTTP_STATUS_OK = 200

# Base headers common for all requests
BASE_HEADERS = {
    "Accept-Encoding": "gzip",
    "User-Agent": "Mozilla/5.0",
    "Accept": "*/*",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
}

# ============================
# Data Classes
# ============================
@dataclass
class ProgressConfig:
    """Configuration for progress bar settings."""

    task_name: str
    item_description: str
    color: str = PROGRESS_MANAGER_COLORS["title_color"]
    panel_width = 40
    overall_buffer: deque = field(default_factory=lambda: deque(maxlen=BUFFER_SIZE))

# ============================
# Argument Parsing
# ============================
def add_common_arguments(parser: ArgumentParser) -> None:
    """Add arguments shared across parsers."""
    parser.add_argument(
        "--custom-path",
        type=str,
        default=None,
        help="The directory where the downloaded content will be saved.",
    )


def setup_parser(
        *, include_url: bool = False, include_password: bool = False,
    ) -> ArgumentParser:
    """Set up parser with optional argument groups."""
    parser = ArgumentParser(description="Command-line arguments.")

    if include_url:
        parser.add_argument("url", type=str, help="The URL to process")

    if include_password:
        parser.add_argument(
            "password",
            nargs="?",
            type=str,
            help="The password for the download.",
        )

    add_common_arguments(parser)
    return parser


def parse_arguments(*, common_only: bool = False) -> Namespace:
    """Full argument parser (including URL, filters, and common)."""
    parser = (
        setup_parser() if common_only
        else setup_parser(include_url=True, include_password=True)
    )
    return parser.parse_args()
