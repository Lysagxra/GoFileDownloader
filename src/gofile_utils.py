"""Module that provides utility functions for interacting with the GoFile API."""

from __future__ import annotations

import logging
import sys
from hashlib import sha256
from time import time
from urllib.parse import urlencode

import requests

from .config import (
    COMMON_HEADERS,
    GOFILE_API,
    GOFILE_API_ACCOUNTS,
    HTTP_STATUS_OK,
    LOCALE,
    TOKEN_SECRET,
    TOKEN_WINDOW_SEC,
    USER_AGENT,
)


def get_content_id(url: str) -> str | None:
    """Extract and returns the content ID from a GoFile URL."""
    try:
        if url.rstrip("/").split("/")[-2] != "d":
            message = f"Missing ID for URL: {url}"
            logging.error(message)
            return None

        return url.rstrip("/").split("/")[-1]

    except IndexError:
        message = f"{url} is not a valid GoFile URL."
        logging.exception(message)
        return None


def generate_content_url(content_id: str, password: str | None = None) -> None:
    """Generate a URL for accessing content, optionally including a password."""
    base_url = (
        f"{GOFILE_API}/contents/{content_id}"
        "?cache=true&sortField=createTime&sortDirection=1"
    )

    # Only add the password if it's provided
    query_params = {}
    if password:
        query_params["password"] = password

    # If there are additional query parameters, append them
    if query_params:
        return f"{base_url}&{urlencode(query_params)}"

    return base_url


def generate_website_token(account_token: str) -> str:
    """Generate the dynamic X-Website-Token."""
    time_window = str(int(time()) // TOKEN_WINDOW_SEC)
    token_seed = (
        f"{USER_AGENT}::{LOCALE}::{account_token}::{time_window}::{TOKEN_SECRET}"
    )
    return sha256(token_seed.encode()).hexdigest()


def check_response_status(response: requests.Response, filename: str) -> bool:
    """Check if the server response is valid based on status codes."""
    response_is_invalid = (
        response.status_code in (403, 404, 405, 500)
        or response.status_code != HTTP_STATUS_OK
    )

    if response_is_invalid:
        message = (
            f"Invalid response for {filename}. Status code: {{response.status_code}}"
        )
        logging.error(message)
        return False

    return True


def get_account_token() -> str:
    """Retrieve the access token for the created account."""
    account_response = requests.post(
        GOFILE_API_ACCOUNTS,
        headers=COMMON_HEADERS,
        timeout=10,
    ).json()

    if account_response["status"] != "ok":
        logging.error("Account creation failed.")
        sys.exit(1)

    return account_response["data"]["token"]
