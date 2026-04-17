from argparse import ArgumentParser, Namespace

from .version import get_version_string

DOWNLOAD_FOLDER = "Downloads"
URLS_FILE = "URLs.txt"

GOFILE_API = "https://api.gofile.io"
GOFILE_API_ACCOUNTS = f"{GOFILE_API}/accounts"

PROGRESS_COLUMNS_SEPARATOR = "•"

PROGRESS_MANAGER_COLORS = {
    "title_color": "light_cyan3",
    "overall_border_color": "bright_blue",
    "task_border_color": "medium_purple",
}

LOG_MANAGER_CONFIG = {
    "colors": {"title_color": "light_cyan3", "border_color": "cyan"},
    "min_column_widths": {"Timestamp": 10, "Event": 15, "Details": 30},
    "column_styles": {
        "Timestamp": "pale_turquoise4",
        "Event": "pale_turquoise1",
        "Details": "pale_turquoise4",
    },
}

MAX_WORKERS = 3
KB = 1024
MB = 1024 * KB

THRESHOLDS = [
    (1 * MB, 8 * KB),
    (10 * MB, 16 * KB),
    (50 * MB, 64 * KB),
    (100 * MB, 128 * KB),
    (250 * MB, 256 * KB),
]

LARGE_FILE_CHUNK_SIZE = 512 * KB
HTTP_STATUS_OK = 200

BASE_HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Encoding": "gzip",
    "Accept": "*/*",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
}


def parse_arguments(*, common_only: bool = False) -> Namespace:
    parser = ArgumentParser(description="GoFile Downloader")

    if not common_only:
        parser.add_argument("url", type=str, help="The URL to process")
        parser.add_argument(
            "password", nargs="?", type=str, help="The password for the download."
        )

    parser.add_argument(
        "--custom-path", type=str, default=None, help="Custom download directory"
    )
    parser.add_argument("--version", action="version", version=get_version_string())

    return parser.parse_args()
