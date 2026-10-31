import time
import requests
import os
import json
from dotenv import load_dotenv, set_key

load_dotenv()

def getToken():
    accessToken = os.environ.get('ACCESS_TOKEN')
    accessTokenExpiresAt = int(os.environ.get('ACCESS_TOKEN_EXPIRES_AT'))
    timeNow = int(time.time())
    if timeNow < accessTokenExpiresAt:
        return accessToken
    else:
        newToken = refreshAccessToken()
        return newToken

def refreshAccessToken():
    logToFile("perform refreshAccessToken")
    clientId = os.environ.get('CLIENT_ID')
    clientSecret = os.environ.get('CLIENT_SECRET')
    refreshToken = os.environ.get('REFRESH_TOKEN')

    url = "https://webexapis.com/v1/access_token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refreshToken,
        "client_id": clientId,
        "client_secret": clientSecret,
    }
    
    try:
        response = requests.post(url, data=data, timeout=30)
        response.raise_for_status() # raise exception if not 200-299 response
        tokens = response.json()
        accessToken = tokens["access_token"]
        expiresIn = tokens["expires_in"]
        refreshToken = tokens["refresh_token"]
        refreshTokenExpiresIn = tokens["refresh_token_expires_in"]
        updateEnv(accessToken, expiresIn, refreshToken, refreshTokenExpiresIn)
        return accessToken
    except Exception as e:
        logToFile(f"refreshAccessToken failed: {e!r}")
        raise

def updateEnv(accessToken, expiresIn, refreshToken, refreshTokenExpiresIn):
    #open .env and write updated values
    timeNow = int(time.time())
    expiresAt = timeNow + expiresIn
    refreshExpiresAt = timeNow + refreshTokenExpiresIn
    dotenv_path = '.env'
    set_key(dotenv_path, "ACCESS_TOKEN", accessToken)
    set_key(dotenv_path, "ACCESS_TOKEN_EXPIRES_AT", str(expiresAt))
    set_key(dotenv_path, "REFRESH_TOKEN", refreshToken)
    set_key(dotenv_path, "REFRESH_TOKEN_EXPIRES_AT", str(refreshExpiresAt))
    load_dotenv(dotenv_path)

def logToFile(message):
    epoch_seconds = time.time()
    with open("output.txt", "a", encoding="utf-8") as file:
            file.write(f"{epoch_seconds}: {message}\n")
