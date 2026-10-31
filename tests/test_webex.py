import requests

import webex


def record_calls(monkeypatch, workspace_devices=(), navigator_location="OutsideRoom", fail_command=None):
    calls = []

    def fake_request(method, path, **kwargs):
        calls.append((method, path))
        if path.startswith("workspaces/"):
            return {"devices": list(workspace_devices)}
        if path == "xapi/status":
            return {"result": {"SystemUnit": {"TouchPanel": {"Location": navigator_location}}}}
        if fail_command and path.endswith(fail_command):
            raise requests.HTTPError("boom")
        return None

    monkeypatch.setattr(webex, "webex_request", fake_request)
    monkeypatch.setattr(webex.time, "sleep", lambda seconds: None)
    return calls


def commands(calls):
    return [path.removeprefix("xapi/command/") for method, path in calls if method in ("POST", "PATCH")]


def test_on_hold_sets_led_text_background_then_colour(monkeypatch):
    calls = record_calls(monkeypatch)
    webex.set_on_hold("dev-1", "ws-1", True)
    assert commands(calls) == [
        "deviceConfigurations",
        "UserInterface.Translation.Override.Set",
        "UserInterface.Branding.Upload",
        "UserInterface.LedControl.Color.Set",
    ]


def test_off_hold_resets_everything(monkeypatch):
    calls = record_calls(monkeypatch)
    webex.set_on_hold("dev-1", "ws-1", False)
    assert commands(calls) == [
        "deviceConfigurations",
        "UserInterface.Translation.Override.Clear",
        "UserInterface.Branding.Delete",
    ]


def test_outside_navigator_is_used_when_present(monkeypatch):
    nav = {"id": "nav-1", "product": "Cisco Room Navigator"}
    record_calls(monkeypatch, workspace_devices=[nav])
    assert webex.find_outside_navigator("ws-1") == "nav-1"


def test_inside_navigator_is_not_used(monkeypatch):
    nav = {"id": "nav-1", "product": "Cisco Room Navigator"}
    record_calls(monkeypatch, workspace_devices=[nav], navigator_location="InsideRoom")
    assert webex.find_outside_navigator("ws-1") is None


def test_one_failed_command_does_not_stop_the_rest(monkeypatch):
    calls = record_calls(monkeypatch, fail_command="Translation.Override.Clear")
    webex.set_on_hold("dev-1", "ws-1", False)
    assert "UserInterface.Branding.Delete" in commands(calls)
