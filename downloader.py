"""Downloader module for downloading files from GoFile.

Example usage:
    python3 gofile_downloader.py <album_url>
    python3 gofile_downloader.py <album_url> <password>
"""

from __future__ import annotations

import hashlib
import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import TYPE_CHECKING

import requests

from src.config import (
    BASE_HEADERS,
    DEFAULT_USAGE,
    DOWNLOAD_FOLDER,
    MAX_WORKERS,
    PASSWORD_USAGE,
    parse_arguments,
)
from src.download_utils import save_file_with_progress
from src.file_utils import create_download_directory
from src.general_utils import clear_terminal
from src.gofile_utils import (
    check_response_status,
    generate_content_url,
    get_account_token,
    get_content_id,
)
from src.managers.live_manager import LiveManager, initialize_managers

if TYPE_CHECKING:
    from argparse import Namespace

DEFAULT_DOWNLOAD_PATH = Path.cwd() / DOWNLOAD_FOLDER


class Downloader:
    """Class to handle downloading files from a specified URL in parallel.

    It manages the download process, including handling authentication, partial
    downloads, and error checking. This class supports resuming interrupted downloads,
    verifying file integrity, and organizing downloads into appropriate directories.
    """

    def __init__(
        self,
        url: str,
        live_manager: LiveManager,
        args: Namespace | None = None,
    ) -> None:
        """Initialize the downloader with the given parameters."""
        self.url = url
        self.live_manager = live_manager
        self.password = args.password if "password" in args else None
        self.max_workers = MAX_WORKERS
        self.token = get_account_token()

        self.download_path = (
            Path(args.custom_path)
            if args.custom_path is not None
            else DEFAULT_DOWNLOAD_PATH
        )
        self.download_path.mkdir(parents=True, exist_ok=True)
        os.chdir(self.download_path)

    def download_item(self, current_task: int, file_info: tuple) -> None:
        """Download a single file."""
        filename = file_info["filename"]
        final_path = Path(file_info["download_path"]) / filename
        download_link = file_info["download_link"]

        # Skip file if it already exists and is not empty
        if Path(final_path).exists():
            self.live_manager.update_log(
                event="Skipped download",
                details=f"{filename} has already been downloaded.",
            )
            return

        headers = self._prepare_headers(url=download_link)

        # Perform the download and handle possible errors
        with requests.get(
            download_link,
            headers=headers,
            stream=True,
            timeout=(10, 30),
        ) as response:
            if not check_response_status(response, filename):
                return

            task_id = self.live_manager.add_task(current_task=current_task)
            save_file_with_progress(response, final_path, task_id, self.live_manager)

    def run_in_parallel(self, content_directory: str, files_info: tuple) -> None:
        """Execute the file downloads in parallel."""
        os.chdir(content_directory)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            for current_task, item_info in enumerate(files_info):
                executor.submit(self.download_item, current_task, item_info)

        os.chdir(self.download_path)

    def _prepare_headers(
        self,
        url: str | None = None,
        *,
        include_auth: bool = False,
    ) -> dict:
        """Prepare the HTTP headers for the request."""
        # Base headers common for all requests
        headers = BASE_HEADERS

        # If 'include_auth' is True, add the 'Authorization' header for Bearer
        # authentication and include the 'X-Website-Token' header with a specific token.
        if include_auth:
            headers["Authorization"] = f"Bearer {self.token}"
            headers["X-Website-Token"] = "4fd6sg89d7s6"

        else:
            # Add Referer and Origin headers if URL is provided
            if url:
                adjusted_url = url + ("/" if not url.endswith("/") else "")
                headers["Referer"] = adjusted_url
                headers["Origin"] = url

            # Include the Cookie header for authentication when URL is not needed
            headers["Cookie"] = f"accountToken={self.token}"

        return headers

    def parse_links(
        self,
        identifier: str,
        files_info: tuple,
        password: str | None = None,
    ) -> None:
        """Parse the URL for file links and populates a list with file information."""

        def append_file_info(files_info: tuple, data: dict) -> None:
            files_info.append(
                {
                    "download_path": str(Path.cwd()),
                    "filename": data["name"],
                    "download_link": data["link"],
                },
            )

        def check_password(data: dict) -> bool:
            password_exists = "password" in data
            password_status_ok = data.get("passwordStatus") == "passwordOk"
            return password_exists and not password_status_ok

        content_url = generate_content_url(identifier, password=password)
        headers = self._prepare_headers(include_auth=True)

        response = requests.get(content_url, headers=headers, timeout=10).json()
        if response["status"] != "ok":
            self.live_manager.update_log(
                event="Failed request",
                details=f"Failed to get a link as response from {content_url}.",
            )
            return

        data = response["data"]
        if check_password(data):
            self.live_manager.update_log(
                event="Missing password",
                details="The URL requires a valid password. "
                "Please provide one to proceed.",
            )
            return

        # Handle folder
        if data["type"] == "folder":
            create_download_directory(data["name"])
            os.chdir(data["name"])

            for child_id in data["children"]:
                child = data["children"][child_id]

                if child["type"] == "folder":
                    self.parse_links(child["id"], files_info, password)
                else:
                    append_file_info(files_info, child)

            os.chdir(os.path.pardir)

        # Handle file
        else:
            append_file_info(files_info, data)

    def initialize_download(self) -> None:
        """Initialize the download process."""
        content_id = get_content_id(self.url)
        content_directory = self.download_path / content_id
        create_download_directory(content_directory)

        files_info = []
        hashed_password = (
            hashlib.sha256(self.password.encode()).hexdigest()
            if self.password
            else self.password
        )
        self.parse_links(content_id, files_info, hashed_password)

        # Remove the root content directory if there's no file or subdirectory.
        if not os.listdir(content_directory) and not files_info:
            Path(content_directory).rmdir()
            return

        self.live_manager.add_overall_task(
            description=content_id,
            num_tasks=len(files_info),
        )
        self.run_in_parallel(content_directory, files_info)


def handle_download_process(
    url: str,
    live_manager: LiveManager,
    args: Namespace | None = None,
) -> None:
    """Handle the process of downloading content from a specified URL."""
    if url is None:
        usage = f"Default usage: {DEFAULT_USAGE}\nPassword usage: {PASSWORD_USAGE}\n"
        logging.error(usage)
        sys.exit(1)

    downloader = Downloader(url=url, live_manager=live_manager, args=args)
    downloader.initialize_download()


def main() -> None:
    """Process command-line arguments to download an album from a specified URL."""
    clear_terminal()
    args = parse_arguments()
    live_manager = initialize_managers()

    try:
        with live_manager.live:
            handle_download_process(args.url, live_manager, args=args)
            live_manager.stop()

    except KeyboardInterrupt:
        sys.exit(1)


if __name__ == "__main__":
    main()
