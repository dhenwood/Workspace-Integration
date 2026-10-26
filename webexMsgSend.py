import time
import requests, json
import manageTokens

def toggleOnHold(deviceId, onHoldState):
    if onHoldState:
        setLedControl = xConfig(deviceId, "Manual")
        if setLedControl == 200:
            ledControlBody = constructLedControlBody()
            xCommand(deviceId, "UserInterface.LedControl.Color.Set", ledControlBody)
            translationBody = constructTranslationBody()
            xCommand(deviceId, "UserInterface.Translation.Override.Set", translationBody)
            background = constructBackground()
            xCommand(deviceId, "UserInterface.Branding.Upload", background)
    else:
        setLedControl = xConfig(deviceId, "Auto")
        if setLedControl == 200:
            xCommand(deviceId, "UserInterface.Translation.Override.Clear", "")
            backgroundDelete = constructDeleteBackground()
            xCommand(deviceId, "UserInterface.Branding.Delete", backgroundDelete)

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
        "value": value
    }
    ]
    resp = requests.patch(url, headers=headers, json=payload)
    logToFile(f"respCode0: {resp.status_code}")
    return resp.status_code


def xCommand(deviceId, urlParameter, msgBody):
    try:
        url = f"https://webexapis.com/v1/xapi/command/{urlParameter}"
        logToFile(f"xCommand Url: {url}")
        token = manageTokens.getToken()
        headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        }
        logToFile(f"msgBody: {msgBody}")
        if msgBody == "":
            payload = {"deviceId": deviceId}
        else:
            payload = {"deviceId": deviceId, **msgBody}
        logToFile(f"payload: {payload}")
        resp = requests.post(url, headers=headers, json=payload)
        logToFile(f"respCode: {resp.status_code}, msg: {resp.json()}")
    except Exception as e:
        logToFile(f"xCommand failed: {e!r}")
        raise

def constructLedControlBody():
    body = {
        "arguments": {
            "Color": "Blue"
        }
    }
    return body

def constructTranslationBody():
    body = {
        "body": {"version": 1, "translations": [{"sourceText": "Available", "translated": "On Hold", "language"
: "English"}]}
    }
    return body

def constructBackground():
    blueBackground = "iVBORw0KGgoAAAANSUhEUgAAAMgAAABkCAYAAADDhn8LAAAKMWlDQ1BJQ0MgcHJvZmlsZQAASImdlndUU9kWh8+9N
