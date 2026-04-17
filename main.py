import os
import sys
from pathlib import Path

from downloader import Downloader
from src.config import URLS_FILE, parse_arguments
from src.file_utils import read_file, write_file
from src.managers.live_manager import LiveManager, ProgressManager, LoggerTable


def main() -> None:
    os.system("cls" if os.name == "nt" else "clear")  # noqa: S605
    
    args = parse_arguments(common_only=True)
    urls = [url.strip() for url in read_file(URLS_FILE) if url.strip()]
    
    if not urls:
        print("No URLs found in URLs.txt")
        return
    
    progress_manager = ProgressManager(task_name="Album", item_description="File")
    logger_table = LoggerTable()
    live_manager = LiveManager(progress_manager, logger_table)

    try:
        with live_manager.live:
            for url in urls:
                Downloader(url, live_manager, args).initialize_download()
            live_manager.stop()
    except KeyboardInterrupt:
        sys.exit(1)

    write_file(URLS_FILE)


if __name__ == "__main__":
    main()
