import os
import sys
import json
from datetime import datetime, timezone

if len(sys.argv) < 2:
    raise Exception("Usage: python create_payload.py <plan.json>")

plan_file = sys.argv[1]

with open(plan_file, "r", encoding="utf-8") as f:
    plan = json.load(f)

resource_changes = plan.get("resource_changes", [])

repository = os.getenv("GITHUB_REPOSITORY", "unknown")

payload = []

summary = {
    "create": 0,
    "update": 0,
    "delete": 0
}

for resource in resource_changes:

    actions = resource.get("change", {}).get("actions", [])

    if "create" in actions:
        summary["create"] += 1

    if "update" in actions:
        summary["update"] += 1

    if "delete" in actions:
        summary["delete"] += 1

    payload.append({
        "Repository": repository,
        "ResourceType": resource.get("type"),
        "ResourceName": resource.get("address"),
        "Action": ",".join(actions),
        "DetectedTime": datetime.now(timezone.utc).isoformat()
    })

output_file = os.path.join(
    os.getenv("GITHUB_WORKSPACE", "."),
    "reports",
    "drift_payload.json"
)

os.makedirs(os.path.dirname(output_file), exist_ok=True)

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(payload, f, indent=2)

print("----- DRIFT SUMMARY -----")
print(f"Create : {summary['create']}")
print(f"Update : {summary['update']}")
print(f"Delete : {summary['delete']}")
print(f"Records: {len(payload)}")

print(f"\nPayload written to: {output_file}")