71QkhCKlNBraFICSA29SJEuKjEJEErAkAAiNkRUcERRkaYIMijggKNDkbEiioUBUbHrBBlE1HFwFBuWSWStGd+8ee/Nm98f935rn73P3Wfvfda6
AJD8gwXCTFgJgAyhWBTh58WIjYtnYAcBDPAAA2wA4HCzs0IW+EYCmQJ82IxsmRP4F726DiD5+yrTP4zBAP+flLlZIjEAUJiM5/L42VwZF8k4PVe
cJbdPyZi2NE3OMErOIlmCMlaTc/IsW3z2mWUPOfMyhDwZy3PO4mXw5Nwn4405Er6MkWAZF+cI+LkyviZjg3RJhkDGb+SxGXxONgAoktwu5nNTZG
wtY5IoMoIt43kA4EjJX/DSL1jMzxPLD8XOzFouEiSniBkmXFOGjZMTi+HPz03ni8XMMA43jSPiMdiZGVkc4XIAZs/8WRR5bRmyIjvYODk4MG0tb
b4o1H9d/JuS93aWXoR/7hlEH/jD9ld+mQ0AsKZltdn6h21pFQBd6wFQu/2HzWAvAIqyvnUOfXEeunxeUsTiLGcrq9zcXEsBn2spL+jv+p8Of0Nf
fM9Svt3v5WF485M4knQxQ143bmZ6pkTEyM7icPkM5p+H+B8H/nUeFhH8JL6IL5RFRMumTCBMlrVbyBOIBZlChkD4n5r4D8P+pNm5lona+BHQllg
CpSEaQH4eACgqESAJe2Qr0O99C8ZHA/nNi9GZmJ37z4L+fVe4TP7IFiR/jmNHRDK4ElHO7Jr8WgI0IABFQAPqQBvoAxPABLbAEbgAD+ADAkEoiA
RxYDHgghSQAUQgFxSAtaAYlIKtYCeoBnWgETSDNnAYdIFj4DQ4By6By2AE3AFSMA6egCnwCsxAEISFyBAVUod0IEPIHLKFWJAb5AMFQxFQHJQIJ
UNCSAIVQOugUqgcqobqoWboW+godBq6AA1Dt6BRaBL6FXoHIzAJpsFasBFsBbNgTzgIjoQXwcnwMjgfLoK3wJVwA3wQ7oRPw5fgEVgKP4GnEYAQ
ETqiizARFsJGQpF4JAkRIauQEqQCaUDakB6kH7mKSJGnyFsUBkVFMVBMlAvKHxWF4qKWoVahNqOqUQdQnag+1FXUKGoK9RFNRmuizdHO6AB0LDo
ZnYsuRlegm9Ad6LPoEfQ4+hUGg6FjjDGOGH9MHCYVswKzGbMb0445hRnGjGGmsVisOtYc64oNxXKwYmwxtgp7EHsSewU7jn2DI+J0cLY4X1w8To
grxFXgWnAncFdwE7gZvBLeEO+MD8Xz8MvxZfhGfA9+CD+OnyEoE4wJroRIQiphLaGS0EY4S7hLeEEkEvWITsRwooC4hlhJPEQ8TxwlviVRSGYkN
imBJCFtIe0nnSLdIr0gk8lGZA9yPFlM3kJuJp8h3ye/UaAqWCoEKPAUVivUKHQqXFF4pohXNFT0VFysmK9YoXhEcUjxqRJeyUiJrcRRWqVUo3RU
6YbStDJV2UY5VDlDebNyi/IF5UcULMWI4kPhUYoo+yhnKGNUhKpPZVO51HXURupZ6jgNQzOmBdBSaaW0b2iDtCkVioqdSrRKnkqNynEVKR2hG9E
D6On0Mvph+nX6O1UtVU9Vvuom1TbVK6qv1eaoeajx1UrU2tVG1N6pM9R91NPUt6l3qd/TQGmYaYRr5Grs0Tir8XQObY7LHO6ckjmH59zWhDXNNC
M0V2ju0xzQnNbS1vLTytKq0jqj9VSbru2hnaq9Q/uE9qQOVcdNR6CzQ+ekzmOGCsOTkc6oZPQxpnQ1df11Jbr1uoO6M3rGelF6hXrtevf0Cfos/
ST9Hfq9+lMGOgYhBgUGrQa3DfGGLMMUw12G/YavjYyNYow2GHUZPTJWMw4wzjduNb5rQjZxN1lm0mByzRRjyjJNM91tetkMNrM3SzGrMRsyh80d
zAXmu82HLdAWThZCiwaLG0wS05OZw2xljlrSLYMtCy27LJ9ZGVjFW22z6rf6aG1vnW7daH3HhmITaFNo02Pzq62ZLde2xvbaXPJc37mr53bPfW5
nbse322N3055qH2K/wb7X/oODo4PIoc1h0tHAMdGx1vEGi8YKY21mnXdCO3k5rXY65vTW2cFZ7HzY+RcXpkuaS4vLo3nG8/jzGueNueq5clzrXa
VuDLdEt71uUnddd457g/sDD30PnkeTx4SnqWeq50HPZ17WXiKvDq/XbGf2SvYpb8Tbz7vEe9CH4hPlU+1z31fPN9m31XfKz95vhd8pf7R/kP82/
xsBWgHcgOaAqUDHwJWBfUGkoAVB1UEPgs2CRcE9IXBIYMj2kLvzDecL53eFgtCA0O2h98KMw5aFfR+OCQ8Lrwl/GGETURDRv4C6YMmClgWvIr0i
yyLvRJlESaJ6oxWjE6Kbo1/HeMeUx0hjrWJXxl6K04gTxHXHY+Oj45vipxf6LNy5cDzBPqE44foi40V5iy4s1licvvj4EsUlnCVHEtGJMYktie8
5oZwGzvTSgKW1S6e4bO4u7hOeB28Hb5Lvyi/nTyS5JpUnPUp2Td6ePJninlKR8lTAFlQLnqf6p9alvk4LTduf9ik9Jr09A5eRmHFUSBGmCfsytT
PzMoezzLOKs6TLnJftXDYlChI1ZUPZi7K7xTTZz9SAxESyXjKa45ZTk/MmNzr3SJ5ynjBvYLnZ8k3LJ/J9879egVrBXdFboFuwtmB0pefK+lXQq
qWrelfrry5aPb7Gb82BtYS1aWt/KLQuLC98uS5mXU+RVtGaorH1futbixWKRcU3NrhsqNuI2ijYOLhp7qaqTR9LeCUXS61LK0rfb+ZuvviVzVeV
X33akrRlsMyhbM9WzFbh1uvb3LcdKFcuzy8f2x6yvXMHY0fJjpc7l+y8UGFXUbeLsEuyS1oZXNldZVC1tep9dUr1SI1XTXutZu2m2te7ebuv7PH
Y01anVVda926vYO/Ner/6zgajhop9mH05+x42Rjf2f836urlJo6m06cN+4X7pgYgDfc2Ozc0tmi1lrXCrpHXyYMLBy994f9Pdxmyrb6e3lx4Chy
SHHn+b+O31w0GHe4+wjrR9Z/hdbQe1o6QT6lzeOdWV0iXtjusePhp4tLfHpafje8vv9x/TPVZzXOV42QnCiaITn07mn5w+lXXq6enk02O9S3rvn
Ik9c60vvG/wbNDZ8+d8z53p9+w/ed71/LELzheOXmRd7LrkcKlzwH6g4wf7HzoGHQY7hxyHui87Xe4Znjd84or7ldNXva+euxZw7dLI/JHh61HX
b95IuCG9ybv56Fb6ree3c27P3FlzF3235J7SvYr7mvcbfjT9sV3qID0+6j068GDBgztj3LEnP2X/9H686CH5YcWEzkTzI9tHxyZ9Jy8/Xvh4/En
Wk5mnxT8r/1z7zOTZd794/DIwFTs1/lz0/NOvm1+ov9j/0u5l73TY9P1XGa9mXpe8UX9z4C3rbf+7mHcTM7nvse8rP5h+6PkY9PHup4xPn34D94
Tz+3EBhusAAAAJcEhZcwAALiMAAC4jAXilP3YAAAAHdElNRQfpBggCCyaFFrX9AAAAGXRFWHRDb21tZW50AENyZWF0ZWQgd2l0aCBHSU1QV4EOF
wAAAkJJREFUeNrt0ztv1EAUgNF7o0QoEkpPjcSf4f93iDaiQqJIxENAsbvzsK/tXWjPKTK7XnvGGfvLdx8+fnrMp/eREXH6E5F9PH3KaL9nRI7f
25Dny8bfsk01fOhzVGtlluf3MSKnc7auX9zTaq0+3+V4rtYqxtX6w/XFPefGPNV93TJvNfZndbCnbf93nuuwN9O82XZq+t7On+Y4WH94Tw7Xn/b
gtnnLfVq+Q8U7+e3L57h/iMd4c/e2fvHGBTM3HvzwMHLvAY3zXL9WLjb8urX6HJk7m5Hzg6/Wqu6z/L+WMYzrb817xVq52Le9ectjyz35r/0v5t
2N4dr9v+zfxrHif9hc65/2v17r14/XuAtgk0BAICAQEAgIBAQCAgGBgEBAIIBAQCAgEBAICAQEAgIBgYBAQCCAQEAgIBAQCAgEBAICAYGAQACBg
EBAICAQEAgIBAQCAgGBgEAAgYBAQCAgEBAICAQEAgIBgQACAYGAQEAgIBAQCAgEBAICAYEAAgGBgEBAICAQEAgIBAQCAgEEAgIBgYBAQCAgEBAI
CAQEAgIBBAICAYGAQEAgIBAQCAgEBAIIBAQCAgGBgEBAICAQEAgIBAQCjO5/xmt8//0QkRHxJ09Hs4+nT3n6/Tzm+L0Neb5s/C3bVMOHPke1VmZ
5fh8jcjpn6/rFPa3W6vNdjudqrWJcrT9cX9xzbsxT3dct81Zjf1YHe9r2f+e5DnszzZttp6bv7fxpjoP1h/fkcP1pD26bt9yn5TtUvJMvX5/jL6
nzEqSQpBvfAAAAAElFTkSuQmCC"
    body = {
        "arguments": {
            "Type": "SchedulerBackground"
        },"body": blueBackground
    }
    return body

def constructDeleteBackground():
    body = {
        "arguments": {
            "Type": "SchedulerBackground"
        }
    }
    return body

def logToFile(message):
    epoch_seconds = time.time()
    with open("output.txt", "a", encoding="utf-8") as file:
            file.write(f"{epoch_seconds}: {message}\n")
