import asyncio
import hashlib
import os
import sys
from pathlib import Path

import httpx

from src.config import BASE_HEADERS, DOWNLOAD_FOLDER, MAX_WORKERS, parse_arguments
from src.download_utils import save_file_with_progress
from src.file_utils import create_directory
from src.gofile_utils import (
    check_response_status,
    generate_content_url,
    generate_website_token,
    get_account_token,
    get_content_id,
)
from src.managers.live_manager import LiveManager, LoggerTable, ProgressManager


class Downloader:
    def __init__(self, url: str, live_manager: LiveManager, args=None) -> None:
        self.url = url
        self.live_manager = live_manager
        self.password = args.password if args and hasattr(args, "password") else None
        self.token = get_account_token()
        self.download_path = (
            Path(args.custom_path)
            if args and args.custom_path
            else Path.cwd() / DOWNLOAD_FOLDER
        )
        self.download_path.mkdir(parents=True, exist_ok=True)

    async def download_item(
        self, client: httpx.AsyncClient, current_task: int, file_info: dict
    ) -> None:
        filename = file_info["filename"]
        final_path = Path(file_info["download_path"]) / filename

        if final_path.exists():
            self.live_manager.update_log(event="Skipped", details=f"{filename} exists")
            return

        headers = BASE_HEADERS.copy()
        headers["Cookie"] = f"accountToken={self.token}"

        try:
            async with client.stream(
                "GET", file_info["download_link"], headers=headers, timeout=30.0
            ) as response:
                if check_response_status(response, filename):
                    task_id = self.live_manager.add_task(current_task=current_task)
                    await save_file_with_progress(
                        response, final_path, task_id, self.live_manager
                    )
        except httpx.TimeoutException:
            self.live_manager.update_log(
                event="Timeout", details=f"{filename} timed out"
            )
        except Exception as e:
            self.live_manager.update_log(event="Error", details=f"{filename}: {e}")

    def parse_links(
        self,
        identifier: str,
        files_info: list,
        password: str | None = None,
        base_path: Path | None = None,
    ) -> None:
        if base_path is None:
            base_path = self.download_path / identifier
            create_directory(base_path)

        headers = BASE_HEADERS.copy()
        headers["Authorization"] = f"Bearer {self.token}"
        headers["X-Website-Token"] = generate_website_token(self.token)

        with httpx.Client(timeout=10.0) as client:
            response = client.get(
                generate_content_url(identifier, password), headers=headers
            )
            data = response.json()

        if data["status"] != "ok":
            self.live_manager.update_log(
                event="Failed", details=f"Invalid response for {identifier}"
            )
            return

        content = data["data"]
        if "password" in content and content.get("passwordStatus") != "passwordOk":
            self.live_manager.update_log(
                event="Password required", details="Invalid password"
            )
            return

        if content["type"] == "folder":
            folder_path = base_path / content["name"]
            create_directory(folder_path)

            for child in content["children"].values():
                if child["type"] == "folder":
                    self.parse_links(child["id"], files_info, password, folder_path)
                else:
                    files_info.append(
                        {
                            "download_path": str(folder_path),
                            "filename": child["name"],
                            "download_link": child["link"],
                        }
                    )
        else:
            files_info.append(
                {
                    "download_path": str(base_path),
                    "filename": content["name"],
                    "download_link": content["link"],
                }
            )

    async def download_all(self, files_info: list) -> None:
        async with httpx.AsyncClient(
            limits=httpx.Limits(max_connections=MAX_WORKERS)
        ) as client:
            tasks = [
                self.download_item(client, i, file_info)
                for i, file_info in enumerate(files_info)
            ]
            await asyncio.gather(*tasks)

    def initialize_download(self) -> None:
        content_id = get_content_id(self.url)
        if not content_id:
            return

        files_info = []
        hashed_password = (
            hashlib.sha256(self.password.encode()).hexdigest()
            if self.password
            else None
        )
        self.parse_links(content_id, files_info, hashed_password)

        if not files_info:
            return

        self.live_manager.add_overall_task(
            description=content_id, num_tasks=len(files_info)
        )
        asyncio.run(self.download_all(files_info))


def main() -> None:
    os.system("cls" if os.name == "nt" else "clear")
    args = parse_arguments()

    progress_manager = ProgressManager(task_name="Album", item_description="File")
    logger_table = LoggerTable()
    live_manager = LiveManager(progress_manager, logger_table)

    try:
        with live_manager.live:
            Downloader(args.url, live_manager, args).initialize_download()
            live_manager.stop()
    except KeyboardInterrupt:
        sys.exit(1)


if __name__ == "__main__":
    main()
