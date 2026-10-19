# Workspace-Integration
This integration is similar in functionality to the [On-Hold macro](https://github.com/dhenwood/OnHoldMacro), but done as a Workspace Integration. Documentation on how the Workspace integration works [can be found here](https://developer.webex.com/create/docs/workspace-integrations).

There are 4 files that make up the integration:
1. app.py - this includes the flask container
2. manageTokens.py - manages the OAuth tokens and refreshes the tokens when needed
3. .env - file to store current tokens
4. manifest file - this file is used to upload into Control Hub
