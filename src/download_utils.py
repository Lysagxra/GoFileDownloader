import logging
from pathlib import Path

import httpx

from src.managers.progress_manager import ProgressManager

from .config import LARGE_FILE_CHUNK_SIZE, THRESHOLDS


def get_chunk_size(file_size: int) -> int:
    for threshold, chunk_size in THRESHOLDS:
        if file_size < threshold:
            return chunk_size
    return LARGE_FILE_CHUNK_SIZE


async def save_file_with_progress(
    response: httpx.Response,
    download_path: Path,
    task: int,
    progress_manager: ProgressManager,
) -> None:
    file_size = int(response.headers.get("Content-Length", -1))
    if file_size == -1:
        logging.exception("Content length not provided in response headers.")
        return

    chunk_size = get_chunk_size(file_size)
    total_downloaded = 0

    with download_path.open("wb") as file:
        async for chunk in response.aiter_bytes(chunk_size=chunk_size):
            if chunk:
                file.write(chunk)
                total_downloaded += len(chunk)
                progress_manager.update_task(
                    task, completed=(total_downloaded / file_size) * 100
                )
