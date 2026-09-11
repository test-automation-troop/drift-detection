import os
import sys
import json
from datetime import datetime, timezone

if len(sys.argv) < 2:
    raise Exception("Usage: python create_payload.py <plan.json>")

plan_file = sys.argv[1]

with open(plan_file, "r", encoding="utf-8") as f:
    plan = json.load(f)

# Prefer resource_drift for refresh-only plans
resource_changes = plan.get("resource_drift", [])

# Fallback if resource_drift is unavailable
if not resource_changes:
    resource_changes = plan.get("resource_changes", [])

repository = os.getenv("GITHUB_REPOSITORY", "unknown")
github_server = os.getenv("GITHUB_SERVER_URL", "https://github.com")
default_environment = os.getenv("ENVIRONMENT", "unknown")

repo_link = (
    f"{github_server}/{repository}"
    if repository != "unknown"
    else "unknown"
)

payload = []

for resource in resource_changes:

    change = resource.get("change", {})

    before = change.get("before", {}) or {}
    after = change.get("after", {}) or {}

    resource_name = resource.get("address", "unknown")
    resource_type = resource.get("type", "unknown")

    tags = after.get("tags", {}) or after.get("tags_all", {}) or {}

    environment = (
        tags.get("Environment")
        or tags.get("environment")
        or default_environment
    )

    detected_time = datetime.now(timezone.utc).isoformat()

    # Compare all attributes
    all_attributes = set(before.keys()) | set(after.keys())

    for attribute in sorted(all_attributes):

        old_value = before.get(attribute)
        new_value = after.get(attribute)

        if old_value != new_value:

            payload.append({
                "DetectedTime": detected_time,
                "ResourceName": resource_name,
                "ResourceType": resource_type,
                "Attribute": attribute,
                "OldValue": json.dumps(old_value, default=str),
                "NewValue": json.dumps(new_value, default=str),
                "Environment": environment,
                "RepositoryLink": repo_link,
                "Drift": f"{attribute}: {old_value} -> {new_value}"
            })

output_file = os.path.join(
    os.getenv("GITHUB_WORKSPACE", "."),
    "reports",
    "drift_payload.json"
)

os.makedirs(os.path.dirname(output_file), exist_ok=True)

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(payload, f, indent=2)

print(f"Payload written to: {output_file}")