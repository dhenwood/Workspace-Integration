from flask import Flask, request, jsonify, render_template
import logging, time, jwt, os
from jwt import PyJWKClient
import webexMsgSend

# Initialize the Flask application
app = Flask(__name__)

# JWT details - for healthCheck
JWKS_URLS = {
    "us-west-2_r":    "https://xapi-r.wbx2.com/jwks",
    "us-east-2_a":    "https://xapi-a.wbx2.com/jwks",
    "eu-central-1_k": "https://xapi-k.wbx2.com/jwks",
    "me-central-1_d": "https://xapi-d.wbx2.com/jwks",
}
DEFAULT_JWKS = JWKS_URLS["us-east-2_a"]
_jwk_clients = {} 


@app.route("/")
def index():
    return render_template('index.html')


@app.route('/onholdintegration', methods=['POST'])
def rxMessage():
    data = request.get_json()

    response = processJson(data)
    return response


def processJson(message):
    if message.get("type") == "events":         # webhook main events
        processEvent(message)
        return jsonify({"status": "ok"}), 200

    if "jwt" in message:                               # actions (healthCheck, update, deprovision)
        claims = verify_jwt(message["jwt"])            # verify signature + appId
        if claims.get("action") == "healthCheck":
            logToFile("healthCheck")
            return jsonify({"operationalState": "operational", "tokensState": "valid"}), 200
        return "", 204

    return jsonify({"status": "ignored"}), 200

def processEvent(event):
    logToFile(f"event: {event}")
    deviceId = event.get("deviceId")
    workspaceId = event.get("workspaceId")
    events = event.get("events")
    event0 = events[0]
    key = event0.get("key")
    if key == "UserInterface.Message.Prompt.Display":
        value = event0.get("value")
        title = value.get("Title")
        logToFile(f"deviceId: {deviceId} Display title: {title}")
        if title == "Cisco Spaces Smart Workspaces":
            webexMsgSend.toggleOnHold(deviceId, workspaceId, True)
    elif key == "Bookings.BookingRequested":
        value = event0.get("value")
        title = value.get("Title")
        logToFile(f"deviceId: {deviceId} Booking Requested: {title}")
        webexMsgSend.toggleOnHold(deviceId, workspaceId, False)

def verify_jwt(token):
    unverified = jwt.decode(token, options={"verify_signature": False})
    url = JWKS_URLS.get(unverified.get("region"), DEFAULT_JWKS)
    client = _jwk_clients.setdefault(url, PyJWKClient(url))

    key = client.get_signing_key_from_jwt(token).key
    claims = jwt.decode(token, key, algorithms=["ES256"],
                        options={"verify_aud": False})

    appId = os.environ.get('APP_ID')
    if claims.get("appId") != appId:
        raise jwt.InvalidTokenError("appId mismatch")
    if claims.get("action") != "provision" and time.time() - claims.get("iat", 0) > 300:
        raise jwt.InvalidTokenError("JWT too old")
    return claims

def logToFile(message):
    epoch_seconds = time.time()
    with open("output.txt", "a", encoding="utf-8") as file:
            file.write(f"{epoch_seconds}: {message}\n")

if __name__ == "__main__":
    app.run(debug=False)
