from pathlib import Path


def read_file(filename: str) -> list[str]:
    return Path(filename).read_text(encoding="utf-8").splitlines()


def write_file(filename: str, content: str = "") -> None:
    Path(filename).write_text(content, encoding="utf-8")


def create_directory(directory_name: str) -> None:
    (Path.cwd() / directory_name).mkdir(parents=True, exist_ok=True)
