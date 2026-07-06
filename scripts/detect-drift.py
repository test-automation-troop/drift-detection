import json

with open("reports/plan.json", "r") as f:
    plan = json.load(f)

def is_trivial_change(before, after):
    if before is None and after in ({}, []):
        return True

    if before == "" and after not in ("", None):
        return True

    return False


def compare_values(before, after, path=""):
    changes = []

    if isinstance(before, dict) and isinstance(after, dict):
        all_keys = set(before.keys()) | set(after.keys())

        for key in all_keys:
            new_path = f"{path}.{key}" if path else key
            changes.extend(compare_values(before.get(key), after.get(key), new_path))

    elif isinstance(before, list) and isinstance(after, list):
        if before != after:
            changes.append((path, before, after))

    else:
        if before != after and not is_trivial_change(before, after):
            changes.append((path, before, after))

    return changes


drifts = plan.get("resource_drift", [])

if not drifts:
    print("No drift detected.")
else:
    for drift in drifts:
        address = drift.get("address")
        before = drift.get("change", {}).get("before", {})
        after = drift.get("change", {}).get("after", {})

        changes = compare_values(before, after)

        if changes:
            print(f"\nDrift detected in resource: {address}")
            print("-" * 60)

            for field, old, new in changes:
                print(f"Changed field: {field}")
                print(f"Azure/current value    : {old}")
                print(f"Terraform desired value: {new}")
                print()