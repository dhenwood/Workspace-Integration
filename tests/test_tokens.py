import time
from unittest.mock import MagicMock

import tokens


def fake_token_response(access_token="new-access"):
    resp = MagicMock(ok=True)
    resp.json.return_value = {
        "access_token": access_token,
        "expires_in": 3600,
        "refresh_token": "new-refresh",
        "refresh_token_expires_in": 7776000,
    }
    return resp


def test_token_is_refreshed_once_then_cached(tmp_path, monkeypatch):
    post = MagicMock(return_value=fake_token_response())
    monkeypatch.setattr(tokens.requests, "post", post)
    store = tokens.TokenStore(env_path=tmp_path / ".env")

    assert store.get() == "new-access"
    assert store.get() == "new-access"
    assert post.call_count == 1


def test_new_tokens_are_saved_to_env_file(tmp_path, monkeypatch):
    monkeypatch.setattr(tokens.requests, "post", MagicMock(return_value=fake_token_response()))
    env_file = tmp_path / ".env"
    tokens.TokenStore(env_path=env_file).get()

    saved = env_file.read_text()
    assert "ACCESS_TOKEN='new-access'" in saved
    assert "REFRESH_TOKEN='new-refresh'" in saved


def test_token_close_to_expiry_is_refreshed(tmp_path, monkeypatch):
    post = MagicMock(return_value=fake_token_response("fresh"))
    monkeypatch.setattr(tokens.requests, "post", post)
    store = tokens.TokenStore(env_path=tmp_path / ".env")
    store._access_token = "old"
    store._expires_at = time.time() + 10  # inside the refresh margin

    assert store.get() == "fresh"
