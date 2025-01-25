# GoFile Downloader

> This script is a utility for downloading files from GoFile, supporting both
public and password-protected albums.

![Demo](https://github.com/Lysagxra/GoFileDownloader/blob/45eb080468efce402d4e74e5d5b71dcf5b1eac79/misc/Demo.gif)

## Features

- Downloads multiple files from an album concurrently.
- Supports batch downloading via a list of URLs.
- Supports downloading password-protected albums by providing a password.
- Progress indication during downloads.
- Automatically creates a directory structure for organized storage.
- Logs URLs that encounter errors for troubleshooting.

## Dependencies

- Python 3
- `requests` - for HTTP requests
- `rich` - for progress display in the terminal.

## Directory Structure

```
project-root/
├── helpers/
│ ├── managers/
│ │ ├── live_manager.py      # Manages a real-time live display
│ │ ├── log_manager.py       # Manages real-time log updates
│ │ └── progress_manager.py  # Manages progress bars
│ ├── config.py              # Manages constants and settings used across the project
│ ├── download_utils.py      # Utilities for managing the download process
│ ├── file_utils.py          # Utilities for managing file operations
│ ├── general_utils.py       # Miscellaneous utility functions
│ └── gofile_utils.py        # Utilities for checking GoFile status and URL validation
├── downloader.py            # Module for initiating downloads from specified GoFile URLs
├── main.py                  # Main script to run the downloader
├── URLs.txt                 # Text file listing album URLs to be downloaded
└── session_log.txt          # Log file for recording session details
```

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Lysagxra/GoFileDownloader.git
```

2. Navigate to the project directory:

```bash
cd GoFileDownloader
```

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Single Album Download

To download a single album, you can use `downloader.py`, running the script with a valid album URL.

### Usage

```bash
python3 downloader.py <gofile_url>
```

### Example

```
python3 downloader.py https://gofile.io/d/clgeTz
```

## Password-Protected Album Download

To download a password-protected album, you can use `downloader.py`, running the script with the album password.

### Usage

```bash
python3 downloader.py <gofile_url> <password>
```

### Example

```
python3 downloader.py https://gofile.io/d/hXHGR1 TestPassword
```

## Batch Download

To batch download from multiple URLs, you can use the `main.py` script. This script reads URLs from a file named `URLs.txt` and downloads each one using the media downloader.

### Usage

1. Create a file named `URLs.txt` in the root of your project, listing each URL on a new line.

- Example of `URLs.txt`:

```
https://gofile.io/d/clgeTz
https://gofile.io/d/FrYeIy
https://gofile.io/d/jLWdTZ
```

- Ensure that each URL is on its own line without any extra spaces.
- You can add as many URLs as you need, following the same format.

2. Run the batch download script:

```
python3 main.py
```

3. The downloaded files will be saved in the `Downloads` directory.
