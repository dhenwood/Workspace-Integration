import time
import requests, json
import manageTokens

def toggleOnHold(deviceId, onHoldState):
    if onHoldState:
        setLedControl = xConfig(deviceId, "Manual")
        if setLedControl == 200:
            logToFile("onHoldActivate: now into commands")
    else:
        setLedControl = xConfig(deviceId, "Auto")
        if setLedControl == 200:
            logToFile("offHold: now into commands")

def xConfig(deviceId, value):
    logToFile(f"toggleOnHold: {value} of device {deviceId}")
    token = manageTokens.getToken()
    url = f"https://webexapis.com/v1/deviceConfigurations?deviceId={deviceId}"
    headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json-patch+json",
    }
    payload = [
    {
        "op": "replace",
        "path": "UserInterface.LedControl.Mode/sources/configured/value",
        "value": value,
    }
    ]
    resp = requests.patch(url, headers=headers, json=payload)
    return resp.status_code


def xCommand(deviceId):
    logToFile(f"xCommand ")

def logToFile(message):
    epoch_seconds = time.time()
    with open("output.txt", "a", encoding="utf-8") as file:
            file.write(f"{epoch_seconds}: {message}\n")
