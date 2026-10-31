"""Webex API calls that put a workspace's outside Navigator on hold and back again."""
import base64
import logging
import time
from pathlib import Path

import requests

from tokens import get_token

API_BASE = "https://webexapis.com/v1"
REQUEST_TIMEOUT = 15
# After switching the LED to Manual mode the device needs a moment before it accepts a colour.
LED_SETTLE_SECONDS = 5

NAVIGATOR_PRODUCT = "Cisco Room Navigator"
OUTSIDE_ROOM = "OutsideRoom"

_BACKGROUND_FILE = Path(__file__).parent / "assets" / "onhold_background.png"
BACKGROUND_PNG_BASE64 = base64.b64encode(_BACKGROUND_FILE.read_bytes()).decode("ascii")

LED_BLUE = {"arguments": {"Color": "Blue"}}
ON_HOLD_TEXT = {
    "body": {
        "version": 1,
        "translations": [{"sourceText": "Available", "translated": "On Hold", "language": "English"}],
    }
}
SCHEDULER_BACKGROUND = {"arguments": {"Type": "SchedulerBackground"}}
ON_HOLD_BACKGROUND = {**SCHEDULER_BACKGROUND, "body": BACKGROUND_PNG_BASE64}

log = logging.getLogger(__name__)
_session = requests.Session()


def webex_request(method, path, **kwargs):
    """Call the Webex API with auth and a timeout; raise on any non-2xx response."""
    headers = {"Authorization": f"Bearer {get_token()}", **kwargs.pop("headers", {})}
    resp = _session.request(method, f"{API_BASE}/{path}", headers=headers, timeout=REQUEST_TIMEOUT, **kwargs)
    if not resp.ok:
        log.error("%s %s failed: %s %s", method, path, resp.status_code, resp.text[:500])
    resp.raise_for_status()
    return resp.json() if resp.content else None


def x_command(device_id, command, body=None):
    webex_request("POST", f"xapi/command/{command}", json={"deviceId": device_id, **(body or {})})


def set_led_mode(device_id, mode):
    webex_request(
        "PATCH",
        "deviceConfigurations",
        params={"deviceId": device_id},
        headers={"Content-Type": "application/json-patch+json"},
        json=[{"op": "replace", "path": "UserInterface.LedControl.Mode/sources/configured/value", "value": mode}],
    )


def set_on_hold(device_id, workspace_id, on_hold):
    """Turn the On Hold look on or off for the workspace's outside Navigator."""
    target = find_outside_navigator(workspace_id) or device_id
    log.info("Setting on hold=%s for device %s", on_hold, target)

    if on_hold:
        set_led_mode(target, "Manual")  # if this fails, stop here
        led_mode_set_at = time.monotonic()
        _send_commands(target, [
            ("UserInterface.Translation.Override.Set", ON_HOLD_TEXT),
            ("UserInterface.Branding.Upload", ON_HOLD_BACKGROUND),
        ])
        time.sleep(max(0.0, LED_SETTLE_SECONDS - (time.monotonic() - led_mode_set_at)))
        _send_commands(target, [("UserInterface.LedControl.Color.Set", LED_BLUE)])
    else:
        set_led_mode(target, "Auto")
        _send_commands(target, [
            ("UserInterface.Translation.Override.Clear", None),
            ("UserInterface.Branding.Delete", SCHEDULER_BACKGROUND),
        ])


def _send_commands(device_id, commands):
    """Send each command; one failing doesn't stop the rest."""
    for command, body in commands:
        try:
            x_command(device_id, command, body)
        except requests.RequestException:
            log.exception("%s failed on device %s", command, device_id)


def find_outside_navigator(workspace_id):
    """Return the id of a standalone Navigator mounted outside the room, or None."""
    try:
        workspace = webex_request("GET", f"workspaces/{workspace_id}", params={"includeDevices": "true"})
    except requests.RequestException:
        log.warning("Could not list devices for workspace %s; using the device that sent the event", workspace_id)
        return None

    for device in (workspace or {}).get("devices", []):
        if device.get("product") == NAVIGATOR_PRODUCT and is_outside_room(device["id"]):
            return device["id"]
    return None


def is_outside_room(device_id):
    try:
        status = webex_request(
            "GET", "xapi/status", params={"deviceId": device_id, "name": "SystemUnit.TouchPanel.Location"}
        )
        return status["result"]["SystemUnit"]["TouchPanel"]["Location"] == OUTSIDE_ROOM
    except (requests.RequestException, ValueError, KeyError, TypeError) as e:
        log.warning("Could not read the location of Navigator %s: %s", device_id, e)
        return False
