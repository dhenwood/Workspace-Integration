"""Flask app that receives Workspace Integration webhooks and actions from Webex."""
import hmac
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import jwt
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from jwt import PyJWKClient

load_dotenv(Path(__file__).with_name(".env"))

import webex  # noqa: E402  (needs .env loaded first)

logging.basicConfig(
    filename=os.environ.get("LOG_FILE", "output.txt"),
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger("app")

WEBHOOK_PATH = os.environ.get("WEBHOOK_PATH", "/onholdintegration")

EVENT_PROMPT_DISPLAY = "UserInterface.Message.Prompt.Display"
EVENT_BOOKING_REQUESTED = "Bookings.BookingRequested"
SPACES_PROMPT_TITLE = "Cisco Spaces Smart Workspaces"

# Keys used to verify the JWTs Webex signs its actions (healthCheck, update, deprovision) with.
JWKS_URLS = {
    "us-west-2_r": "https://xapi-r.wbx2.com/jwks",
    "us-east-2_a": "https://xapi-a.wbx2.com/jwks",
    "eu-central-1_k": "https://xapi-k.wbx2.com/jwks",
    "me-central-1_d": "https://xapi-d.wbx2.com/jwks",
}
DEFAULT_JWKS = JWKS_URLS["us-east-2_a"]
MAX_JWT_AGE_SECONDS = 300
_jwk_clients = {}

# Webex expects a quick reply, so events are handled in the background.
# One worker means two events for the same room never run at the same time.
_worker = ThreadPoolExecutor(max_workers=1)

app = Flask(__name__)


@app.get("/")
def index():
    return "On Hold Workspace Integration is running.\n"


@app.post(WEBHOOK_PATH)
def receive():
    message = request.get_json(silent=True)
    if not isinstance(message, dict):
        return jsonify({"error": "expected a JSON object"}), 400

    if message.get("type") == "events":
        if not basic_auth_ok():
            log.warning("Rejected webhook with missing or wrong credentials")
            return jsonify({"error": "unauthorized"}), 401
        _worker.submit(_log_errors, handle_events, message)
        return jsonify({"status": "ok"}), 200

    if "jwt" in message:
        try:
            claims = verify_jwt(message["jwt"])
        except jwt.PyJWTError as e:
            log.warning("Rejected action JWT: %s", e)
            return jsonify({"error": "invalid token"}), 401
        if claims.get("action") == "healthCheck":
            log.info("healthCheck")
            return jsonify({"operationalState": "operational", "tokensState": "valid"}), 200
        return "", 204

    return jsonify({"status": "ignored"}), 200


def handle_events(message):
    device_id = message.get("deviceId")
    workspace_id = message.get("workspaceId")
    log.info("Event: %s", message)

    for event in message.get("events") or []:
        key = event.get("key")
        value = event.get("value")
        title = value.get("Title") if isinstance(value, dict) else None

        if key == EVENT_PROMPT_DISPLAY:
            log.info("Device %s displayed prompt %r", device_id, title)
            if title == SPACES_PROMPT_TITLE:
                webex.set_on_hold(device_id, workspace_id, True)
        elif key == EVENT_BOOKING_REQUESTED:
            log.info("Device %s booking requested: %r", device_id, title)
            webex.set_on_hold(device_id, workspace_id, False)


def _log_errors(func, *args):
    try:
        func(*args)
    except Exception:
        log.exception("%s failed", func.__name__)


def basic_auth_ok():
    """Check the username/password Webex sends with each webhook (set in the provisioning PATCH)."""
    expected_user = os.environ.get("WEBHOOK_USERNAME")
    expected_password = os.environ.get("WEBHOOK_PASSWORD")
    if not expected_user or not expected_password:
        log.error("WEBHOOK_USERNAME and WEBHOOK_PASSWORD must be set in .env")
        return False

    auth = request.authorization
    if auth is None:
        return False
    user_ok = hmac.compare_digest((auth.username or "").encode(), expected_user.encode())
    password_ok = hmac.compare_digest((auth.password or "").encode(), expected_password.encode())
    return user_ok and password_ok


def verify_jwt(token):
    """Verify an action JWT's signature, appId and age. Raises jwt.PyJWTError if invalid."""
    # The region is only used to pick which allow-listed key server to fetch keys from.
    unverified = jwt.decode(token, options={"verify_signature": False})
    url = JWKS_URLS.get(unverified.get("region"), DEFAULT_JWKS)
    if url not in _jwk_clients:
        _jwk_clients[url] = PyJWKClient(url)

    key = _jwk_clients[url].get_signing_key_from_jwt(token).key
    claims = jwt.decode(token, key, algorithms=["ES256"], options={"verify_aud": False})

    if claims.get("appId") != os.environ.get("APP_ID"):
        raise jwt.InvalidTokenError("appId mismatch")
    if claims.get("action") != "provision" and time.time() - claims.get("iat", 0) > MAX_JWT_AGE_SECONDS:
        raise jwt.InvalidTokenError("JWT too old")
    return claims


if __name__ == "__main__":
    app.run(debug=False)
