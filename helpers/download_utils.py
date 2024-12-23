"""
This module provides utilities for handling file downloads with progress
tracking.
"""

KB = 1024
MB = 1024 * KB

def get_chunk_size(file_size):
    """
    Determines the optimal chunk size based on the file size.

    Args:
        file_size (int): The size of the file in bytes.

    Returns:
        int: The optimal chunk size in bytes.
    """
    thresholds = [
        (1 * MB, 8 * KB),      # Less than 1 MB
        (10 * MB, 16 * KB),    # 1 MB to 10 MB
        (50 * MB, 64 * KB),    # 10 MB to 50 MB
        (100 * MB, 128 * KB),  # 50 MB to 100 MB
        (250 * MB, 256 * KB),  # 100 MB to 250 MB
    ]

    for threshold, chunk_size in thresholds:
        if file_size < threshold:
            return chunk_size

    return 1 * MB

def save_file_with_progress(response, download_path, task, progress_manager):
    """
    Saves the file from the response to the specified path while updating
    the download progress.

    Args:
        response (Response): The response object containing the file data.
        download_path (str): The path where the file will be saved.
        task (Task): The task object representing the current download task.
        progress_manager (ProgressManager): An object responsible for managing
                                            and updating task progress.

    Raises:
        ValueError: If the content length is not provided in the response
                    headers.
    """
    file_size = int(response.headers.get("Content-Length", -1))
    if file_size == -1:
        raise ValueError("Content length not provided in response headers.")

    chunk_size = get_chunk_size(file_size)
    total_downloaded = 0

    with open(download_path, 'ab') as file:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk is not None:
                file.write(chunk)
                total_downloaded += len(chunk)
                completed = (total_downloaded / file_size) * 100
                progress_manager.update_task(task, completed=completed)
