import json
import os
from dotenv import load_dotenv
from datetime import datetime, UTC
from azure.storage.blob import BlobServiceClient

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

# -------------------------------
# Upload report to Blob Storage
# -------------------------------

load_dotenv()
connection_string = os.getenv(
    "ACCESS_TOKEN_STORAGE_ACC"
)

if not connection_string:
    raise ValueError(
        "ACCESS_TOKEN_STORAGE_ACC environment variable not found"
    )

container_name = "drift-reports"

blob_service_client = BlobServiceClient.from_connection_string(
    connection_string
)

blob_name = (
    f"drift_report_"
    f"{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}.json"
)

blob_client = blob_service_client.get_blob_client(
    container=container_name,
    blob=blob_name
)

with open(report_file, "rb") as data:
    blob_client.upload_blob(
        data,
        overwrite=False
    )

print(
    f"Report uploaded successfully to "
    f"container '{container_name}' "
    f"as '{blob_name}'"
)