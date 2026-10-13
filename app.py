from flask import Flask, request, jsonify, render_template
import logging
import time
import jwt
from jwt import PyJWKClient

# Initialize the Flask application
app = Flask(__name__)

## JWT details - for healthCheck
APP_ID = "<appIdRemoved>" # sent inside the health check JWT and all messsages
JWKS_URLS = {
    "us-west-2_r":    "https://xapi-r.wbx2.com/jwks",
    "us-east-2_a":    "https://xapi-a.wbx2.com/jwks",
    "eu-central-1_k": "https://xapi-k.wbx2.com/jwks",
    "me-central-1_d": "https://xapi-d.wbx2.com/jwks",
}
DEFAULT_JWKS = JWKS_URLS["us-east-2_a"]
_jwk_clients = {} 


@app.route('/onholdintegration', methods=['POST'])
def rxMessage():
    data = request.get_json()
    response = processJson(data)
    return response


def processJson(message):
    if message.get("type") == "events":               # webhook main events
        processEvent(message)
        return jsonify({"status": "ok"}), 200

    if message.get("type") == "healthCheck":          # webhook health check
        return jsonify({"status": "ok"}), 200

    if "jwt" in message:                               # actions (healthCheck, update, deprovision)
        claims = verify_jwt(message["jwt"])            # verify signature + appId
        if claims.get("action") == "healthCheck":
            return jsonify({"operationalState": "operational", "tokensState": "valid"}), 200
        return "", 204

    return jsonify({"status": "ignored"}), 200

def processEvent(event):
    deviceId = event.get("deviceId")
    events = event.get("events")
    event0 = events[0]
    key = event0.get("key")
    if key == "UserInterface.Message.Prompt.Display":
        value = event0.get("value")
        title = value.get("Title")
        # use values to trigger On-Hold process
    elif key == "Bookings.BookingRequested":
        value = event0.get("value")
        title = value.get("Title")
        # use values to cancel On-Hold process

def verify_jwt(token):
    unverified = jwt.decode(token, options={"verify_signature": False})
    url = JWKS_URLS.get(unverified.get("region"), DEFAULT_JWKS)
    client = _jwk_clients.setdefault(url, PyJWKClient(url))

    key = client.get_signing_key_from_jwt(token).key
    claims = jwt.decode(token, key, algorithms=["ES256"],
                        options={"verify_aud": False})

    if claims.get("appId") != APP_ID:
        raise jwt.InvalidTokenError("appId mismatch")
    if claims.get("action") != "provision" and time.time() - claims.get("iat", 0) > 300:
        raise jwt.InvalidTokenError("JWT too old")
    return claims

if __name__ == "__main__":
    app.run(debug=False)
