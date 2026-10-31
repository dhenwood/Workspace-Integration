import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Set before the app is imported so tests never touch a real .env or log file.
os.environ.setdefault("LOG_FILE", os.path.join(tempfile.gettempdir(), "onhold-test.log"))
os.environ.update({
    "CLIENT_ID": "client-id",
    "CLIENT_SECRET": "client-secret",
    "APP_ID": "test-app-id",
    "WEBHOOK_USERNAME": "hook-user",
    "WEBHOOK_PASSWORD": "hook-pass",
})
