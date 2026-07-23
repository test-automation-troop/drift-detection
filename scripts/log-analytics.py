import os
import json
import base64
import hashlib
import hmac
import requests
from datetime import datetime, timezone

workspace_id = os.getenv("LOG_ANALYTICS_WORKSPACE_ID")
shared_key = os.getenv("LOG_ANALYTICS_SHARED_KEY")

if not workspace_id:
    raise Exception("LOG_ANALYTICS_WORKSPACE_ID not found")

if not shared_key:
    raise Exception("LOG_ANALYTICS_SHARED_KEY not found")

payload_file = os.path.join(
    os.getenv("GITHUB_WORKSPACE", "."),
    "reports",
    "drift_payload.json"
)

with open(payload_file, "r", encoding="utf-8") as f:
    payload = json.load(f)

body = json.dumps(payload)
body_bytes = body.encode("utf-8")

rfc1123date = datetime.now(timezone.utc).strftime(
    "%a, %d %b %Y %H:%M:%S GMT"
)

string_to_hash = (
    f"POST\n"
    f"{len(body_bytes)}\n"
    f"application/json\n"
    f"x-ms-date:{rfc1123date}\n"
    f"/api/logs"
)

decoded_key = base64.b64decode(shared_key)

signature = base64.b64encode(
    hmac.new(
        decoded_key,
        string_to_hash.encode("utf-8"),
        hashlib.sha256
    ).digest()
).decode()

headers = {
    "Content-Type": "application/json",
    "Authorization": f"SharedKey {workspace_id}:{signature}",
    "Log-Type": "TerraformDrift",
    "x-ms-date": rfc1123date
}

uri = (
    f"https://{workspace_id}.ods.opinsights.azure.com"
    "/api/logs?api-version=2016-04-01"
)

response = requests.post(
    uri,
    data=body_bytes,
    headers=headers
)

print(f"Status Code: {response.status_code}")

if response.status_code not in [200, 202]:
    print(response.text)
    raise Exception("Failed to send logs")

print("Logs sent successfully.")