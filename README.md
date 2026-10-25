# Workspace-Integration
This integration is similar in functionality to the [On-Hold macro](https://github.com/dhenwood/OnHoldMacro), but done as a Workspace Integration. Documentation on how the Workspace integration works [can be found here](https://developer.webex.com/create/docs/workspace-integrations).

There are 5 files that make up the integration:
1. app.py - manages inbound messages including healthCheck JWT and its response
2. webexMsgSend.py - manages sending messages to the device via Control Hub
3. manageTokens.py - manages the OAuth tokens and refreshes the tokens when needed
4. .env - file to store current tokens and duration
5. manifest file - this file is used to create the integration included desired scopes and is uploaded into Control Hub
