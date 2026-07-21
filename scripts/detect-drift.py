import json
import os
import base64
import hashlib
import hmac
import requests

from dotenv import load_dotenv
from email.utils import formatdate

# Load Terraform plan
with open("reports/plan.json", "r") as f:
    plan = json.load(f)


def is_trivial_change(before, after):
    return (
        (before is None and after in ({}, []))
        or (before == "" and after not in ("", None))
    )


def find_changes(before, after, path=""):
    changes = []

    if isinstance(before, dict) and isinstance(after, dict):
        for key in set(before) | set(after):
            new_path = f"{path}.{key}" if path else key
            changes.extend(
                find_changes(
                    before.get(key),
                    after.get(key),
                    new_path
                )
            )

    elif before != after and not is_trivial_change(before, after):
        changes.append({
            "field": path,
            "from": before,
            "to": after
        })

    return changes


def build_signature(
    workspace_id,
    shared_key,
    date,
    content_length,
    method,
    content_type,
    resource,
):
    x_headers = f"x-ms-date:{date}"

    string_to_hash = (
        f"{method}\n"
        f"{content_length}\n"
        f"{content_type}\n"
        f"{x_headers}\n"
        f"{resource}"
    )

    bytes_to_hash = string_to_hash.encode("utf-8")
    decoded_key = base64.b64decode(shared_key)

    encoded_hash = base64.b64encode(
        hmac.new(
            decoded_key,
            bytes_to_hash,
            digestmod=hashlib.sha256,
        ).digest()
    ).decode("utf-8")

    return f"SharedKey {workspace_id}:{encoded_hash}"


def send_to_log_analytics(data):
    workspace_id = os.getenv("LOG_ANALYTICS_WORKSPACE_ID")
    shared_key = os.getenv("LOG_ANALYTICS_SHARED_KEY")

    if not workspace_id:
        raise ValueError(
            "LOG_ANALYTICS_WORKSPACE_ID environment variable not found"
        )

    if not shared_key:
        raise ValueError(
            "LOG_ANALYTICS_SHARED_KEY environment variable not found"
        )

    log_type = "TerraformDrift"

    body = json.dumps(data)

    method = "POST"
    content_type = "application/json"
    resource = "/api/logs"

    rfc1123date = formatdate(usegmt=True)

    signature = build_signature(
        workspace_id,
        shared_key,
        rfc1123date,
        len(body),
        method,
        content_type,
        resource,
    )

    uri = (
        f"https://{workspace_id}.ods.opinsights.azure.com"
        f"{resource}?api-version=2016-04-01"
    )

    headers = {
        "Content-Type": content_type,
        "Authorization": signature,
        "Log-Type": log_type,
        "x-ms-date": rfc1123date,
    }

    print("Payload:")
    print(json.dumps(data, indent=2))

    print("Records to send:", len(data))

    response = requests.post(
        uri,
        data=body,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    print(
        f"Successfully sent drift report to Log Analytics. "
        f"Status Code: {response.status_code}"
    )


# Detect drift
report = []

for drift in plan.get("resource_drift", []):
    changes = find_changes(
        drift.get("change", {}).get("before", {}),
        drift.get("change", {}).get("after", {})
    )

    if changes:
        report.append({
            "resource": drift.get("address"),
            "changes": changes
        })

# Exit if no drift found
if not report:
    print("No drift detected. No report generated.")
    exit(0)

# Generate report
report_file = "reports/drift_report.json"

with open(report_file, "w") as f:
    json.dump(report, f, indent=4)

print(f"Drift detected. Report generated: {report_file}")

# Load environment variables
load_dotenv()

# Send to Log Analytics
send_to_log_analytics(report)