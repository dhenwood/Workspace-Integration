"""OAuth token handling for the Workspace Integration.

The access token is kept in memory and refreshed shortly before it expires.
New tokens are also written back to .env so a restart can pick them up.
"""
import logging
import os
import threading
import time
from pathlib import Path

import requests
from dotenv import load_dotenv, set_key

TOKEN_URL = "https://webexapis.com/v1/access_token"
ENV_PATH = Path(__file__).with_name(".env")
REFRESH_MARGIN_SECONDS = 60  # refresh a little early so a token never expires mid-request

log = logging.getLogger(__name__)
load_dotenv(ENV_PATH)


class TokenStore:
    def __init__(self, env_path=ENV_PATH):
        self._env_path = Path(env_path)
        self._lock = threading.Lock()  # Flask serves requests on several threads
        self._access_token = os.environ.get("ACCESS_TOKEN") or None
        self._expires_at = int(os.environ.get("ACCESS_TOKEN_EXPIRES_AT") or 0)
        self._refresh_token = os.environ.get("REFRESH_TOKEN")

    def get(self):
        """Return a valid access token, refreshing it first if needed."""
        with self._lock:
            if self._access_token and time.time() < self._expires_at - REFRESH_MARGIN_SECONDS:
                return self._access_token
            self._refresh()
            return self._access_token

    def _refresh(self):
        log.info("Refreshing access token")
        resp = requests.post(
            TOKEN_URL,
            data={
                "grant_type": "refresh_token",
                "refresh_token": self._refresh_token,
                "client_id": os.environ["CLIENT_ID"],
                "client_secret": os.environ["CLIENT_SECRET"],
            },
            timeout=30,
        )
        if not resp.ok:
            log.error("Token refresh failed: %s %s", resp.status_code, resp.text[:500])
        resp.raise_for_status()

        tokens = resp.json()
        now = int(time.time())
        self._access_token = tokens["access_token"]
        self._expires_at = now + tokens["expires_in"]
        self._refresh_token = tokens["refresh_token"]
        self._save(refresh_expires_at=now + tokens["refresh_token_expires_in"])

    def _save(self, refresh_expires_at):
        self._env_path.touch(exist_ok=True)
        path = str(self._env_path)
        set_key(path, "ACCESS_TOKEN", self._access_token)
        set_key(path, "ACCESS_TOKEN_EXPIRES_AT", str(self._expires_at))
        set_key(path, "REFRESH_TOKEN", self._refresh_token)
        set_key(path, "REFRESH_TOKEN_EXPIRES_AT", str(refresh_expires_at))


_store = TokenStore()


def get_token():
    return _store.get()
