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

if not payload:
    print("No drift detected. Nothing to send.")
    exit(0)

body = json.dumps(payload)
body_bytes = body.encode("utf-8")

rfc1123date = datetime.now(timezone.utc).strftime(
    "%a, %d %b %Y %H:%M:%S GMT"
)

content_length = len(body_bytes)

string_to_hash = (
    f"POST\n"
    f"{content_length}\n"
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
).decode("utf-8")

headers = {
    "Content-Type": "application/json",
    "Authorization": f"SharedKey {workspace_id}:{signature}",
    "Log-Type": "TerraformDrift",
    "x-ms-date": rfc1123date,
    "time-generated-field": "DetectedTime"
}

uri = (
    f"https://{workspace_id}.ods.opinsights.azure.com"
    "/api/logs?api-version=2016-04-01"
)

response = requests.post(
    uri,
    data=body_bytes,
    headers=headers,
    timeout=30
)

print(f"Status Code: {response.status_code}")

if response.status_code not in [200, 202]:
    print(response.text)
    raise Exception("Failed to send logs")

print(f"Successfully sent {len(payload)} drift records to Log Analytics")