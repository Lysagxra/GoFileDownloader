import logging
import sys
from hashlib import sha256
from time import time
from urllib.parse import urlencode

import httpx

from .config import GOFILE_API, GOFILE_API_ACCOUNTS, HTTP_STATUS_OK


def get_content_id(url: str) -> str | None:
    try:
        if url.rstrip("/").split("/")[-2] != "d":
            logging.error(f"Missing ID for URL: {url}")
            return None
        return url.rstrip("/").split("/")[-1]
    except IndexError:
        logging.exception(f"{url} is not a valid GoFile URL.")
        return None


def generate_content_url(content_id: str, password: str | None = None) -> str:
    base_url = f"{GOFILE_API}/contents/{content_id}?cache=true&sortField=createTime&sortDirection=1"
    return f"{base_url}&{urlencode({'password': password})}" if password else base_url


def generate_website_token(account_token: str) -> str:
    time_window = str(int(time()) // 14400)
    token_seed = f"Mozilla/5.0::en-US::{account_token}::{time_window}::5d4f7g8sd45fsd"
    return sha256(token_seed.encode()).hexdigest()


def check_response_status(response: httpx.Response, filename: str) -> bool:
    if response.status_code != HTTP_STATUS_OK:
        logging.error(f"Invalid response for {filename}. Status code: {response.status_code}")
        return False
    return True


def get_account_token() -> str:
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Encoding": "gzip",
        "Accept": "*/*",
        "Connection": "keep-alive",
    }

    with httpx.Client(timeout=15.0) as client:
        account_response = client.post(GOFILE_API_ACCOUNTS, headers=headers).json()

    if account_response["status"] != "ok":
        logging.error("Account creation failed.")
        sys.exit(1)

    return account_response["data"]["token"]
