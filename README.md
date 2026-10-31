# Workspace-Integration
This macro updates the Cisco Navigator outside panel to On-Hold (blue) when requested by a user in Cisco Spaces. This includes the background image, workspace avatar, LED strip on the wall mount, and the main text. If no one books the room after 3 minutes or if a user presses "Book Room" from the outside panel, it will return to its default state.

![alt text](https://github.com/dhenwood/OnHoldMacro/blob/main/OnHoldExample.png)

## Options
There are three options for providing this capability. The differences between each is as follows;
1. Macro for paired Navigators. When your Navigator is paired (not standalone) to the codec. Note for **MTR's**, most of the features will work however the ability to change the text to "On-Hold" is not available when paired _and_ in MTR mode. [Github repo here](https://github.com/dhenwood/OnHoldMacro)
2. Macro for Navigators in standalone. In this case, messages between the codec and Navigator are sent via the Webex cloud. For MTR's this option works in full (unlike option 1). [Github repo here](https://github.com/dhenwood/OnHoldMacroMTR)
3. Workspace Integration. This option makes deploying the capability for a large fleet of devices the easiest. It is built on a server and made available for all devices (not requiring deploying the macro to every device).

This repo is for option 3 - supports devices in RoomOS or MTR and paired or standalone Navigators.

## Setup
Documentation on how Workspace integrations works [can be found here](https://developer.webex.com/create/docs/workspace-integrations).

The integration is made up of:
1. app.py - receives webhooks and actions from Webex, checks they are genuine, and responds to healthCheck
2. webex.py - sends the commands that put the outside Navigator on hold (and back) via the Webex API
3. tokens.py - manages the OAuth tokens and refreshes them when needed
4. assets/onhold_background.png - the blue background shown while on hold
5. .env.example - template for the `.env` file that stores your credentials and current tokens
6. manifest.json - used to create the integration (including the scopes it needs) and is uploaded into Control Hub

### Setup Workspace Integration
The manifest.json file contains the details of the integration including the OAuth scopes and permissions. You may wish to change the vendor and email to reflect your own. The [Manifest Editor, found here](https://cisco-ce.github.io/workspace-integrations-editor/) can be used to do this. Save the file to your computer.
In Control Hub under Workspaces -> Integrations, select "Add Integration" then "Upload Integration". Specify the manifest.json file you saved then "Upload".

Once processed, the next page will provide a ClientID and ClientSecret. Copy each of these and 🚨**ensure they are saved securely**🚨 as both cannot be obtained again (the setup process would need to be repeated).
![alt text](https://images.contentstack.io/v3/assets/bltd74e2c7e18c68b20/blt86782cd1f8590aa6/64526bc5fb3d807d46df80e7/client-id-secret.png)

Once done, you should be on the On-Hold Workspace Integration page. Select the "Actions" button and "Activate". An activation code will be provided. Copy this to clipboard. 
![alt text](https://images.contentstack.io/v3/assets/bltd74e2c7e18c68b20/blt71d25a6f2b6ddfe6/64526bc526dc891182facd4a/activation-code.png)

This is a base64 encoded JWT. Online tools such as [jwt.io](https://www.jwt.io/) can be used to decode this, but given it contains your refresh token, you may prefer to do this locally on your computer (MacOS and Windows have tools to do this). The base64 decoded payload should look somthing like the following:
```json
{
  "sub": "Y2lzY29zcGFyazovL3VybjpURUFNOnVzLWVhc3QtMl9hL09SR0FOSVpBVElPTi80NTkwZWI2YS0yY2EyLTQzOTQtYmMyNy05YjY3MWNlMmZlNzM=",
  "oauthUrl": "https://webexapis.com/v1/access_token",
  "orgName": "CVTG labs",
  "appUrl": "https://xapi-a.wbx2.com/xapi/api/organizations/4590eb6a-2ca2-4394-bc27-9b671ce2fe73/apps/ac6b6972-538e-11ec-bf63-0242ac130003",
  "userId": "Y2lzY29zcGFyazovL3VybjpURUFNOnVzLWVhc3QtMl9hL1BFT1BMRS8xYzdmMDQ2YS1jOWRiLTQyZWQtOTFkYi1jNmY4NDVkMWYxNmU=",
  "manifestUrl": "https://xapi-a.wbx2.com/xapi/api/organizations/4590eb6a-2ca2-4394-bc27-9b671ce2fe73/appManifests/ac6b6972-538e-11ec-bf63-0242ac130003",
  "appId": "ac6b6972-538e-11ec-bf63-0242ac130003",
  "expiryTime": "2023-08-10T08:02:33.816114574Z",
  "action": "provision",
  "webexapisBaseUrl": "https://webexapis.com/v1",
  "scopes": "spark-admin:devices_read,spark:xapi_statuses,spark-admin:workspaces_read,spark:xapi_commands",
  "region": "us-east-2_a",
  "iat": 1691568153,
  "jti": "KqBo61g8SzmjcMP3CEYDPA==",
  "refreshToken": "<yourRefreshToken>",
  "xapiAccess": "{\"commands\":[\"Message.Send\"],\"statuses\":[\"RoomAnalytics.*\",\"Peripherals.ConnectedDevice[*].RoomAnalytics.*\",\"SystemUnit.State.NumberOfActiveCalls\",\"Standby.State\"],\"events\":[\"UserInterface.Message.Prompt.Response\",\"BootEvent\"]}"
}
```

The following three items need to be saved
* oauthUrl
* appUrl
* refreshToken

Using [Postman](https://www.postman.com/) or equivalant, construct the following message:
```http
POST {oauthUrl_ObtainedInPreviousStep}
Content-Type: application/json

{
  "grant_type": "refresh_token",
  "client_id": "{clientId_ObtainedEarlier}",
  "client_secret": "{clientSecret_ObtainedEarlier}",
  "refresh_token": "{refreshToken_ObtainedInPreviousStep}"
}
```

The response will include a number of values, copy the **access_token**. Using Postman again, construct the following message. Note, you will need to specify **your** server URL (and directory) for which messages will be sent to.

Choose a username and a strong password for the webhook below. Webex sends them with every event, and the server rejects any event that doesn't include them, so nobody else can trigger the integration. You'll add the same values to the `.env` file later. More details on how messages are secured can be [found here](https://developer.webex.com/create/docs/workspace-integration-technical-details#activation).

```http
PATCH {appUrl_ObtainedInPreviousStep}
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "provisioningState": "completed",
  "actionsUrl": "{yourWebServer.com/onholdintegration}",
  "webhook": {
    "targetUrl": "{yourWebServer.com/onholdintegration}",
    "type": "basic_authentication",
    "username": "{userName}",
    "password": "{password}"
  }
}
```

Once processed, the Control Hub Workspace Integration for On-Hold should appear **Active**

### Server Details
1. Copy the repo to your web server and install the dependencies (Python 3.9 or later):
   ```bash
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and fill in the following fields. **Note**, the AppId can be found in the manifest.json file:
   1. CLIENT_ID
   2. CLIENT_SECRET
   3. REFRESH_TOKEN
   4. APP_ID
   5. WEBHOOK_USERNAME and WEBHOOK_PASSWORD - the same values used in the PATCH above
   6. WEBHOOK_PATH (optional) - only if you used a path other than `/onholdintegration` in the PATCH above
3. Keep `.env` private - it holds your secrets and is listed in `.gitignore` so it won't be committed.
4. Run the app with a production server such as gunicorn, behind HTTPS:
   ```bash
   gunicorn --bind 0.0.0.0:8000 app:app
   ```
   (`flask run` works for local testing, but it's a development server and shouldn't be exposed to the internet.)

Logs are written to `output.txt` (change with `LOG_FILE` in `.env`).

### Running the tests
```bash
pip install -r requirements-dev.txt
pytest
```
