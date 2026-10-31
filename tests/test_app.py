import base64
import time
from types import SimpleNamespace

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import ec

import app as app_module

AUTH = {"Authorization": "Basic " + base64.b64encode(b"hook-user:hook-pass").decode()}
PROMPT_EVENT = {
    "type": "events",
    "deviceId": "dev-1",
    "workspaceId": "ws-1",
    "events": [{"key": "UserInterface.Message.Prompt.Display", "value": {"Title": "Cisco Spaces Smart Workspaces"}}],
}


class InlineExecutor:
    """Runs submitted work straight away so tests can check the result."""

    def submit(self, fn, *args):
        fn(*args)


@pytest.fixture
def client(monkeypatch):
    calls = []
    monkeypatch.setattr(app_module, "_worker", InlineExecutor())
    monkeypatch.setattr(app_module.webex, "set_on_hold", lambda *args: calls.append(args))
    test_client = app_module.app.test_client()
    test_client.on_hold_calls = calls
    return test_client


@pytest.fixture
def signing_key(monkeypatch):
    private_key = ec.generate_private_key(ec.SECP256R1())
    fake_jwks = SimpleNamespace(get_signing_key_from_jwt=lambda token: SimpleNamespace(key=private_key.public_key()))
    monkeypatch.setitem(app_module._jwk_clients, app_module.DEFAULT_JWKS, fake_jwks)
    return private_key


def make_jwt(key, **claims):
    payload = {"appId": "test-app-id", "action": "healthCheck", "iat": int(time.time()), **claims}
    return jwt.encode(payload, key, algorithm="ES256")


def test_prompt_event_puts_room_on_hold(client):
    resp = client.post("/onholdintegration", json=PROMPT_EVENT, headers=AUTH)
    assert resp.status_code == 200
    assert client.on_hold_calls == [("dev-1", "ws-1", True)]


def test_booking_event_takes_room_off_hold(client):
    event = {**PROMPT_EVENT, "events": [{"key": "Bookings.BookingRequested", "value": {"Title": "x"}}]}
    client.post("/onholdintegration", json=event, headers=AUTH)
    assert client.on_hold_calls == [("dev-1", "ws-1", False)]


def test_other_prompt_titles_are_ignored(client):
    event = {**PROMPT_EVENT, "events": [{"key": "UserInterface.Message.Prompt.Display", "value": {"Title": "Hi"}}]}
    client.post("/onholdintegration", json=event, headers=AUTH)
    assert client.on_hold_calls == []


@pytest.mark.parametrize("headers", [{}, {"Authorization": "Basic " + base64.b64encode(b"hook-user:wrong").decode()}])
def test_webhook_without_valid_credentials_is_rejected(client, headers):
    resp = client.post("/onholdintegration", json=PROMPT_EVENT, headers=headers)
    assert resp.status_code == 401
    assert client.on_hold_calls == []


@pytest.mark.parametrize("events", [None, [], [{"key": "UserInterface.Message.Prompt.Display"}]])
def test_malformed_events_do_not_crash(client, events):
    resp = client.post("/onholdintegration", json={**PROMPT_EVENT, "events": events}, headers=AUTH)
    assert resp.status_code == 200


def test_non_json_body_returns_400(client):
    resp = client.post("/onholdintegration", data="not json", content_type="text/plain")
    assert resp.status_code == 400


def test_health_check_with_valid_jwt(client, signing_key):
    resp = client.post("/onholdintegration", json={"jwt": make_jwt(signing_key)})
    assert resp.status_code == 200
    assert resp.get_json()["operationalState"] == "operational"


@pytest.mark.parametrize("claims", [{"appId": "someone-else"}, {"iat": int(time.time()) - 3600}])
def test_invalid_jwt_returns_401(client, signing_key, claims):
    resp = client.post("/onholdintegration", json={"jwt": make_jwt(signing_key, **claims)})
    assert resp.status_code == 401


def test_jwt_signed_with_wrong_key_returns_401(client, signing_key):
    other_key = ec.generate_private_key(ec.SECP256R1())
    resp = client.post("/onholdintegration", json={"jwt": make_jwt(other_key)})
    assert resp.status_code == 401
