# Workspace-Integration
This macro updates the Cisco Navigator outside panel to On-Hold (blue) when requested by a user in Cisco Spaces. This includes the background image, workspace avatar, LED strip on the wall mount, and the main text. If no one books the room after 3 minutes or if a user presses "Book Room" from the outside panel, it will return to its default state.

![alt text](https://github.com/dhenwood/OnHoldMacro/blob/main/OnHoldExample.png)

## Options
There are three options for providing this capability. The differences between each is as follows;
1. Macro for paired Navigators. When your Navigator is paired (not standalone) to the codec. Note for **MTR's**, most of the features will work however the ability to change the text to "On-Hold" is not available when paired _and_ in MTR mode. [Github repo here](https://github.com/dhenwood/OnHoldMacro)
2. Macro for Navigators in standalone. In this case, messages between the codec and Navigator are sent via the Webex cloud. For MTR's this option works in full (unlike option 1).
3. Workspace Integration. This option makes deploying the capability for a large fleet of devices the easiest. It is built on a server and made available for all devices (not requiring deploying the macro to every device). [Github repo here](https://github.com/dhenwood/Workspace-Integration)

This repo is for option 3 - devices in RoomOS or MTR and irrespective of paired or standalone Navigator.

## Setup
Documentation on how Workspace integrations works [can be found here](https://developer.webex.com/create/docs/workspace-integrations).

There are 5 files that make up the integration:
1. app.py - manages inbound messages including healthCheck JWT and its response
2. webexMsgSend.py - manages sending messages to the device via Control Hub
3. manageTokens.py - manages the OAuth tokens and refreshes the tokens when needed
4. .env - file to store current tokens and duration
5. manifest file - this file is used to create the integration included desired scopes and is uploaded into Control Hub
