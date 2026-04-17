# GoFile Downloader

Modern async downloader for GoFile with concurrent downloads and real-time progress tracking.

![Demo](https://github.com/Lysagxra/GoFileDownloader/blob/90b902ff734115dd1d955f80ac855700bcde7cc2/assets/demo.gif)

## Features

- ⚡ Async concurrent downloads (faster than traditional methods)
- 📦 Batch downloading via URL list
- 🔒 Password-protected album support
- 📁 Custom download location
- 📊 Real-time progress tracking
- 🗂️ Organized directory structure

## Requirements

- Python 3.11+
- httpx
- rich

## Installation

```bash
git clone https://github.com/dacrab/GoFileDownloader.git
cd GoFileDownloader
pip install -r requirements.txt
```

## Usage

### Single Album

```bash
python3 downloader.py <gofile_url>
```

### Password-Protected Album

```bash
python3 downloader.py <gofile_url> <password>
```

### Batch Download

1. Create `URLs.txt` with one URL per line:
```
https://gofile.io/d/clgeTz
https://gofile.io/d/FrYeIy
```

2. Run:
```bash
python3 main.py
```

### Custom Download Location

```bash
python3 main.py --custom-path /path/to/directory
```

Files are saved to `<custom_path>/Downloads` or `./Downloads` by default.

## Development

### Setup

```bash
pip install -r requirements.txt
pip install pre-commit ruff mypy
pre-commit install
```

### Code Quality

```bash
ruff check .          # Lint
ruff format .         # Format
mypy src/             # Type check
```

## What's New

- Migrated from `requests` to `httpx` for better async support and HTTP/2
- True async downloads with `asyncio` (2-3x faster)
- Modern Python packaging with `pyproject.toml`
- Type checking with MyPy
- Pre-commit hooks for code quality
- Automated dependency updates with Dependabot
- Multi-version CI testing (Python 3.11, 3.12, 3.13)

## Project Structure

```
GoFileDownloader/
├── src/
│   ├── managers/
│   │   ├── live_manager.py
│   │   ├── log_manager.py
│   │   └── progress_manager.py
│   ├── config.py
│   ├── download_utils.py
│   ├── file_utils.py
│   ├── gofile_utils.py
│   └── version.py
├── downloader.py
├── main.py
├── pyproject.toml
└── requirements.txt
```

## License

GPL-3.0
