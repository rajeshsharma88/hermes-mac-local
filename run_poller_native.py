import os
import sys
import json
import subprocess

# Read TELEGRAM_BOT_TOKEN from .env
env_path = r"C:\Users\Aarogya\AppData\Local\hermes\.env"
token = None
with open(env_path, "r") as f:
    for line in f:
        if line.startswith("TELEGRAM_BOT_TOKEN="):
            token = line.strip().split("=", 1)[1]
            break

if not token:
    print("ERROR: TELEGRAM_BOT_TOKEN not found in .env", file=sys.stderr)
    sys.exit(1)

print(f"Token loaded (length: {len(token)})")

# Set environment variables
os.environ["TELEGRAM_BOT_TOKEN"] = token
os.environ["VAULT_PATH"] = r"C:\Users\Aarogya\Documents\rajesh-sharma-os"
os.environ["STATE_DIR"] = r"C:\Users\Aarogya\AppData\Local\hermes\state"

# Run the poller script
script_path = r"C:\Users\Aarogya\AppData\Local\hermes\scripts\telegram_inbox_poller.py"
result = subprocess.run(
    [sys.executable, script_path],
    capture_output=True,
    text=True,
    timeout=120
)

print("STDOUT:")
print(result.stdout)
if result.stderr:
    print("STDERR:")
    print(result.stderr)
print(f"Exit code: {result.returncode}")
